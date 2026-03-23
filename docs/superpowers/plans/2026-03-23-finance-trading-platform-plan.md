# 金融交易监控系统 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建完整的金融交易监控系统（Vue3 + FastAPI），包含认证、交易管理、仪表盘、多级菜单、报表生成下载

**Architecture:** 全栈分离架构，前端 Vue3 SPA，后端 FastAPI REST API，SQLite 数据库，JWT 认证

**Tech Stack:** Vue 3, Ant Design Vue, Pinia, Vue Router, Axios, FastAPI, SQLAlchemy, openpyxl

---

## 文件结构总览

```
testing-project-1/
├── backend/
│   └── app/
│       ├── models/
│       │   ├── transaction.py    # 新建
│       │   └── report.py        # 新建
│       ├── schemas/
│       │   ├── transaction.py   # 新建
│       │   └── report.py        # 新建
│       ├── routers/
│       │   ├── transactions.py   # 新建
│       │   └── reports.py       # 新建
│       └── services/
│           └── report_generator.py  # 新建
├── frontend/                     # 新建整个目录
│   ├── src/
│   │   ├── api/
│   │   │   └── index.ts
│   │   ├── components/
│   │   │   ├── AppLayout.vue
│   │   │   ├── AppHeader.vue
│   │   │   └── AppSider.vue
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── stores/
│   │   │   ├── auth.ts
│   │   │   ├── transaction.ts
│   │   │   └── report.ts
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── TransactionListView.vue
│   │   │   ├── TransactionFormView.vue
│   │   │   └── ReportListView.vue
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
└── docs/superpowers/plans/
```

---

## Part 1: 后端扩展

### Task 1: Transaction 模型和路由

**Files:**
- Create: `backend/app/models/transaction.py`
- Create: `backend/app/schemas/transaction.py`
- Create: `backend/app/routers/transactions.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/schemas/__init__.py`
- Modify: `backend/app/routers/__init__.py`
- Modify: `backend/app/main.py:7` (import transactions router)
- Modify: `backend/app/main.py:29` (include transactions router)

- [ ] **Step 1: 创建 Transaction 模型**

`backend/app/models/transaction.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    asset = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="transactions")
```

- [ ] **Step 2: 更新 models/__init__.py**

```python
from app.models.user import User
from app.models.department import Department
from app.models.transaction import Transaction, TransactionType, TransactionStatus

__all__ = ["User", "Department", "Transaction", "TransactionType", "TransactionStatus"]
```

- [ ] **Step 3: 创建 Transaction Schema**

`backend/app/schemas/transaction.py`:
```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransactionBase(BaseModel):
    type: TransactionType
    asset: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0)
    price: float = Field(..., gt=0)


class TransactionCreate(TransactionBase):
    trade_time: Optional[datetime] = None


class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None


class TransactionResponse(TransactionBase):
    id: str
    user_id: str
    status: TransactionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[TransactionResponse]
```

- [ ] **Step 4: 更新 schemas/__init__.py**

```python
from app.schemas.user import *
from app.schemas.department import *
from app.schemas.transaction import *

__all__ = ["User", "UserCreate", "UserUpdate", "UserResponse", "UserListResponse",
           "Transaction", "TransactionCreate", "TransactionUpdate", "TransactionResponse", "TransactionListResponse"]
```

- [ ] **Step 5: 创建 Transactions 路由**

`backend/app/routers/transactions.py`:
```python
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse, TransactionListResponse
from app.routers.auth import oauth2_scheme
from app.config import settings
from jose import jwt

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    asset: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if asset:
        query = query.filter(Transaction.asset == asset)
    if type:
        query = query.filter(Transaction.type == type)
    if status:
        query = query.filter(Transaction.status == status)

    total = query.count()
    transactions = query.order_by(desc(Transaction.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[TransactionResponse.model_validate(t) for t in transactions]
    )


@router.post("", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = Transaction(
        user_id=current_user.id,
        type=transaction.type,
        asset=transaction.asset,
        amount=transaction.amount,
        price=transaction.price,
        status=TransactionStatus.PENDING
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: str,
    update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if update.status:
        transaction.status = update.status
    db.commit()
    db.refresh(transaction)
    return transaction
```

- [ ] **Step 6: 更新 routers/__init__.py**

```python
from app.routers.health import router as health_router
from app.routers.users import router as users_router
from app.routers.departments import router as departments_router
from app.routers.auth import router as auth_router
from app.routers.stats import router as stats_router
from app.routers.transactions import router as transactions_router

__all__ = ["health_router", "users_router", "departments_router", "auth_router", "stats_router", "transactions_router"]
```

- [ ] **Step 7: 更新 main.py 引入 transactions router**

