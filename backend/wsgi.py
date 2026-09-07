"""PythonAnywhere WSGI 配置文件

在 PythonAnywhere 的 Web 页面，将 WSGI 配置文件路径指向此文件。
这个文件将 FastAPI (ASGI) 转换为 WSGI 供 PythonAnywhere 使用。
"""
import sys
import os

# 添加项目根目录到 Python 路径
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# 设置环境变量
os.environ.setdefault("AIGC_PROVIDER", "mock")
os.environ.setdefault("BLOCKCHAIN_PROVIDER", "mock")
os.environ.setdefault("JWT_SECRET", "aigc-platform-secret-2024")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:////home/{your_username}/ecommerce-aigc-platform/backend/aigc_platform.db")

from a2wsgi import ASGIMiddleware
from app.main import app

# PythonAnywhere 使用 application 变量
application = ASGIMiddleware(app)
