from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

class TransactionStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Account(Base):
    __tablename__ = "accounts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    balance = Column(String, nullable=False, default="0.00")
    currency = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key = Column(String, unique=True, nullable=False)
    from_account_id = Column(String, nullable=False)
    to_account_id = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)