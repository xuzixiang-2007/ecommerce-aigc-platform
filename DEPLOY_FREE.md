# 免费部署指南（Vercel + PythonAnywhere）

## 架构
- 前端 → Vercel（免费，无需信用卡）
- 后端 → PythonAnywhere（免费，无需信用卡）
- 数据库 → SQLite（PythonAnywhere 自带，零配置）

---

## 第一部分：部署后端到 PythonAnywhere

### 1. 注册账号
1. 打开 https://www.pythonanywhere.com/registration/register/beginner/
2. 注册免费账号（Beginner 计划）
3. 登录后进入 Dashboard

### 2. 上传代码
1. 点击 "Files" 标签
2. 在 home 目录下创建文件夹 `ecommerce-aigc-platform`
3. 在该文件夹下创建子文件夹 `backend`
4. 通过 GitHub 或文件上传，将 backend 目录下所有文件上传到 `/home/你的用户名/ecommerce-aigc-platform/backend/`

或者用 Bash 控制台克隆：
1. 点击 "Consoles" → "Bash"
2. 执行：
```bash
cd ~
git clone https://github.com/xuzixiang-2007/ecommerce-aigc-platform.git
cd ecommerce-aigc-platform/backend
pip install --user -r requirements.txt
```

### 3. 创建 Web 应用
1. 点击 "Web" 标签
2. 点击 "Add a new web app"
3. 选择 "Manual configuration" → "Python 3.10"
4. 设置 Working directory: `/home/你的用户名/ecommerce-aigc-platform/backend/`
5. 在 WSGI 配置文件中，替换内容为：
```python
import sys
import os

path = "/home/你的用户名/ecommerce-aigc-platform/backend"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["AIGC_PROVIDER"] = "mock"
os.environ["BLOCKCHAIN_PROVIDER"] = "mock"
os.environ["JWT_SECRET"] = "aigc-platform-secret-2024"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:////home/你的用户名/ecommerce-aigc-platform/backend/aigc_platform.db"

from a2wsgi import ASGIMiddleware
from app.main import app
application = ASGIMiddleware(app)
```
6. 把 `你的用户名` 替换成你的 PythonAnywhere 用户名
7. 点击 Reload 重启服务

### 4. 获取后端公网 URL
- 部署后，你的后端地址为：`https://你的用户名.pythonanywhere.com/`
- 访问 `https://你的用户名.pythonanywhere.com/health` 确认返回 `{"status": "ok"}`

---

## 第二部分：部署前端到 Vercel

### 1. 注册 Vercel
1. 打开 https://vercel.com
2. 用 GitHub 账号登录（不需要信用卡）

### 2. 导入项目
1. 点击 "Add New" → "Project"
2. 选择 `ecommerce-aigc-platform` 仓库
3. 设置：
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Output Directory: `dist`

### 3. 设置环境变量（关键！）
在 "Environment Variables" 中添加：
- Name: `VITE_API_BASE`
- Value: `https://你的用户名.pythonanywhere.com`（你的 PythonAnywhere 后端地址）
- 不带末尾斜杠

### 4. 部署
1. 点击 "Deploy"
2. 等待 1-2 分钟构建完成
3. 获取前端公网 URL：`https://ecommerce-aigc-frontend-xxxx.vercel.app`

---

## 验证
1. 打开 Vercel 前端链接，能看到平台界面
2. 尝试注册/登录商家
3. 尝试生成商品图
4. 尝试存证验证
5. 查看数据可视化大屏

## 注意事项
- PythonAnywhere 免费版每天限制 100 CPU 秒，评审期间足够用
- PythonAnywhere 免费版有冷启动延迟（约 30 秒），首次访问可能慢
- 数据存储在 SQLite 文件中，重启不会丢失
