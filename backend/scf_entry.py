"""腾讯云 SCF 入口文件

执行方法填: scf_entry.handler

腾讯云 SCF Web 函数要求:
1. 监听 9000 端口
2. 通过 scf_bootstrap 启动
3. 执行方法只允许字母、数字、下划线、连字符
"""
import sys
import os
import asyncio

# 确保项目根目录在 Python 路径中
_path = os.path.dirname(os.path.abspath(__file__))
if _path not in sys.path:
    sys.path.insert(0, _path)

# 确保依赖目录在路径中
_third_party = os.path.join(_path, "third_party")
if os.path.exists(_third_party) and _third_party not in sys.path:
    sys.path.insert(0, _third_party)

# 设置环境变量
os.environ.setdefault("AIGC_PROVIDER", "mock")
os.environ.setdefault("BLOCKCHAIN_PROVIDER", "mock")
os.environ.setdefault("JWT_SECRET", "aigc-platform-secret-2024")

from app.main import app

# SCF Web 函数入口: 返回 ASGI app
def handler(event, context):
    """SCF Web 函数处理器"""
    return app
