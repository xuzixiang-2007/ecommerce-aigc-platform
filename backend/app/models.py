"""数据模型 - 对应数据库表结构"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Merchant(Base):
    """商家信息表"""
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="商家名称")
    phone = Column(String(20), unique=True, index=True, comment="联系电话")
    email = Column(String(100), comment="邮箱")
    password_hash = Column(String(200), comment="密码哈希")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tasks = relationship("ProductTask", back_populates="merchant")


class ProductTask(Base):
    """商品图生成任务表"""
    __tablename__ = "product_tasks"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    product_name = Column(String(200), nullable=False, comment="商品名称")
    product_category = Column(String(100), comment="商品类目")
    prompt = Column(Text, comment="生成提示词")
    status = Column(String(20), default="pending", comment="状态: pending/generating/checking/passed/failed/certified")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    merchant = relationship("Merchant", back_populates="tasks")
    images = relationship("GeneratedImage", back_populates="task")
    certificate = relationship("BlockchainCertificate", back_populates="task", uselist=False)
    compliance_reports = relationship("ComplianceReport", back_populates="task")


class GeneratedImage(Base):
    """生成图片记录表"""
    __tablename__ = "generated_images"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("product_tasks.id"), nullable=False)
    image_path = Column(String(500), comment="MinIO 存储路径")
    image_url = Column(String(500), comment="可访问 URL")
    image_hash = Column(String(64), comment="SHA-256 哈希")
    phash = Column(String(32), comment="感知哈希 pHash")
    model_version = Column(String(50), comment="模型版本")
    generation_params = Column(Text, comment="生成参数 JSON")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("ProductTask", back_populates="images")


class ComplianceReport(Base):
    """合规检测报告表"""
    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("product_tasks.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("generated_images.id"), nullable=False)
    content_safety = Column(String(20), default="pass", comment="内容安全: pass/fail")
    copyright_check = Column(String(20), default="pass", comment="版权检测: pass/fail")
    spec_check = Column(String(20), default="pass", comment="规范检查: pass/fail")
    score = Column(Float, default=100.0, comment="合规得分")
    details = Column(Text, comment="检测详情 JSON")
    passed = Column(Boolean, default=True, comment="是否通过")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("ProductTask", back_populates="compliance_reports")


class BlockchainCertificate(Base):
    """区块链存证证书表"""
    __tablename__ = "blockchain_certificates"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("product_tasks.id"), nullable=False)
    image_hash = Column(String(64), nullable=False, comment="图片 SHA-256 哈希")
    phash = Column(String(32), comment="感知哈希")
    tx_hash = Column(String(128), comment="区块链交易哈希")
    block_number = Column(Integer, comment="区块高度")
    certificate_no = Column(String(64), comment="证书编号")
    timestamp = Column(DateTime(timezone=True), comment="存证时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("ProductTask", back_populates="certificate")


class DetectionRecord(Base):
    """AIGC 识别记录表"""
    __tablename__ = "detection_records"

    id = Column(Integer, primary_key=True, index=True)
    image_hash = Column(String(64), nullable=False, index=True, comment="图片 SHA-256 哈希")
    is_aigc = Column(Boolean, comment="是否为AI生成")
    confidence = Column(Float, comment="置信度")
    label = Column(String(50), comment="标签: AI生成/人工拍摄")
    details = Column(Text, comment="详细分析 JSON")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