修改 `backend/app/main.py`:
- Line 6: `from app.routers import health, users, departments, auth, stats, transactions`
- Line 29: `app.include_router(transactions.router, prefix="/api/v1")`

- [ ] **Step 8: 提交**

```bash
cd C:/Projects/testing-project-1 && git add backend/app/models/transaction.py backend/app/schemas/transaction.py backend/app/routers/transactions.py backend/app/models/__init__.py backend/app/schemas/__init__.py backend/app/routers/__init__.py backend/app/main.py && git commit -m "feat: add Transaction model and API router"
```

---

### Task 2: Report 模型、Schema、路由和报表生成服务

**Files:**
- Create: `backend/app/models/report.py`
- Create: `backend/app/schemas/report.py`
- Create: `backend/app/routers/reports.py`
- Create: `backend/app/services/report_generator.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/schemas/__init__.py`
- Modify: `backend/app/routers/__init__.py`
- Modify: `backend/app/main.py`

**Dependencies:** Task 1 must complete first

- [ ] **Step 1: 创建 Report 模型**

`backend/app/models/report.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ReportType(str, enum.Enum):
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(SQLEnum(ReportType), nullable=False)
    file_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="reports")
```

- [ ] **Step 2: 更新 models/__init__.py**

```python
from app.models.user import User
from app.models.department import Department
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.report import Report, ReportType

__all__ = ["User", "Department", "Transaction", "TransactionType", "TransactionStatus", "Report", "ReportType"]
```

- [ ] **Step 3: 创建 Report Schema**

`backend/app/schemas/report.py`:
```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ReportType(str, Enum):
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ReportGenerateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: ReportType


class ReportResponse(BaseModel):
    id: str
    user_id: str
    name: str
    type: ReportType
    file_path: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    total: int
    items: list[ReportResponse]
```

- [ ] **Step 4: 更新 schemas/__init__.py**

```python
from app.schemas.user import *
from app.schemas.department import *
from app.schemas.transaction import *
from app.schemas.report import *

__all__ = ["User", "UserCreate", "UserUpdate", "UserResponse", "UserListResponse",
           "Transaction", "TransactionCreate", "TransactionUpdate", "TransactionResponse", "TransactionListResponse",
           "ReportType", "ReportGenerateRequest", "ReportResponse", "ReportListResponse"]
```

- [ ] **Step 5: 创建 Report 生成服务**

`backend/app/services/report_generator.py`:
```python
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


def generate_excel_report(db: Session, user_id: str, report_name: str, report_type: str) -> str:
    """Generate Excel report and return file path"""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_name}_{report_type}_{timestamp}.xlsx"
    filepath = os.path.join(reports_dir, filename)

    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"

    headers = ["ID", "Type", "Asset", "Amount", "Price", "Status", "Created At"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for row, t in enumerate(transactions, 2):
        ws.cell(row=row, column=1, value=t.id)
        ws.cell(row=row, column=2, value=t.type.value)
        ws.cell(row=row, column=3, value=t.asset)
        ws.cell(row=row, column=4, value=t.amount)
        ws.cell(row=row, column=5, value=t.price)
        ws.cell(row=row, column=6, value=t.status.value)
        ws.cell(row=row, column=7, value=t.created_at.strftime("%Y-%m-%d %H:%M:%S"))

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )
    for row in ws.iter_rows(min_row=1, max_row=len(transactions) + 1, min_col=1, max_col=7):
        for cell in row:
            cell.border = thin_border

    for col in range(1, 8):
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = 20

    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["G"].width = 25

    wb.save(filepath)
    return filepath
```

- [ ] **Step 6: 创建 Reports 路由**

`backend/app/routers/reports.py`:
```python
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.report import Report
from app.schemas.report import ReportGenerateRequest, ReportResponse, ReportListResponse
from app.routers.auth import oauth2_scheme
from app.services.report_generator import generate_excel_report
from app.config import settings
from jose import jwt

router = APIRouter(prefix="/reports", tags=["Reports"])

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("", response_model=ReportListResponse)
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reports = db.query(Report).filter(Report.user_id == current_user.id).all()
    return ReportListResponse(total=len(reports), items=[ReportResponse.model_validate(r) for r in reports])


@router.post("/generate", response_model=ReportResponse)
def generate_report(
    request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_path = generate_excel_report(db, current_user.id, request.name, request.type.value)

    report = Report(
        user_id=current_user.id,
        name=request.name,
        type=request.type,
        file_path=file_path
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}/download")
def download_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(
        report.file_path,
        filename=os.path.basename(report.file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

- [ ] **Step 7: 更新 routers/__init__.py**

```python
from app.routers.health import router as health_router
from app.routers.users import router as users_router
from app.routers.departments import router as departments_router
from app.routers.auth import router as auth_router
from app.routers.stats import router as stats_router
from app.routers.transactions import router as transactions_router
from app.routers.reports import router as reports_router

