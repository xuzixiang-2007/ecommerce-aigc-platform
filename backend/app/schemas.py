"""API 数据模型（Pydantic） - 定义请求和响应格式"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ========== 请求模型 ==========

class CreateTaskRequest(BaseModel):
    """创建生成任务"""
    merchant_id: int
    product_name: str
    product_category: str = "通用"
    prompt: Optional[str] = None  # 为空时自动生成


class VerifyRequest(BaseModel):
    """存证验证请求"""
    image_hash: str  # 图片的 SHA-256 哈希


# ========== 响应模型 ==========

class TaskResponse(BaseModel):
    """任务信息"""
    id: int
    merchant_id: int
    product_name: str
    product_category: str
    prompt: Optional[str]
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImageResponse(BaseModel):
    """图片信息"""
    id: int
    image_url: Optional[str]
    image_hash: Optional[str]
    phash: Optional[str]
    model_version: Optional[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComplianceResponse(BaseModel):
    """合规检测报告"""
    id: int
    task_id: int
    content_safety: str
    copyright_check: str
    spec_check: str
    score: float
    passed: bool
    details: Optional[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CertificateResponse(BaseModel):
    """存证证书"""
    id: int
    task_id: int
    image_hash: str
    phash: Optional[str]
    tx_hash: Optional[str]
    block_number: Optional[int]
    certificate_no: Optional[str]
    timestamp: Optional[datetime]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VerifyResponse(BaseModel):
    """存证验证结果"""
    verified: bool
    certificate: Optional[CertificateResponse] = None
    message: str


# ========== AIGC 识别相关 ==========

class DetectionIndicator(BaseModel):
    """检测指标"""
    name: str
    score: float
    desc: str


class DetectionResponse(BaseModel):
    """AIGC 识别结果"""
    is_aigc: bool
    confidence: float
    label: str
    indicators: list[DetectionIndicator]
    image_hash: str
    image_size: str
    details: str
    detected_at: str


class DetectionRecordResponse(BaseModel):
    """识别记录"""
    id: int
    image_hash: str
    is_aigc: bool
    confidence: float
    label: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 认证相关 ==========

class RegisterRequest(BaseModel):
    """商家注册请求"""
    name: str
    phone: str
    password: str
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """商家登录请求"""
    phone: str
    password: str


class AuthResponse(BaseModel):
    """认证响应"""
    token: str
    merchant_id: int
    name: str
    phone: str
