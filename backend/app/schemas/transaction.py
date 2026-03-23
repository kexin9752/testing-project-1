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
