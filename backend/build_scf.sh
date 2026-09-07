#!/bin/bash
# 腾讯云 SCF 部署打包脚本
# 在本地执行，生成可上传的 zip 包

set -e

echo "=== 开始打包后端代码 ==="

# 创建临时打包目录
PACK_DIR="/data/user/work/scf_package"
rm -rf "$PACK_DIR"
mkdir -p "$PACK_DIR"

# 复制后端代码
cp -r /workspace/ecommerce-aigc-platform/backend/* "$PACK_DIR/"

# 删除不需要的文件
rm -f "$PACK_DIR/build_scf.sh"
rm -rf "$PACK_DIR/__pycache__"
rm -rf "$PACK_DIR/app/__pycache__"
rm -rf "$PACK_DIR/app/services/__pycache__"
rm -f "$PACK_DIR/Procfile"
rm -f "$PACK_DIR/wsgi.py"

# 安装依赖到 third_party 目录
echo "=== 安装 Python 依赖到 third_party ==="
cd "$PACK_DIR"
pip install -r requirements.txt -t third_party --quiet

# 设置 scf_bootstrap 可执行权限
chmod +x scf_bootstrap

# 打包
echo "=== 打包 zip ==="
cd /data/user/work
rm -f scf_backend.zip
cd scf_package && zip -r /data/user/work/scf_backend.zip . -q

echo "=== 打包完成 ==="
echo "文件位置: /data/user/work/scf_backend.zip"
echo "文件大小: $(du -h /data/user/work/scf_backend.zip | cut -f1)"
ls -lh /data/user/work/scf_backend.zip