__all__ = ["health_router", "users_router", "departments_router", "auth_router", "stats_router", "transactions_router", "reports_router"]
```

- [ ] **Step 8: 更新 main.py 引入 reports router**

修改 `backend/app/main.py`:
- Line 6: `from app.routers import health, users, departments, auth, stats, transactions, reports`
- Line 29: `app.include_router(reports.router, prefix="/api/v1")`

- [ ] **Step 9: 添加 openpyxl 到 requirements.txt**

`backend/requirements.txt`:
```
openpyxl>=3.1.0
```

- [ ] **Step 10: 提交**

```bash
git add backend/app/models/report.py backend/app/schemas/report.py backend/app/routers/reports.py backend/app/services/report_generator.py backend/app/models/__init__.py backend/app/schemas/__init__.py backend/app/routers/__init__.py backend/app/main.py backend/requirements.txt && git commit -m "feat: add Report model, API and Excel generation"
```

---

## Part 2: 前端项目搭建

### Task 3: Vue3 项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/env.d.ts`

**Dependencies:** Tasks 1 & 2 complete

- [ ] **Step 1: 创建 package.json**

`frontend/package.json`:
```json
{
  "name": "finance-trading-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "ant-design-vue": "^4.1.0",
    "axios": "^1.6.0",
    "dayjs": "^1.11.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vue-tsc": "^1.8.0"
  }
}
```

- [ ] **Step 2: 创建 vite.config.ts**

`frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **Step 3: 创建 tsconfig.json**

`frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: 创建 tsconfig.node.json**

`frontend/tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: 创建 index.html**

`frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>金融交易监控系统</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 6: 创建 src/main.ts**

`frontend/src/main.ts`:
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(Antd)
app.mount('#app')
```

- [ ] **Step 7: 创建 src/App.vue**

`frontend/src/App.vue`:
```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
#app {
  height: 100vh;
}
body {
  margin: 0;
  padding: 0;
}
</style>
```

- [ ] **Step 8: 创建 src/env.d.ts**

`frontend/src/env.d.ts`:
```typescript
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 9: 提交**

```bash
git add frontend/package.json frontend/vite.config.ts frontend/tsconfig.json frontend/tsconfig.node.json frontend/index.html frontend/src/main.ts frontend/src/App.vue frontend/src/env.d.ts && git commit -m "feat: scaffold Vue3 frontend project with Vite"
```

---

### Task 4: 前端类型定义和 API 层

**Files:**
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/api/index.ts`

**Dependencies:** Task 3 complete

- [ ] **Step 1: 创建类型定义**

`frontend/src/types/index.ts`:
```typescript
export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export type TransactionType = 'buy' | 'sell'
export type TransactionStatus = 'pending' | 'completed' | 'cancelled'

export interface Transaction {
  id: string
  user_id: string
  type: TransactionType
  asset: string
  amount: number
  price: number
  status: TransactionStatus
  created_at: string
}

export interface TransactionCreate {
  type: TransactionType
  asset: string
  amount: number
  price: number
  trade_time?: string
}

export interface TransactionListResponse {
  total: number
  page: number
  page_size: number
  items: Transaction[]
}

export type ReportType = 'daily' | 'monthly' | 'quarterly' | 'yearly'

export interface Report {
  id: string
  user_id: string
  name: string
  type: ReportType
  file_path: string | null
  created_at: string
}

export interface ReportGenerateRequest {
  name: string
  type: ReportType
}

export interface ReportListResponse {
  total: number
  items: Report[]
}

export interface MenuItem {
  key: string
  label: string
  icon?: string
  children?: MenuItem[]
}
```

- [ ] **Step 2: 创建 API 层**

`frontend/src/api/index.ts`:
```typescript
import axios from 'axios'
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  Transaction,
  TransactionCreate,
  TransactionListResponse,
  Report,
  ReportGenerateRequest,
  ReportListResponse
} from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data: LoginRequest) =>
    api.post<AuthResponse>('/auth/login', data),
  register: (data: RegisterRequest) =>
    api.post<AuthResponse>('/auth/register', data),
  me: () => api.get('/auth/me')
}

export const transactionApi = {
  list: (params: {
    page?: number
    page_size?: number
    asset?: string
    type?: string
    status?: string
  }) => api.get<TransactionListResponse>('/transactions', { params }),
  create: (data: TransactionCreate) =>
    api.post<Transaction>('/transactions', data),
  get: (id: string) => api.get<Transaction>(`/transactions/${id}`),
  update: (id: string, data: { status: string }) =>
    api.patch<Transaction>(`/transactions/${id}`, data)
}

