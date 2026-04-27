# 服务启动文档

本项目为前后端分离应用：

- 后端：FastAPI + SQLAlchemy + SQLite
- 前端：Vue 3 + Vite

## 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

## 首次启动

### 1. 启动后端

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/init_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

说明：

- `python scripts/init_db.py` 会初始化 SQLite 数据库并写入演示数据
- 数据库文件默认生成在 `backend/user_management.db`

### 2. 启动前端

新开一个终端：

```powershell
cd frontend
npm install
npm run dev
```

## 日常开发启动

如果依赖已经安装完成，后续只需执行：

后端：

```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```powershell
cd frontend
npm run dev
```

## 访问地址

- 前端：http://localhost:3000
- 后端接口：http://localhost:8000
- Swagger：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/v1/health

## 默认账号

执行 `python scripts/init_db.py` 后可使用：

- 管理员：`admin` / `admin123`
- 普通用户：`john.doe` / `password123`
- 普通用户：`jane.smith` / `password123`

## 补充说明

- 前端开发服务已将 `/api` 代理到 `http://localhost:8000`
- 启动前端前请先确认后端已经运行
