from fastapi import FastAPI, Depends, HTTPException, Header
from src.core.schemas import TransactionRequest, TransactionResponse, BalanceResponse
from src.core.services import FinancialService
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from src.core.models import Base
import jwt

app = FastAPI(title="Financial Services API", version="1.0.0")

engine = create_engine("postgresql://fintech_user:secure_password@localhost:5432/fintech")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_financial_service(db: Session = Depends(get_db)):
    return FinancialService(db)

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/v1/transactions", response_model=TransactionResponse)
async def create_transaction(
    request: TransactionRequest,
    service: FinancialService = Depends(get_financial_service),
    user = Depends(verify_token)
):
    return await service.create_transaction(request)

@app.get("/v1/accounts/{account_id}/balance", response_model=BalanceResponse)
async def get_balance(
    account_id: str,
    service: FinancialService = Depends(get_financial_service),
    user = Depends(verify_token)
):
    return await service.get_balance(account_id)

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