export const reportApi = {
  list: () => api.get<ReportListResponse>('/reports'),
  generate: (data: ReportGenerateRequest) =>
    api.post<Report>('/reports/generate', data),
  download: (id: string) => `/api/v1/reports/${id}/download`
}

export default api
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/types/index.ts frontend/src/api/index.ts && git commit -m "feat: add TypeScript types and API layer"
```

---

## Part 3: 前端状态管理

### Task 5: Pinia Stores

**Files:**
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/stores/transaction.ts`
- Create: `frontend/src/stores/report.ts`

**Dependencies:** Task 4 complete

- [ ] **Step 1: 创建 auth store**

`frontend/src/stores/auth.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api'
import type { User, LoginRequest, RegisterRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isAuthenticated = !!token.value

  async function login(data: LoginRequest) {
    const response = await authApi.login(data)
    token.value = response.data.access_token
    user.value = response.data.user
    localStorage.setItem('token', response.data.access_token)
    return response.data
  }

  async function register(data: RegisterRequest) {
    const response = await authApi.register(data)
    return response.data
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await authApi.me()
      user.value = response.data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isAuthenticated, login, register, fetchUser, logout }
})
```

- [ ] **Step 2: 创建 transaction store**

`frontend/src/stores/transaction.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { transactionApi } from '@/api'
import type { Transaction, TransactionCreate } from '@/types'

export const useTransactionStore = defineStore('transaction', () => {
  const transactions = ref<Transaction[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)
  const loading = ref(false)

  async function fetchTransactions(params?: {
    page?: number
    page_size?: number
    asset?: string
    type?: string
    status?: string
  }) {
    loading.value = true
    try {
      const response = await transactionApi.list({
        page: params?.page ?? page.value,
        page_size: params?.page_size ?? pageSize.value,
        ...params
      })
      transactions.value = response.data.items
      total.value = response.data.total
      page.value = response.data.page
      pageSize.value = response.data.page_size
    } finally {
      loading.value = false
    }
  }

  async function createTransaction(data: TransactionCreate) {
    const response = await transactionApi.create(data)
    return response.data
  }

  return { transactions, total, page, pageSize, loading, fetchTransactions, createTransaction }
})
```

- [ ] **Step 3: 创建 report store**

`frontend/src/stores/report.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reportApi } from '@/api'
import type { Report, ReportGenerateRequest } from '@/types'

export const useReportStore = defineStore('report', () => {
  const reports = ref<Report[]>([])
  const loading = ref(false)

  async function fetchReports() {
    loading.value = true
    try {
      const response = await reportApi.list()
      reports.value = response.data.items
    } finally {
      loading.value = false
    }
  }

  async function generateReport(data: ReportGenerateRequest) {
    const response = await reportApi.generate(data)
    return response.data
  }

  function getDownloadUrl(id: string) {
    return reportApi.download(id)
  }

  return { reports, loading, fetchReports, generateReport, getDownloadUrl }
})
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/stores/auth.ts frontend/src/stores/transaction.ts frontend/src/stores/report.ts && git commit -m "feat: add Pinia stores for auth, transaction and report"
```

---

## Part 4: 前端路由和组件

### Task 6: 路由配置

**Files:**
- Create: `frontend/src/router/index.ts`

**Dependencies:** Task 5 complete

- [ ] **Step 1: 创建路由配置**

`frontend/src/router/index.ts`:
```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      {
        path: 'transactions',
        name: 'Transactions',
        component: () => import('@/views/TransactionListView.vue')
      },
      {
        path: 'transactions/new',
        name: 'NewTransaction',
        component: () => import('@/views/TransactionFormView.vue')
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/ReportListView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/router/index.ts && git commit -m "feat: add Vue Router configuration with auth guards"
```

---

### Task 7: AppLayout 和导航组件

**Files:**
- Create: `frontend/src/components/AppLayout.vue`
- Create: `frontend/src/components/AppHeader.vue`
- Create: `frontend/src/components/AppSider.vue`

**Dependencies:** Task 6 complete

- [ ] **Step 1: 创建 AppLayout**

