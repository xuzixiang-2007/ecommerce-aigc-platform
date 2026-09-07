# Render 部署指南

## 部署架构

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  前端静态站点  │ ──→ │  后端 API 服务  │ ──→ │  PostgreSQL   │
│  (Vite构建)   │     │  (FastAPI)    │     │  数据库        │
│  Render免费版  │     │  Render免费版   │     │  Render免费版   │
└─────────────┘     └──────────────┘     └──────────────┘
```

## 第一步：推送代码到 GitHub

### 1.1 创建 GitHub 仓库

1. 打开 https://github.com/new
2. Repository name: `ecommerce-aigc-platform`
3. 选择 **Public**（公开）
4. **不要**勾选 "Add a README file"
5. 点击 **Create repository**

### 1.2 推送代码

在项目目录下执行：

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-aigc-platform.git

# 推送代码
git branch -M main
git push -u origin main
```

## 第二步：在 Render 上部署

### 2.1 创建 Blueprint 部署

1. 打开 https://render.com 并登录（可用 GitHub 账号登录）
2. 点击右上角 **New +** → **Blueprint**
3. 选择刚创建的 GitHub 仓库 `ecommerce-aigc-platform`
4. Render 会自动检测到 `render.yaml` 文件
5. 确认服务配置：
   - `aigc-db`：PostgreSQL 数据库（免费版）
   - `aigc-platform-backend`：Python Web 服务（免费版）
   - `aigc-platform-frontend`：静态站点（免费版）
6. 点击 **Apply** 开始部署

### 2.2 等待部署完成

- 数据库创建：约 1 分钟
- 后端部署：约 3-5 分钟（安装依赖 + 启动服务）
- 前端部署：约 2-3 分钟（npm install + build）
- 总计约 5-10 分钟

### 2.3 获取公网链接

部署完成后，在 Render Dashboard 可以看到三个服务的公网 URL：

- **前端访问地址**：`https://aigc-platform-frontend.onrender.com`
- **后端 API 地址**：`https://aigc-platform-backend.onrender.com`
- **API 文档（Swagger）**：`https://aigc-platform-backend.onrender.com/docs`

> 实际域名会包含随机字符串，以 Render Dashboard 显示的为准。

## 第三步：验证部署

1. 打开前端公网链接，能看到平台首页
2. 点击"登录"，注册一个商家账号
3. 在商家门户创建任务并生成商品图
4. 在管理后台查看数据可视化大屏
5. 在 AIGC 识别页面上传图片进行检测

## 常见问题

### Q: 后端启动失败？
检查 Render 日志（Dashboard → 服务 → Logs），常见原因：
- 数据库连接失败：确认 DATABASE_URL 环境变量已设置
- 依赖缺失：确认 requirements.txt 包含所有依赖

### Q: 前端 API 请求报错？
- 确认 VITE_API_BASE 环境变量已正确设置（应指向后端 URL）
- 后端已配置 CORS 允许所有来源

### Q: 免费版限制？
- Web 服务 15 分钟无请求会自动休眠，首次访问需等待冷启动
- PostgreSQL 免费版 90 天后过期
- 带宽和构建时间有月度限额

### Q: 如何更新代码？
```bash
git add -A
git commit -m "更新说明"
git push
```
推送后 Render 会自动重新部署。
