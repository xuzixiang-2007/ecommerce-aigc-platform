"""配置管理 - 读取 .env 环境变量"""
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # 应用信息
    APP_NAME: str = "电商AIGC商品图合规溯源存证平台"

    # 数据库
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres123@localhost:5432/aigc_platform"

    # MinIO 对象存储
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "product-images"
    MINIO_SECURE: bool = False

    # AIGC 生成服务（mock = 模拟，wanx = 通义万相，stability = Stability AI）
    AIGC_PROVIDER: str = "mock"
    DASHSCOPE_API_KEY: str = ""
    STABILITY_API_KEY: str = ""
    COMFYUI_URL: str = "http://localhost:8188"

    # 区块链服务（mock = 模拟，fisco = FISCO BCOS）
    BLOCKCHAIN_PROVIDER: str = "mock"
    FISCO_RPC_URL: str = "http://localhost:8545"

    # JWT 密钥
    JWT_SECRET: str = "aigc-platform-secret-2024"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def convert_database_url(cls, v):
        """将 Render 提供的 postgres:// 转为 SQLAlchemy asyncpg 格式"""
        if isinstance(v, str):
            if v.startswith('postgres://'):
                return v.replace('postgres://', 'postgresql+asyncpg://', 1)
            if v.startswith('postgresql://') and not v.startswith('postgresql+'):
                return v.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return v


# 全局配置实例
settings = Settings()