`frontend/src/components/AppLayout.vue`:
```vue
<template>
  <a-layout style="height: 100vh">
    <AppSider :menus="menus" v-model:collapsed="collapsed" />
    <a-layout>
      <AppHeader />
      <a-layout-content style="padding: 24px; overflow-y: auto">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSider from './AppSider.vue'
import type { MenuItem } from '@/types'

const collapsed = ref(false)

const menus: MenuItem[] = [
  {
    key: 'monitor',
    label: '监控',
    children: [
      {
        key: 'dashboard',
        label: '实时大盘',
        children: [
          { key: 'dashboard-overview', label: '概览' },
          { key: 'dashboard-detail', label: '详情' }
        ]
      },
      {
        key: 'alerts',
        label: '告警中心',
        children: [
          { key: 'alerts-list', label: '告警列表' },
          { key: 'alerts-rules', label: '告警规则' }
        ]
      }
    ]
  },
  {
    key: 'trade',
    label: '交易',
    children: [
      { key: 'transactions', label: '交易记录' },
      { key: 'transactions-new', label: '下单' }
    ]
  },
  {
    key: 'report',
    label: '报表',
    children: [
      {
        key: 'reports',
        label: '报表中心',
        children: [
          { key: 'reports-monthly', label: '月报' },
          { key: 'reports-quarterly', label: '季报' },
          { key: 'reports-yearly', label: '年报' }
        ]
      },
      { key: 'reports-export', label: '导出' }
    ]
  }
]
</script>
```

- [ ] **Step 2: 创建 AppHeader**

`frontend/src/components/AppHeader.vue`:
```vue
<template>
  <a-layout-header style="background: #001529; padding: 0 24px; display: flex; align-items: center; justify-content: space-between">
    <div style="color: white; font-size: 18px; font-weight: bold">金融交易监控系统</div>
    <a-dropdown>
      <a-avatar style="cursor: pointer">{{ user?.username?.[0]?.toUpperCase() }}</a-avatar>
      <template #overlay>
        <a-menu>
          <a-menu-item key="profile">
            <a-space direction="vertical" style="width: 100%">
              <div>{{ user?.username }}</div>
              <div style="font-size: 12px; color: #999">{{ user?.email }}</div>
            </a-space>
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item key="logout" @click="handleLogout">退出登录</a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </a-layout-header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
```

- [ ] **Step 3: 创建 AppSider**

`frontend/src/components/AppSider.vue`:
```vue
<template>
  <a-layout-sider v-model:collapsed="collapsed" :trigger="null" collapsible style="overflow: auto">
    <div v-if="!collapsed" style="height: 64px; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; font-weight: bold; border-bottom: 1px solid #ffffff20">
      FinanceTrade
    </div>
    <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline" :items="menuItems" @click="handleMenuClick" />
  </a-layout-sider>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { MenuProps } from 'ant-design-vue'
import type { MenuItem } from '@/types'

const props = defineProps<{
  menus: MenuItem[]
  collapsed: boolean
}>()

const router = useRouter()
const route = useRoute()
const selectedKeys = ref<string[]>([route.name as string])

function buildMenuItems(menus: MenuItem[]): MenuProps['items'] {
  return menus.map((menu) => {
    if (menu.children) {
      return {
        key: menu.key,
        label: menu.label,
        children: buildMenuItems(menu.children)
      }
    }
    return {
      key: menu.key,
      label: menu.label
    }
  })
}

const menuItems = ref<MenuProps['items']>([])

watch(
  () => props.menus,
  (newMenus) => {
    menuItems.value = buildMenuItems(newMenus)
  },
  { immediate: true }
)

function handleMenuClick({ key }: { key: string }) {
  const routeMap: Record<string, string> = {
    'dashboard-overview': '/dashboard',
    'dashboard-detail': '/dashboard',
    'dashboard': '/dashboard',
    'transactions': '/transactions',
    'transactions-new': '/transactions/new',
    'reports': '/reports',
    'reports-monthly': '/reports',
    'reports-quarterly': '/reports',
    'reports-yearly': '/reports',
    'reports-export': '/reports',
    'alerts-list': '/dashboard',
    'alerts-rules': '/dashboard'
  }
  const path = routeMap[key]
  if (path) {
    router.push(path)
  }
}
</script>
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/components/AppLayout.vue frontend/src/components/AppHeader.vue frontend/src/components/AppSider.vue && git commit -m "feat: add AppLayout with nested menu navigation"
```

---

### Task 8: 登录和注册页面

**Files:**
- Create: `frontend/src/views/LoginView.vue`
- Create: `frontend/src/views/RegisterView.vue`

**Dependencies:** Task 7 complete

- [ ] **Step 1: 创建 LoginView**

