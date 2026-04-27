# 项目启动手册

本项目是一个前后端分离的用户管理系统：

- 后端：FastAPI + SQLAlchemy + SQLite
- 前端：Vue 3 + Vite + Pinia + Ant Design Vue

## 1. 环境要求

建议先准备以下环境：

- Python 3.10 及以上
- Node.js 18 及以上
- npm 9 及以上

## 2. 首次启动

### 2.1 启动后端

进入后端目录并安装依赖：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

初始化数据库和演示数据：

```powershell
python scripts/init_db.py
```

启动后端服务：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后可访问：

- 接口根地址：`http://localhost:8000/`
- Swagger 文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/v1/health`

### 2.2 启动前端

新开一个终端，进入前端目录并安装依赖：

```powershell
cd frontend
npm install
```

启动前端开发服务：

```powershell
npm run dev
```

前端默认访问地址：

- `http://localhost:3000`

说明：

- 前端已配置代理，`/api` 请求会自动转发到 `http://localhost:8000`
- 启动前端前，请先确保后端已经运行

## 3. 默认账号

执行 `python scripts/init_db.py` 后，会写入演示账号：

- 管理员：`admin` / `admin123`
- 普通用户：`john.doe` / `password123`
- 普通用户：`jane.smith` / `password123`

## 4. 数据库位置

项目默认使用 SQLite，连接串配置在 `backend/app/config.py`：

```python
sqlite:///./user_management.db
```

实际数据库文件会生成在后端运行目录下，通常为：

- `backend/user_management.db`

## 5. 常用启动顺序

每次开发时，按下面顺序即可：

1. 启动后端：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
2. 启动前端：`npm run dev`
3. 打开前端：`http://localhost:3000`
4. 如需查看接口文档，打开：`http://localhost:8000/docs`

## 6. 常见问题

### 前端打开后请求失败

通常是后端没有启动，或后端不是运行在 `8000` 端口。

### 登录失败

请先确认是否执行过：

```powershell
python scripts/init_db.py
```

### 依赖安装失败

可先升级基础工具：

```powershell
python -m pip install --upgrade pip
npm install -g npm
```

## 7. 目录说明

```text
backend/   后端服务
frontend/  前端页面
docs/      项目文档和设计资料
```
