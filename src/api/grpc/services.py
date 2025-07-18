import grpc
from grpc import aio
from src.api.grpc import financial_pb2, financial_pb2_grpc
from src.core.services import FinancialService
from src.core.schemas import TransactionRequest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class TransactionService(financial_pb2_grpc.TransactionServiceServicer):
    def __init__(self):
        engine = create_engine("postgresql://fintech_user:secure_password@localhost:5432/fintech")
        self.db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
        self.service = FinancialService(self.db)

    async def CreateTransaction(self, request, context):
        try:
            transaction_request = TransactionRequest(
                idempotency_key=request.idempotency_key,
                from_account_id=request.from_account_id,
                to_account_id=request.to_account_id,
                amount=request.amount,
                currency=request.currency
            )
            response = await self.service.create_transaction(transaction_request)
            return financial_pb2.TransactionResponse(
                id=response.id,
                status=response.status.value,
                from_account_id=response.from_account_id,
                to_account_id=response.to_account_id,
                amount=response.amount,
                currency=response.currency,
                created_at=response.created_at
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return financial_pb2.TransactionResponse()

    async def GetBalance(self, request, context):
        try:
            response = await self.service.get_balance(request.account_id)
            return financial_pb2.BalanceResponse(
                account_id=response.account_id,
                available_balance=response.available_balance,
                currency=response.currency,
                last_updated=response.last_updated
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return financial_pb2.BalanceResponse()

async def serve():
    server = aio.server()
    financial_pb2_grpc.add_TransactionServiceServicer_to_server(TransactionService(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())
