import models
from fastapi import FastAPI, Request
from database import engine, SessionLocal

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def homepage():
    return{
        "Welcome to loan amortization app"
    }


@app.get("/user/{user_id}")
def get_user(user_id: int):
    if not user_id:
        return {
            "message": "no user id passed",
            "data": {},
            "status": 404
        }
    db_session = SessionLocal()
    result = db_session.query(models.User).filter(models.User.id == user_id).first()
    if not result:
        return {
            "message": "no user found",
            "data": {},
            "status": 404
        }
    return {
        "data": result
    }


@app.post("/user")
async def create_user(request: Request):
    payload = await request.json()
    if not payload:
        return{
            "message": "invalid payload",
            "data": {},
            "status": 404
        }
    db_session = SessionLocal()
    email = payload["email"]
    password = payload["password"]
    first_name = payload["first_name"]
    last_name = payload["last_name"]

    user_model = models.User(email=email, hashed_password=password, first_name=first_name, last_name=last_name)
    db_session.add(user_model)
    db_session.commit()
    db_session.refresh(user_model)

    return {
        "data": user_model
    }


@app.post("/loans/")
async def create_loan(request: Request):
    error_message = "invalid payload"
    try:
        payload = await request.json()
        if not payload or not payload["loan_detail"] or not payload["user_detail"]:
            return {
                "message": error_message,
                "data": {},
                "status": 404
            }

        loan_detail = payload["loan_detail"]
        user_detail = payload["user_detail"]

        loan_amount = loan_detail["amount"]
        loan_interest = loan_detail["interest"]
        loan_months = loan_detail["months"]

        user_ids = user_detail["user_ids"]
        owner = user_detail["owner"]



        return {
            "message": "loan created",
            "data": {
                "payload": payload
            },
            "status": 200
        }
    except Exception as e:
        return {e}

@app.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    return{}

@app.get("/loans/{user_id}")
def get_user_loans(user_id: int):
    return{}

@app.get("/loans/summary/{loan_id}")
def get_loan_summary(loan_id: int):
    return{}