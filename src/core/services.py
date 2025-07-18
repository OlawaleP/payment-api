from sqlalchemy.orm import Session
from src.core.models import Account, Transaction, TransactionStatus
from src.core.schemas import TransactionRequest, TransactionResponse, BalanceResponse
from fastapi import HTTPException
from decimal import Decimal
import uuid
import asyncio

class FinancialService:
    def __init__(self, db: Session):
        self.db = db

    async def create_transaction(self, request: TransactionRequest) -> TransactionResponse:
        existing = self.db.query(Transaction).filter(
            Transaction.idempotency_key == request.idempotency_key
        ).first()
        if existing:
            return self._to_transaction_response(existing)

        from_account = self.db.query(Account).filter(Account.id == request.from_account_id).first()
        to_account = self.db.query(Account).filter(Account.id == request.to_account_id).first()

        if not from_account or not to_account:
            raise HTTPException(status_code=404, detail="Account not found")

        from_balance = Decimal(from_account.balance)
        amount = Decimal(request.amount)
        if from_balance < amount:
            raise HTTPException(status_code=422, detail="Insufficient funds")

        transaction = Transaction(
            idempotency_key=request.idempotency_key,
            from_account_id=request.from_account_id,
            to_account_id=request.to_account_id,
            amount=request.amount,
            currency=request.currency,
            status=TransactionStatus.PENDING
        )
        self.db.add(transaction)
        self.db.commit()

        asyncio.create_task(self._process_transaction(transaction))
        return self._to_transaction_response(transaction)

    async def _process_transaction(self, transaction: Transaction):
        transaction.status = TransactionStatus.COMPLETED
        from_account = self.db.query(Account).filter(Account.id == transaction.from_account_id).first()
        to_account = self.db.query(Account).filter(Account.id == transaction.to_account_id).first()
        amount = Decimal(transaction.amount)
        from_account.balance = str(Decimal(from_account.balance) - amount)
        to_account.balance = str(Decimal(to_account.balance) + amount)
        self.db.commit()

    async def get_balance(self, account_id: str) -> BalanceResponse:
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return BalanceResponse(
            account_id=account_id,
            available_balance=account.balance,
            currency=account.currency,
            last_updated=account.created_at
        )

    def _to_transaction_response(self, transaction: Transaction) -> TransactionResponse:
        return TransactionResponse(
            id=transaction.id,
            status=transaction.status,
            from_account_id=transaction.from_account_id,
            to_account_id=transaction.to_account_id,
            amount=transaction.amount,
            currency=transaction.currency,
            created_at=transaction.created_at
        )