`frontend/src/views/LoginView.vue`:
```vue
<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5">
    <a-card style="width: 400px">
      <template #title>
        <div style="text-align: center; font-size: 20px">金融交易监控系统</div>
      </template>
      <a-form :model="form" @finish="handleLogin">
        <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="form.username" placeholder="用户名" size="large">
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
          <a-input-password v-model:value="form.password" placeholder="密码" size="large">
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">登录</a-button>
        </a-form-item>
        <div style="text-align: center">
          还没有账号？<router-link to="/register">立即注册</router-link>
        </div>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(form)
    message.success('登录成功')
    router.push('/dashboard')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 2: 创建 RegisterView**

`frontend/src/views/RegisterView.vue`:
```vue
<template>
  <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5">
    <a-card style="width: 400px">
      <template #title>
        <div style="text-align: center; font-size: 20px">用户注册</div>
      </template>
      <a-form :model="form" @finish="handleRegister">
        <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="form.username" placeholder="用户名" size="large">
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="email" :rules="[{ required: true, type: 'email', message: '请输入有效邮箱' }]">
          <a-input v-model:value="form.email" placeholder="邮箱" size="large">
            <template #prefix><MailOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="full_name" :rules="[{ required: true, message: '请输入姓名' }]">
          <a-input v-model:value="form.full_name" placeholder="姓名" size="large">
            <template #prefix><IdcardOutlined /></template>
          </a-input>
        </a-form-item>
        <a-form-item name="password" :rules="[{ required: true, min: 8, message: '密码至少8位' }]">
          <a-input-password v-model:value="form.password" placeholder="密码" size="large">
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" size="large" block :loading="loading">注册</a-button>
        </a-form-item>
        <div style="text-align: center">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, MailOutlined, IdcardOutlined } from '@ant-design/icons-vue'
import { authApi } from '@/api'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  full_name: '',
  password: ''
})

async function handleRegister() {
  loading.value = true
  try {
    await authApi.register(form)
    message.success('注册成功，请登录')
    router.push('/login')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/LoginView.vue frontend/src/views/RegisterView.vue && git commit -m "feat: add Login and Register views"
```

---

### Task 9: 仪表盘页面

**Files:**
- Create: `frontend/src/views/DashboardView.vue`

**Dependencies:** Task 8 complete

- [ ] **Step 1: 创建 DashboardView**

`frontend/src/views/DashboardView.vue`:
```vue
<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 16px">
      <a-col :span="6">
        <a-select v-model:value="filters.asset" placeholder="选择账户" style="width: 100%" allow-clear @change="handleFilterChange">
          <a-select-option value="BTC">BTC</a-select-option>
          <a-select-option value="ETH">ETH</a-select-option>
          <a-select-option value="USD">USD</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="6">
        <a-select v-model:value="filters.type" placeholder="交易类型" style="width: 100%" allow-clear @change="handleFilterChange">
          <a-select-option value="buy">买入</a-select-option>
          <a-select-option value="sell">卖出</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="12">
        <a-range-picker v-model:value="filters.dateRange" style="width: 100%" @change="handleFilterChange" />
      </a-col>
    </a-row>

    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6">
        <a-card>
          <a-statistic title="总交易笔数" :value="stats.totalTransactions" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="总买入" :value="stats.totalBuy" suffix="笔" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="总卖出" :value="stats.totalSell" suffix="笔" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="累计交易额" :value="stats.totalAmount" prefix="$" />
        </a-card>
      </a-col>
    </a-row>

    <a-card title="交易趋势">
      <div style="height: 300px; display: flex; align-items: center; justify-content: center; color: #999">
        图表区域 (ECharts)
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, computed } from 'vue'
import { useTransactionStore } from '@/stores/transaction'
import { storeToRefs } from 'pinia'
import type { Dayjs } from 'dayjs'

const transactionStore = useTransactionStore()
const { transactions, total } = storeToRefs(transactionStore)

const filters = reactive({
  asset: undefined as string | undefined,
  type: undefined as string | undefined,
  dateRange: null as [Dayjs, Dayjs] | null
})

onMounted(() => {
  transactionStore.fetchTransactions({ page_size: 100 })
})

function handleFilterChange() {
  transactionStore.fetchTransactions({
    page: 1,
    asset: filters.asset,
    type: filters.type
  })
}

const stats = computed(() => {
  const txs = transactions.value
  return {
    totalTransactions: txs.length,
    totalBuy: txs.filter((t) => t.type === 'buy').length,
    totalSell: txs.filter((t) => t.type === 'sell').length,
    totalAmount: txs.reduce((sum, t) => sum + t.amount * t.price, 0)
  }
})
</script>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/views/DashboardView.vue && git commit -m "feat: add Dashboard view with filters and statistics"
```

---

### Task 10: 交易列表和下单表单页面

**Files:**
- Create: `frontend/src/views/TransactionListView.vue`
- Create: `frontend/src/views/TransactionFormView.vue`

**Dependencies:** Task 9 complete

- [ ] **Step 1: 创建 TransactionListView**

`frontend/src/views/TransactionListView.vue`:
```vue
<template>
  <div>
    <a-row :gutter="16" style="margin-bottom: 16px">
      <a-col :span="4">
        <a-select v-model:value="searchFilters.asset" placeholder="账户" style="width: 100%" allow-clear @change="handleSearch">
          <a-select-option value="BTC">BTC</a-select-option>
          <a-select-option value="ETH">ETH</a-select-option>
          <a-select-option value="USD">USD</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="4">
        <a-select v-model:value="searchFilters.type" placeholder="类型" style="width: 100%" allow-clear @change="handleSearch">
          <a-select-option value="buy">买入</a-select-option>
          <a-select-option value="sell">卖出</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="4">
        <a-select v-model:value="searchFilters.status" placeholder="状态" style="width: 100%" allow-clear @change="handleSearch">
          <a-select-option value="pending">待处理</a-select-option>
          <a-select-option value="completed">已完成</a-select-option>
          <a-select-option value="cancelled">已取消</a-select-option>
        </a-select>
      </a-col>
      <a-col :span="4">
        <a-button type="primary" @click="goToCreate">新建交易</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="transactions" :columns="columns" :loading="loading" :pagination="pagination" @change="handleTableChange" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'type'">
          <a-tag :color="record.type === 'buy' ? 'green' : 'red'">{{ record.type === 'buy' ? '买入' : '卖出' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="statusColor[record.status]">{{ statusText[record.status] }}</a-tag>
        </template>
        <template v-else-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTransactionStore } from '@/stores/transaction'
import { storeToRefs } from 'pinia'
import dayjs from 'dayjs'

const router = useRouter()
const transactionStore = useTransactionStore()
const { transactions, total, page, pageSize, loading } = storeToRefs(transactionStore)

const searchFilters = reactive({
  asset: undefined as string | undefined,
  type: undefined as string | undefined,
  status: undefined as string | undefined
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 200 },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '资产', dataIndex: 'asset', key: 'asset' },
  { title: '数量', dataIndex: 'amount', key: 'amount' },
  { title: '价格', dataIndex: 'price', key: 'price' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '时间', dataIndex: 'created_at', key: 'created_at' }
]

const pagination = reactive({
  current: page,
  pageSize: pageSize,
  total: total,
  showSizeChanger: true,
  showTotal: (t: number) => `共 ${t} 条`
})

const statusColor: Record<string, string> = {
  pending: 'orange',
  completed: 'green',
  cancelled: 'grey'
}

const statusText: Record<string, string> = {
  pending: '待处理',
  completed: '已完成',
  cancelled: '已取消'
}

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  transactionStore.fetchTransactions()
})

