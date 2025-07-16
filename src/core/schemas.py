from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime
from typing import Optional
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class TransactionRequest(BaseModel):
    idempotency_key: str
    from_account_id: str
    to_account_id: str
    amount: str
    currency: str

    @validator('amount')
    def validate_amount(cls, v):
        try:
            amount = Decimal(v)
            if amount <= 0:
                raise ValueError('Amount must be positive')
            return str(amount)
        except:
            raise ValueError('Invalid amount format')

class TransactionResponse(BaseModel):
    id: str
    status: TransactionStatus
    from_account_id: str
    to_account_id: str
    amount: str
    currency: str
    created_at: datetime

class BalanceResponse(BaseModel):
    account_id: str
    available_balance: str
    currency: str
    last_updated: datetime