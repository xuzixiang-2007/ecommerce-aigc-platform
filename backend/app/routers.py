"""API 路由 - 处理前端请求"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import json
import io
import hashlib
import os
import base64
import time

from app.database import get_db
from app.models import Merchant, ProductTask, GeneratedImage, ComplianceReport, BlockchainCertificate, DetectionRecord
from app.schemas import (
    CreateTaskRequest, TaskResponse, ImageResponse,
    ComplianceResponse, CertificateResponse,
    VerifyRequest, VerifyResponse,
    DetectionResponse, DetectionRecordResponse,
    RegisterRequest, LoginRequest, AuthResponse,
)
from app.services.aigc_service import generate_product_image
from app.services.compliance_service import check_compliance
from app.services.traceability_service import generate_certificate_no, compute_image_hash, compute_phash
from app.services.blockchain_service import store_evidence, verify_evidence
from app.services.detection_service import detect_aigc_image
from app.config import settings

router = APIRouter()


# ========== 工具函数 ==========

def hash_password(password: str) -> str:
    """PBKDF2 密码哈希"""
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + ':' + hash_bytes.hex()


def verify_password(password: str, stored_hash: str) -> bool:
    """验证密码"""
    try:
        salt_hex, hash_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return hash_bytes.hex() == hash_hex
    except Exception:
        return False


def create_token(merchant_id: int, name: str, phone: str) -> str:
    """创建简单 token（base64 编码）"""
    payload = json.dumps({
        "merchant_id": merchant_id,
        "name": name,
        "phone": phone,
        "exp": int(time.time()) + 86400 * 7,
    })
    return base64.b64encode(payload.encode()).decode()

# MinIO 客户端（延迟初始化）
_minio_client = None


def get_minio():
    global _minio_client
    if _minio_client is None:
        from minio import Minio
        _minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        # 自动创建 bucket
        if not _minio_client.bucket_exists(settings.MINIO_BUCKET):
            _minio_client.make_bucket(settings.MINIO_BUCKET)
    return _minio_client


# ========== 商家相关 ==========

@router.get("/api/merchants", response_model=list[TaskResponse])
async def list_merchants(db: AsyncSession = Depends(get_db)):
    """获取商家列表"""
    result = await db.execute(select(Merchant))
    merchants = result.scalars().all()
    return merchants


# ========== 认证相关 ==========

@router.post("/api/auth/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """商家注册"""
    result = await db.execute(select(Merchant).where(Merchant.phone == req.phone))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该手机号已注册")

    merchant = Merchant(
        name=req.name,
        phone=req.phone,
        email=req.email,
        password_hash=hash_password(req.password),
    )
    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)

    token = create_token(merchant.id, merchant.name, merchant.phone)
    return {
        "token": token,
        "merchant_id": merchant.id,
        "name": merchant.name,
        "phone": merchant.phone,
    }


@router.post("/api/auth/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """商家登录"""
    result = await db.execute(select(Merchant).where(Merchant.phone == req.phone))
    merchant = result.scalar_one_or_none()

    if not merchant or not merchant.password_hash:
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    if not verify_password(req.password, merchant.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")

    token = create_token(merchant.id, merchant.name, merchant.phone)
    return {
        "token": token,
        "merchant_id": merchant.id,
        "name": merchant.name,
        "phone": merchant.phone,
    }


# ========== 任务相关 ==========

@router.post("/api/tasks", response_model=TaskResponse)
async def create_task(req: CreateTaskRequest, db: AsyncSession = Depends(get_db)):
    """创建商品图生成任务"""
    task = ProductTask(
        merchant_id=req.merchant_id,
        product_name=req.product_name,
        product_category=req.product_category,
        prompt=req.prompt,
        status="pending",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/api/tasks", response_model=list[TaskResponse])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    """获取任务列表"""
    result = await db.execute(select(ProductTask).order_by(ProductTask.created_at.desc()))
    return result.scalars().all()


@router.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """获取任务详情"""
    result = await db.execute(select(ProductTask).where(ProductTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


# ========== 生成图片 ==========

@router.post("/api/tasks/{task_id}/generate")
async def generate_image(task_id: int, db: AsyncSession = Depends(get_db)):
    """执行 AIGC 生成 + 合规检测 + 存证（一站式流程）"""
    # 1. 查询任务
    result = await db.execute(select(ProductTask).where(ProductTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 2. 更新状态为生成中
    task.status = "generating"
    await db.commit()

    # 3. AIGC 生成图片
    gen_result = await generate_product_image(
        task.product_name, task.product_category, task.prompt
    )

    # 4. 上传到 MinIO（失败时用 base64 data URL 兜底）
    import io as _io
    import base64 as _b64
    object_name = f"products/{task_id}/{gen_result['image_hash'][:16]}.png"
    try:
        minio = get_minio()
        minio.put_object(
            settings.MINIO_BUCKET,
            object_name,
            _io.BytesIO(gen_result["image_bytes"]),
            len(gen_result["image_bytes"]),
            content_type="image/png",
        )
        image_url = f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{object_name}"
    except Exception as e:
        # MinIO 不可用时，用 base64 data URL 返回图片
        b64_str = _b64.b64encode(gen_result["image_bytes"]).decode()
        image_url = f"data:image/png;base64,{b64_str}"
        print(f"MinIO 不可用，使用 base64 返回图片: {e}")

    # 5. 保存图片记录
    image = GeneratedImage(
        task_id=task_id,
        image_path=object_name,
        image_url=image_url,
        image_hash=gen_result["image_hash"],
        phash=gen_result["phash"],
        model_version=gen_result["model_version"],
        generation_params=gen_result["params"],
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)

    # 6. 合规检测
    task.status = "checking"
    await db.commit()

    compliance_result = await check_compliance(
        gen_result["image_bytes"], task.product_name, task.product_category
    )

    report = ComplianceReport(
        task_id=task_id,
        image_id=image.id,
        content_safety=compliance_result["content_safety"],
        copyright_check=compliance_result["copyright_check"],
        spec_check=compliance_result["spec_check"],
        score=compliance_result["score"],
        passed=compliance_result["passed"],
        details=compliance_result["details"],
    )
    db.add(report)

    if not compliance_result["passed"]:
        # 不通过
        task.status = "failed"
        await db.commit()
        return {
            "task_id": task_id,
            "status": "failed",
            "message": "合规检测未通过",
            "compliance": compliance_result,
        }

    # 7. 溯源存证
    task.status = "passed"
    await db.commit()

    chain_result = await store_evidence(
        gen_result["image_hash"], gen_result["phash"],
        task.product_name, task_id
    )

    cert_no = generate_certificate_no()
    certificate = BlockchainCertificate(
        task_id=task_id,
        image_hash=gen_result["image_hash"],
        phash=gen_result["phash"],
        tx_hash=chain_result["tx_hash"],
        block_number=chain_result["block_number"],
        certificate_no=cert_no,
        timestamp=chain_result["timestamp"],
    )
    db.add(certificate)

    task.status = "certified"
    await db.commit()
    await db.refresh(certificate)

    return {
        "task_id": task_id,
        "status": "certified",
        "message": "生成、合规检测、存证全部完成",
        "image": {
            "id": image.id,
            "image_url": image_url,
            "image_hash": gen_result["image_hash"],
            "phash": gen_result["phash"],
        },
        "compliance": compliance_result,
        "certificate": {
            "id": certificate.id,
            "certificate_no": cert_no,
            "tx_hash": chain_result["tx_hash"],
            "block_number": chain_result["block_number"],
        },
    }


# ========== 存证验证 ==========

@router.post("/api/verify", response_model=VerifyResponse)
async def verify_certificate(req: VerifyRequest, db: AsyncSession = Depends(get_db)):
    """验证图片存证"""
    result = await db.execute(
        select(BlockchainCertificate).where(
            BlockchainCertificate.image_hash == req.image_hash
        )
    )
    cert = result.scalar_one_or_none()

    if not cert:
        return VerifyResponse(
            verified=False,
            certificate=None,
            message="未找到对应的存证记录",
        )

    # 验证链上数据
    is_valid = await verify_evidence(cert.image_hash, cert.tx_hash)

    return VerifyResponse(
        verified=is_valid,
        certificate=cert,
        message="存证验证通过" if is_valid else "链上数据不一致",
    )


@router.get("/api/certificates", response_model=list[CertificateResponse])
async def list_certificates(db: AsyncSession = Depends(get_db)):
    """获取所有存证证书"""
    result = await db.execute(
        select(BlockchainCertificate).order_by(BlockchainCertificate.created_at.desc())
    )
    return result.scalars().all()


# ========== 数据统计 ==========

@router.get("/api/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """获取数据可视化统计"""
    # 1. 总览数据
    total_tasks = await db.scalar(select(func.count(ProductTask.id)))
    total_certified = await db.scalar(
        select(func.count(ProductTask.id)).where(ProductTask.status == "certified")
    )
    total_failed = await db.scalar(
        select(func.count(ProductTask.id)).where(ProductTask.status == "failed")
    )
    total_pending = await db.scalar(
        select(func.count(ProductTask.id)).where(
            ProductTask.status.in_(["pending", "generating", "checking"])
        )
    )
    total_merchants = await db.scalar(select(func.count(Merchant.id)))
    total_certificates = await db.scalar(select(func.count(BlockchainCertificate.id)))
    total_images = await db.scalar(select(func.count(GeneratedImage.id)))

    # 2. 合规检测统计
    total_compliance = await db.scalar(select(func.count(ComplianceReport.id)))
    passed_compliance = await db.scalar(
        select(func.count(ComplianceReport.id)).where(ComplianceReport.passed == True)
    )
    avg_score = await db.scalar(select(func.avg(ComplianceReport.score))) or 0

    # 3. 任务状态分布（饼图）
    status_result = await db.execute(
        select(ProductTask.status, func.count(ProductTask.id))
        .group_by(ProductTask.status)
    )
    status_dist = [
        {"name": _status_label(s), "value": cnt}
        for s, cnt in status_result.all()
    ]

    # 4. 商品类目分布（柱状图）
    category_result = await db.execute(
        select(ProductTask.product_category, func.count(ProductTask.id))
        .group_by(ProductTask.product_category)
        .order_by(func.count(ProductTask.id).desc())
    )
    category_dist = [
        {"name": cat or "未分类", "value": cnt}
        for cat, cnt in category_result.all()
    ]

    # 5. 最近7天任务趋势（折线图）
    seven_days_ago = datetime.now() - timedelta(days=7)
    daily_result = await db.execute(
        select(
            cast(ProductTask.created_at, Date).label("date"),
            func.count(ProductTask.id).label("count"),
        )
        .where(ProductTask.created_at >= seven_days_ago)
        .group_by(cast(ProductTask.created_at, Date))
        .order_by(cast(ProductTask.created_at, Date))
    )
    daily_trend = [
        {"date": d.strftime("%m-%d"), "count": cnt}
        for d, cnt in daily_result.all()
    ]

    # 6. 最近7天存证趋势（折线图）
    daily_cert_result = await db.execute(
        select(
            cast(BlockchainCertificate.created_at, Date).label("date"),
            func.count(BlockchainCertificate.id).label("count"),
        )
        .where(BlockchainCertificate.created_at >= seven_days_ago)
        .group_by(cast(BlockchainCertificate.created_at, Date))
        .order_by(cast(BlockchainCertificate.created_at, Date))
    )
    daily_cert_trend = [
        {"date": d.strftime("%m-%d"), "count": cnt}
        for d, cnt in daily_cert_result.all()
    ]

    return {
        "overview": {
            "total_tasks": total_tasks or 0,
            "total_certified": total_certified or 0,
            "total_failed": total_failed or 0,
            "total_pending": total_pending or 0,
            "total_merchants": total_merchants or 0,
            "total_certificates": total_certificates or 0,
            "total_images": total_images or 0,
        },
        "compliance": {
            "total": total_compliance or 0,
            "passed": passed_compliance or 0,
            "failed": (total_compliance or 0) - (passed_compliance or 0),
            "pass_rate": round((passed_compliance or 0) / (total_compliance or 1) * 100, 1),
            "avg_score": round(float(avg_score), 1),
        },
        "status_dist": status_dist,
        "category_dist": category_dist,
        "daily_trend": daily_trend,
        "daily_cert_trend": daily_cert_trend,
    }


def _status_label(status: str) -> str:
    """状态英文转中文"""
    labels = {
        "pending": "待处理",
        "generating": "生成中",
        "checking": "检测中",
        "passed": "检测通过",
        "failed": "未通过",
        "certified": "已存证",
    }
    return labels.get(status, status)


# ========== AIGC 图片识别 ==========

@router.post("/api/detect", response_model=DetectionResponse)
async def detect_image(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """上传图片进行 AIGC 识别"""
    # 读取上传的图片
    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB 限制
        raise HTTPException(status_code=400, detail="图片大小不能超过10MB")

    # 执行检测
    result = await detect_aigc_image(image_bytes)

    # 保存记录到数据库
    record = DetectionRecord(
        image_hash=result["image_hash"],
        is_aigc=result["is_aigc"],
        confidence=result["confidence"],
        label=result["label"],
        details=json.dumps(result, ensure_ascii=False),
    )
    db.add(record)
    await db.commit()

    return result


@router.get("/api/detect/records", response_model=list[DetectionRecordResponse])
async def list_detection_records(db: AsyncSession = Depends(get_db)):
    """获取 AIGC 识别记录列表"""
    result = await db.execute(
        select(DetectionRecord).order_by(DetectionRecord.created_at.desc())
    )
    return result.scalars().all()
