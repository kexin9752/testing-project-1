# 金融交易监控系统 - 设计文档

## 1. 项目概述

**项目名称：** 金融交易监控系统
**项目类型：** 全栈 Web 应用（Vue3 + FastAPI）
**核心功能：** 实时交易监控、交易管理、报表生成与下载
**目标用户：** 金融从业者、数据分析师

## 2. 技术栈

| 层 | 技术 |
|----|------|
| 前端框架 | Vue 3 + Composition API |
| UI 库 | Ant Design Vue |
| 状态管理 | Pinia |
| 路由 | Vue Router |
| HTTP 客户端 | Axios |
| 后端框架 | FastAPI |
| 数据库 | SQLite（开发环境） |
| 报表生成 | openpyxl（Excel） |
| 认证 | JWT Token |

## 3. 项目结构

```
testing-project-1/
├── backend/          # FastAPI 后端
│   └── app/
│       ├── routers/  # API 路由（auth, transactions, reports, stats）
│       ├── models/   # 数据库模型（User, Transaction, Report）
│       ├── schemas/  # Pydantic 模型
│       ├── services/ # 业务逻辑
│       └── main.py  # 应用入口
├── frontend/         # Vue3 前端（新建）
│   └── src/
│       ├── views/    # 页面组件
│       ├── components/# 公共组件
│       ├── stores/   # Pinia 状态管理
│       ├── router/   # Vue Router 配置
│       ├── api/      # API 调用层
│       └── assets/   # 静态资源
└── docs/             # 设计文档
```

## 4. 功能模块

### 4.1 认证模块
- 用户注册（用户名、密码、邮箱）
- 用户登录（JWT Token）
- Token 刷新与过期处理
- 登出功能

### 4.2 仪表盘
- 实时交易数据展示
- 图表可视化（交易趋势）
- 下拉筛选（按账户/币种/时间段）

### 4.3 菜单导航
- 三级嵌套菜单
- 支持展开/折叠
- 刷新后保留菜单状态

**菜单结构示例：**
```
监控
├── 实时大盘
│   ├── 概览
│   └── 详情
└── 告警中心
    ├── 告警列表
    └── 告警规则
交易
├── 交易记录
└── 下单
报表
├── 报表中心
│   ├── 月报
│   ├── 季报
│   └── 年报
└── 导出
```

### 4.4 交易管理
- 交易列表（搜索 + 表格 + 分页）
  - 搜索条件：账户、币种、时间范围、状态
- 交易下单表单
  - 字段：交易类型（下拉）、数量（数字）、价格（数字）、时间（日期选择）

### 4.5 报表中心
- 报表列表展示
- 报表生成（后端处理）
- 报表下载（Excel 格式）

## 5. 页面布局

```
┌─────────────────────────────────────────┐
│  Header（Logo + 应用名 + 用户下拉 + 退出）│
├────────┬────────────────────────────────┤
│        │                                │
│  Side  │        Main Content           │
│  Menu  │        (RouterView)           │
│ (嵌套) │                                │
│        │                                │
└────────┴────────────────────────────────┘
```

- **Header**：固定顶部，包含 Logo、当前用户、下拉菜单
- **Side Menu**：左侧固定，支持多级嵌套和折叠
- **Content**：右侧内容区，根据路由显示

## 6. API 设计

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| GET | `/api/v1/auth/me` | 获取当前用户 |
| GET | `/api/v1/transactions` | 交易列表（分页+搜索） |
| POST | `/api/v1/transactions` | 新建交易 |
| GET | `/api/v1/reports` | 报表列表 |
| POST | `/api/v1/reports/generate` | 生成报表 |
| GET | `/api/v1/reports/{id}/download` | 下载报表 |

## 7. 数据模型

### 7.1 User
```
id: int
username: str (unique)
email: str (unique)
hashed_password: str
created_at: datetime
```

### 7.2 Transaction
```
id: int
user_id: int (FK)
type: str (buy/sell)
asset: str
amount: float
price: float
status: str (pending/completed/cancelled)
created_at: datetime
```

### 7.3 Report
```
id: int
user_id: int (FK)
name: str
type: str (daily/monthly/quarterly/yearly)
file_path: str
created_at: datetime
```

## 8. 组件层级

```
AppLayout
├── Header
│   └── UserDropdown
├── Sider
│   └── Menu (递归组件，支持多级)
└── Content
    └── RouterView
        ├── LoginView
        ├── RegisterView
        ├── DashboardView
        ├── TransactionListView
        ├── TransactionFormView
        └── ReportListView
```

## 9. 状态管理（Pinia）

### 9.1 authStore
- `user`: 当前用户信息
- `token`: JWT Token
- `isAuthenticated`: 认证状态
- `login()`, `register()`, `logout()`

### 9.2 transactionStore
- `transactions`: 交易列表
- `pagination`: 分页信息
- `fetchTransactions()`, `createTransaction()`

### 9.3 reportStore
- `reports`: 报表列表
- `fetchReports()`, `generateReport()`, `downloadReport()`

## 10. 路由配置

```javascript
const routes = [
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: DashboardView },
      { path: 'transactions', component: TransactionListView },
      { path: 'transactions/new', component: TransactionFormView },
      { path: 'reports', component: ReportListView },
    ]
  }
]
```

## 11. 报表生成流程

1. 用户选择报表类型和时间范围
2. 前端调用 `/api/v1/reports/generate`
3. 后端查询数据，使用 openpyxl 生成 Excel
4. 文件保存到服务器指定目录
5. 前端调用 `/api/v1/reports/{id}/download` 下载

## 12. 错误处理

- 401 未授权：跳转登录页
- 400 请求错误：显示错误信息
- 500 服务器错误：显示通用错误提示
- 网络错误：显示重试选项
