from app.routers.health import router as health_router
from app.routers.users import router as users_router
from app.routers.departments import router as departments_router
from app.routers.auth import router as auth_router
from app.routers.stats import router as stats_router
from app.routers.transactions import router as transactions_router
from app.routers.reports import router as reports_router

__all__ = ["health_router", "users_router", "departments_router", "auth_router", "stats_router", "transactions_router", "reports_router"]