function handleSearch() {
  transactionStore.fetchTransactions({ page: 1, ...searchFilters })
}

function handleTableChange(pag: any) {
  transactionStore.fetchTransactions({ page: pag.current, page_size: pag.pageSize, ...searchFilters })
}

function goToCreate() {
  router.push('/transactions/new')
}
</script>
```

- [ ] **Step 2: 创建 TransactionFormView**

`frontend/src/views/TransactionFormView.vue`:
```vue
<template>
  <div style="max-width: 600px">
    <a-card title="新建交易">
      <a-form :model="form" layout="vertical" @finish="handleSubmit">
        <a-form-item label="交易类型" name="type" :rules="[{ required: true, message: '请选择交易类型' }]">
          <a-select v-model:value="form.type" placeholder="请选择">
            <a-select-option value="buy">买入</a-select-option>
            <a-select-option value="sell">卖出</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="资产" name="asset" :rules="[{ required: true, message: '请输入资产' }]">
          <a-select v-model:value="form.asset" placeholder="请选择资产">
            <a-select-option value="BTC">BTC</a-select-option>
            <a-select-option value="ETH">ETH</a-select-option>
            <a-select-option value="USD">USD</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="数量" name="amount" :rules="[{ required: true, message: '请输入数量' }, { type: 'number', min: 0.0001, message: '数量必须大于0' }]">
          <a-input-number v-model:value="form.amount" style="width: 100%" :min="0" :precision="4" />
        </a-form-item>

        <a-form-item label="价格" name="price" :rules="[{ required: true, message: '请输入价格' }, { type: 'number', min: 0, message: '价格必须大于等于0' }]">
          <a-input-number v-model:value="form.price" style="width: 100%" :min="0" :precision="2" prefix="$" />
        </a-form-item>

        <a-form-item label="交易时间" name="trade_time" :rules="[{ required: true, message: '请选择交易时间' }]">
          <a-date-picker v-model:value="form.trade_time" style="width: 100%" show-time format="YYYY-MM-DD HH:mm:ss" />
        </a-form-item>

        <a-form-item>
          <a-space>
            <a-button type="primary" html-type="submit" :loading="loading">提交</a-button>
            <a-button @click="router.push('/transactions')">取消</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useTransactionStore } from '@/stores/transaction'
import dayjs from 'dayjs'

const router = useRouter()
const transactionStore = useTransactionStore()
const loading = ref(false)

const form = reactive({
  type: undefined as 'buy' | 'sell' | undefined,
  asset: undefined as string | undefined,
  amount: 0,
  price: 0,
  trade_time: null as dayjs.Dayjs | null
})

