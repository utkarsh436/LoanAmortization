import math

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
    try:
        result = db_session.query(models.UserModel).filter(models.UserModel.id == user_id).first()
        if not result:
            return {
                "message": "no user found",
                "data": {},
                "status": 404
            }
        return {
            "data": result
        }
    except Exception as e:
        return {e}
    finally:
        db_session.close()


@app.post("/user")
async def create_user(request: Request):
    payload = await request.json()
    db_session = SessionLocal()
    if not payload:
        return{
            "message": "invalid payload",
            "data": {},
            "status": 404
        }
    try:

        email = payload["email"]
        password = payload["password"]
        first_name = payload["first_name"]
        last_name = payload["last_name"]

        user_model = models.UserModel(email=email, hashed_password=password, first_name=first_name, last_name=last_name)
        db_session.add(user_model)
        db_session.commit()
        db_session.refresh(user_model)

        return {
            "data": user_model
        }
    except Exception as e:
        return{e}
    finally:
        db_session.close()


@app.post("/loans/")
async def create_loan(request: Request):
    error_message = "invalid payload"
    db_session = SessionLocal()
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


        loan_model = models.LoanModel(amount=loan_amount, interest=loan_interest, term_months=loan_months, owner=owner)
        db_session.add(loan_model)
        db_session.commit()
        db_session.refresh(loan_model)

        for id in user_ids:
            user_obj = db_session.query(models.UserModel).filter(models.UserModel.id == id).first()
            if user_obj:
                user_obj.loans.append(loan_model)
                db_session.commit()

        return {
            "message": "loan created",
            "data": {
                "loan_id": loan_model.id
            },
            "status": 200
        }
    except Exception as e:
        return {e}
    finally:
        db_session.close()

@app.get("/loans/{loan_id}")
def get_loan(loan_id: int):
    db_session = SessionLocal()
    if not loan_id:
        return {
            "message": "no loan id passed",
            "data": {},
            "status": 404
        }
    try:
        result = db_session.query(models.LoanModel).filter(models.LoanModel.id == loan_id).first()
        if not result:
            return {
                "message": "no loan found",
                "data": {},
                "status": 404
            }
        return {
            "data": result
        }
    except Exception as e:
        return {e}
    finally:
        db_session.close()

@app.get("/loans/user/{user_id}")
def get_user_loans(user_id: int):
    """
    gets all loan objects for a user
    :param user_id:
    :return: array of loan objects associated to user
    """
    if not user_id:
        return {
            "message": "no user id passed",
            "data": {},
            "status": 404
        }
    db_session = SessionLocal()
    try:
        user_obj = db_session.query(models.UserModel).filter(models.UserModel.id == user_id).first()
        res_arr = user_obj.loans
        return {
            "loans": res_arr
        }

    except Exception as e:
        return {e}
    finally:
        db_session.close()

@app.post("/loans/share")
async def share_loan(request: Request):
    """
    shares an existing loan from the given loan id with the user id in the payload
    {
        "loan_id": 1
        "user_id": 2
    }
    :param request:
    :return:
    """
    db_session = SessionLocal()
    try:
        payload = await request.json()
        user_id = payload['user_id']
        loan_id = payload['loan_id']
        if not user_id or not loan_id:
            return{
                "message": "invalid payload",
                "data": {},
                "status": 400
            }
        user_obj = db_session.query(models.UserModel).filter(models.UserModel.id == user_id).first()
        loan_obj = db_session.query(models.LoanModel).filter(models.LoanModel.id == loan_id).first()
        user_obj.loans.append(loan_obj)

        return {
            "message": "loan shared",
            "data": {
                "loan_id": loan_obj.id
            },
            "status": 200
        }

    except Exception as e:
        return {e}
    finally:
        db_session.close()


@app.get("/loans/schedule/{loan_id}")
def get_loan_schedule(loan_id: int):
    """
    {
        month: 1
        remaining_balance: 200000
        monthly_payment:
        ]

    }


    :param loan_id:
    :return:
    """
    if not loan_id:
        return {
            "message": "no loan id passed",
            "data": {},
            "status": 400
        }
    db_session = SessionLocal()
    try:
        loan_obj = db_session.query(models.LoanModel).filter(models.LoanModel.id == loan_id).first()
        amount = loan_obj.amount
        term_months = loan_obj.term_months
        interest = loan_obj.interest

        monthly_interest_rate = (interest/100)/12
        numerator = monthly_interest_rate * math.pow((1+monthly_interest_rate), term_months)
        denominator = ((math.pow(1 + monthly_interest_rate, term_months)) - 1)

        EMI_raw = amount * (numerator/denominator)
        rounded_EMI = round(EMI_raw, 2)
        rounded_EMI_cents = int(rounded_EMI * 100)


        principal_cents = int(amount *100)
        result_list = []
        for month in range(1, term_months+1):
            monthly_interest_amount_cents = int(monthly_interest_rate * principal_cents)
            total_cents = principal_cents + monthly_interest_amount_cents
            remaining_balance_cents = total_cents - rounded_EMI_cents
            if remaining_balance_cents < 0:
                rounded_EMI = total_cents/100.00
                remaining_balance_cents = 0
            monthly_object = {
                "Month": month,
                "interest": monthly_interest_amount_cents/100.00,
                "Remaining_balance": remaining_balance_cents/100.00,
                "Monthly_payment": rounded_EMI
            }
            result_list.append(monthly_object)
            principal_cents = remaining_balance_cents

        return {
            "data": result_list,
            "status": 200
        }

    except Exception as e:
        return {e}
    finally:
        db_session.close()
@app.get("/loans/summary/{loan_id}/month/{month_val}")
def get_loan_summary(loan_id: int, month_val: int):
    if not loan_id or not month_val:
        return {
            "message": "invalid request",
            "data": {},
            "status": 400
        }
    db_session = SessionLocal()
    try:
        loan_obj = db_session.query(models.LoanModel).filter(models.LoanModel.id == loan_id).first()
        term_months = loan_obj.term_months
        amount = loan_obj.amount
        interest = loan_obj.interest

        monthly_interest_rate = (interest / 100) / 12
        numerator = monthly_interest_rate * math.pow((1 + monthly_interest_rate), term_months)
        denominator = ((math.pow(1 + monthly_interest_rate, term_months)) - 1)

        EMI_raw = amount * (numerator / denominator)
        rounded_EMI = round(EMI_raw, 2)
        rounded_EMI_cents = int(rounded_EMI * 100)

        principal_cents = int(amount * 100)

        aggregate_amount_interest_paid = 0
        for month in range(1, month_val + 1):
            monthly_interest_amount_cents = int(monthly_interest_rate * principal_cents)
            aggregate_amount_interest_paid += monthly_interest_amount_cents
            total_cents = principal_cents + monthly_interest_amount_cents
            remaining_balance_cents = total_cents - rounded_EMI_cents
            if remaining_balance_cents < 0:
                rounded_EMI = total_cents / 100.00
                remaining_balance_cents = 0
            principal_cents = remaining_balance_cents
        aggregate_amount_principal_paid = ((amount*100) - principal_cents)/100.00

        return {
            "data": {
                "Current_Principal": principal_cents/100.00,
                "Aggregate Amount of interest paid": aggregate_amount_interest_paid/100.00,
                "Aggregate AMount of principal paid": aggregate_amount_principal_paid
            },
            "status": 200
        }

    except Exception as e:
        return {e}
    finally:
        db_session.close()