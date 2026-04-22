from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine("sqlite:///expenses.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(String, primary_key=True)
    amount = Column(Integer)  # stored in paise
    category = Column(String)
    description = Column(String)
    date = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    client_id = Column(String, unique=True)  # for idempotency

Base.metadata.create_all(engine)

class ExpenseIn(BaseModel):
    amount: float
    category: str
    description: str
    date: str
    client_id: str  # frontend generates this UUID

@app.post("/expenses")
def create_expense(expense: ExpenseIn):
    db = SessionLocal()
    # Idempotency check
    existing = db.query(Expense).filter_by(client_id=expense.client_id).first()
    if existing:
        db.close()
        return {"id": existing.id, "status": "already exists"}
    
    new_expense = Expense(
        id=str(uuid.uuid4()),
        amount=int(expense.amount * 100),  # convert to paise
        category=expense.category,
        description=expense.description,
        date=expense.date,
        client_id=expense.client_id,
        created_at=datetime.utcnow()
    )
    db.add(new_expense)
    db.commit()
    expense_id = new_expense.id
    db.close()
    return {"id": new_expense.id, "status": "created"}

@app.get("/expenses")
def get_expenses(category: Optional[str] = None, sort: Optional[str] = None):
    db = SessionLocal()
    query = db.query(Expense)
    if category:
        query = query.filter(Expense.category == category)
    if sort == "date_desc":
        query = query.order_by(Expense.date.desc())
    expenses = query.all()
    db.close()
    return [
        {
            "id": e.id,
            "amount": e.amount / 100,  # convert back to rupees
            "category": e.category,
            "description": e.description,
            "date": e.date,
            "created_at": e.created_at,
        }
        for e in expenses
    ]