"""溯源存证服务 - 生成指纹、哈希、时间戳"""
import hashlib
import time
import uuid
from datetime import datetime, timezone


def generate_certificate_no() -> str:
    """生成证书编号（格式：AGC-年月日-随机6位）"""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_str = uuid.uuid4().hex[:6].upper()
    return f"AGC-{date_str}-{random_str}"


def compute_image_hash(image_bytes: bytes) -> str:
    """计算图片 SHA-256 哈希"""
    return hashlib.sha256(image_bytes).hexdigest()


def compute_phash(image_bytes: bytes) -> str:
    """计算感知哈希 pHash（用于图片相似度比对）"""
    from PIL import Image
    import io
    from app.utils.phash import phash as compute_phash_internal

    img = Image.open(io.BytesIO(image_bytes))
    return compute_phash_internal(img)


def build_evidence_data(image_hash: str, phash: str, product_name: str, task_id: int) -> dict:
    """构建上链存证数据"""
    return {
        "image_hash": image_hash,
        "phash": phash,
        "product_name": product_name,
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