async function handleSubmit() {
  if (!form.type || !form.asset || !form.trade_time) {
    message.error('请填写完整信息')
    return
  }
  loading.value = true
  try {
    await transactionStore.createTransaction({
      type: form.type,
      asset: form.asset,
      amount: form.amount,
      price: form.price,
      trade_time: form.trade_time.format('YYYY-MM-DDTHH:mm:ss')
    })
    message.success('创建成功')
    router.push('/transactions')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '创建失败')
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/TransactionListView.vue frontend/src/views/TransactionFormView.vue && git commit -m "feat: add Transaction list and form views"
```

---

### Task 11: 报表页面

**Files:**
- Create: `frontend/src/views/ReportListView.vue`

**Dependencies:** Task 10 complete

- [ ] **Step 1: 创建 ReportListView**

`frontend/src/views/ReportListView.vue`:
```vue
<template>
  <div>
    <a-row style="margin-bottom: 16px" justify="end">
      <a-col>
        <a-button type="primary" @click="showGenerateModal = true">生成报表</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="reports" :columns="columns" :loading="loading" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'type'">
          <a-tag>{{ typeText[record.type] }}</a-tag>
        </template>
        <template v-else-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" :href="getDownloadUrl(record.id)" :disabled="!record.file_path">下载</a-button>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="showGenerateModal" title="生成报表" @ok="handleGenerate">
      <a-form :model="generateForm" layout="vertical">
        <a-form-item label="报表名称" name="name" :rules="[{ required: true, message: '请输入报表名称' }]">
          <a-input v-model:value="generateForm.name" placeholder="请输入报表名称" />
        </a-form-item>
        <a-form-item label="报表类型" name="type" :rules="[{ required: true, message: '请选择报表类型' }]">
          <a-select v-model:value="generateForm.type" placeholder="请选择">
            <a-select-option value="daily">日报</a-select-option>
            <a-select-option value="monthly">月报</a-select-option>
            <a-select-option value="quarterly">季报</a-select-option>
            <a-select-option value="yearly">年报</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useReportStore } from '@/stores/report'
import { storeToRefs } from 'pinia'
import dayjs from 'dayjs'

const reportStore = useReportStore()
const { reports, loading } = storeToRefs(reportStore)

const showGenerateModal = ref(false)
const generateLoading = ref(false)

const generateForm = reactive({
  name: '',
  type: undefined as string | undefined
})

const columns = [
  { title: '报表名称', dataIndex: 'name', key: 'name' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '生成时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action' }
]

const typeText: Record<string, string> = {
  daily: '日报',
  monthly: '月报',
  quarterly: '季报',
  yearly: '年报'
}

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

function getDownloadUrl(id: string) {
  return reportStore.getDownloadUrl(id)
}

onMounted(() => {
  reportStore.fetchReports()
})

async function handleGenerate() {
  if (!generateForm.name || !generateForm.type) {
    message.error('请填写完整信息')
    return
  }
  generateLoading.value = true
  try {
    await reportStore.generateReport({
      name: generateForm.name,
      type: generateForm.type as any
    })
    message.success('生成成功')
    showGenerateModal.value = false
    generateForm.name = ''
    generateForm.type = undefined
    reportStore.fetchReports()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '生成失败')
  } finally {
    generateLoading.value = false
  }
}
</script>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/views/ReportListView.vue && git commit -m "feat: add Report list view with generate and download"
```

---

## Part 5: 集成测试

### Task 12: 后端注册接口适配

**Files:**
- Modify: `backend/app/routers/auth.py`

**Dependencies:** Tasks 1-2 complete

- [ ] **Step 1: 添加注册路由**

在 `backend/app/routers/auth.py` 末尾添加:

```python
@router.post("/register")
def register(
    username: str,
    email: str,
    password: str,
    full_name: str,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = pwd_context.hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/routers/auth.py && git commit -m "feat: add register endpoint to auth router"
```

---

### Task 13: 最终验证

**Files:**
- Verify: 所有文件存在且正确

**Dependencies:** All tasks complete

- [ ] **Step 1: 安装后端依赖并验证后端启动**

```bash
cd C:/Projects/testing-project-1/backend && pip install -r requirements.txt && python -c "from app.main import app; print('Backend OK')"
```

Expected: `Backend OK`

- [ ] **Step 2: 安装前端依赖并验证前端构建**

```bash
cd C:/Projects/testing-project-1/frontend && npm install && npm run build 2>&1 | head -20
```

Expected: Build successful with no errors

- [ ] **Step 3: 提交所有更改**

```bash
cd C:/Projects/testing-project-1 && git status
```

Review all changed files, then commit any remaining changes.

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-03-23-finance-trading-platform-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
