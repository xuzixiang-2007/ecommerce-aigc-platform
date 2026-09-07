# 电商AIGC商品图合规溯源存证平台

> 人工智能精英算法大赛 - AI+创新创业赛道参赛项目

## 项目简介

本平台将 AIGC 商品图生成、合规检测、区块链溯源存证三大能力整合为一体化服务，为电商商家提供"生成即合规、合规即存证"的完整闭环。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS |
| 后端 | Python FastAPI + SQLAlchemy + asyncpg |
| 数据库 | PostgreSQL 15 |
| 对象存储 | MinIO |
| AI 生成 | Stable Diffusion（mock 模式可先跑通流程）|
| 区块链 | FISCO BCOS（mock 模式可先跑通流程）|

## 快速开始

### 第一步：启动基础设施

```bash
cd ecommerce-aigc-platform
podman compose up -d
# 或 docker compose up -d
```

验证：打开 http://localhost:9001 查看 MinIO 控制台（用户名 minioadmin / 密码 minioadmin123）

### 第二步：启动后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
copy .env.example .env    # Windows
# cp .env.example .env      # Mac/Linux
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

验证：打开 http://localhost:8000/docs 查看 Swagger API 文档

### 第三步：启动前端

```bash
cd frontend
npm install
npm run dev
```

验证：打开 http://localhost:3000 查看平台界面

## 使用流程

1. 在「商家门户」页面输入商品名称和类目
2. 点击「一键生成 + 合规检测 + 存证」
3. 系统自动完成 AIGC 生成 → 合规检测 → 区块链存证
4. 在「管理后台」查看所有存证证书
5. 在「存证验证」页面输入图片哈希验证溯源信息

## 项目结构

```
ecommerce-aigc-platform/
├── docker-compose.yml          # 基础设施（PostgreSQL + MinIO + Redis）
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库连接
│   │   ├── models.py           # 数据模型
│   │   ├── schemas.py          # API 数据模型
│   │   ├── routers.py          # API 路由
│   │   └── services/
│   │       ├── aigc_service.py        # AIGC 生成
│   │       ├── compliance_service.py  # 合规检测
│   │       ├── traceability_service.py # 溯源
│   │       └── blockchain_service.py   # 区块链存证
│   ├── requirements.txt
│   ├── .env.example
│   └── init.sql                # 数据库初始化
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # 主应用 + 路由
│   │   ├── api/client.ts       # API 客户端
│   │   └── pages/
│   │       ├── PortalPage.tsx   # 商家门户
│   │       ├── AdminPage.tsx    # 管理后台
│   │       └── VerifyPage.tsx    # 存证验证
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 后续升级指南

### 接入真实 AIGC 模型
1. 修改 .env 中 AIGC_PROVIDER=stability
2. 填入 STABILITY_API_KEY
3. 或配置 COMFYUI_URL 使用本地模型

### 接入 FISCO BCOS 区块链
1. 部署 FISCO BCOS 节点
2. 部署存证智能合约
3. 修改 .env 中 BLOCKCHAIN_PROVIDER=fisco
4. 在 blockchain_service.py 中实现 _fisco_store 方法
