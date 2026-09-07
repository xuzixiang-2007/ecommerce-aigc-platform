"""腾讯云 SCF 入口文件

CloudBase HTTP 云函数要求：
1. 应用监听 9000 端口
2. 通过 scf_bootstrap 启动
3. 依赖打包在 third_party 目录

启动命令（scf_bootstrap）:
  /var/lang/python310/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000
"""
# 直接复用 main.py 的 app
from app.main import app
