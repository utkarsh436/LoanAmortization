from fastapi import APIRouter, Request

import math
import models
from database import SessionLocal
from utils import check_loan_details, check_user_details

router = APIRouter(prefix="/loans")

@router.post("/")
async def create_loan(request: Request):
    """
    creates a loan object based on payload and existing users
    sample payload:
            "loan_detail": {
                "amount": 250000,
                "interest": 4.5,
                "months": 360
            },
            "user_detail": {
                "user_ids": [1,2],
                "owner" : 1
            }
        }

    :param request:
    :return: {
    "message": "loan created",
    "data": {
        "id": 8,
        "amount": 250000.0,
        "interest": 4.5,
        "term_months": 360,
        "owner": 1
    },
    "status": 200
}
    """


    error_message = "invalid payload"
    db_session = SessionLocal()
    try:
        payload = await request.json()
        if not payload or not payload.get("loan_detail") or not payload.get("user_detail"):
            return {
                "message": error_message,
                "data": {},
                "status": 400
            }

        loan_detail = payload.get("loan_detail")
        user_detail = payload.get("user_detail")

        loan_amount = loan_detail.get("amount")
        loan_interest = loan_detail.get("interest")
        loan_months = loan_detail.get("months")

        if not loan_amount or not loan_interest or not loan_months:
            raise Exception("missing loan details")
        if not check_loan_details(loan_amount, loan_interest, loan_months):
            raise Exception("invalid loan details")

        user_ids = user_detail.get("user_ids")
        owner = user_detail.get("owner")

        if not user_ids or len(user_ids) == 0 or not owner:
            raise Exception("missing user id details")
        if not check_user_details(user_ids, owner, db_session):
            raise Exception("invalid used detail")

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
                "id": loan_model.id,
                "amount": loan_model.amount,
                "interest": loan_model.interest,
                "term_months": loan_model.term_months,
                "owner": loan_model.owner
            },
            "status": 200
        }
    except Exception as e:
        return {
            "message": str(e),
            "data": {},
            "status": 400
        }
    finally:
        db_session.close()
@router.get("/{loan_id}")
async def get_loan(loan_id: int):
    """
    retrieves a loan object for a specified loan id
    :param loan_id:
    :return: {
    "message": "loan found",
    "data": {
        "id": 7,
        "term_months": 360,
        "interest": 4.5,
        "owner": 1,
        "amount": 430000.0
    },
    "status": 200
}
    """
    db_session = SessionLocal()
    if not loan_id:
        return {
            "message": "no loan id passed",
            "data": {},
            "status": 400
        }
    try:
        result = db_session.query(models.LoanModel).filter(models.LoanModel.id == loan_id).first()
        result.users
        if not result:
            return {
                "message": "no loan found",
                "data": {},
                "status": 400
            }
        return {
            "message": "loan found",
            "data": {
                "loan_details": result
            },
            "status": 200
        }
    except Exception as e:
        return {e}
    finally:
        db_session.close()

@router.get("/user/{user_id}")
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
            "status": 400
        }
    db_session = SessionLocal()
    message = "no loans found"
    try:
        user_obj = db_session.query(models.UserModel).filter(models.UserModel.id == user_id).first()
        res_arr = user_obj.loans
        if res_arr:
            message = "loans found"
        return {
            "message": message,
            "loans": res_arr,
            "status": 200
        }

    except Exception as e:
        return {e}
    finally:
        db_session.close()


@router.post("/share")
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
            return {
                "message": "invalid payload",
                "data": {},
                "status": 400
            }
        user_obj = db_session.query(models.UserModel).filter(models.UserModel.id == user_id).first()
        loan_obj = db_session.query(models.LoanModel).filter(models.LoanModel.id == loan_id).first()

        if not user_obj:
            return {
                "message": "user not found",
                "data": {},
                "status": 400
            }
        if not loan_obj:
            return {
                "message": "loan not found",
                "data": {},
                "status": 400
            }

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


@router.get("/schedule/{loan_id}")
def get_loan_schedule(loan_id: int):
    """
    builds the loan amortization schedule month by month

    :param loan_id:
    :return:
    {
    "message": "monthly loan amortization schedule created"
    "data": [
        {
            "Month": 1,
            "interest": 937.5,
            "Remaining_balance": 249670.79,
            "Monthly_payment": 1266.71
        },
        {
            "Month": 2,
            "interest": 936.26,
            "Remaining_balance": 249340.34,
            "Monthly_payment": 1266.71
        },
        {
            "Month": 3,
            "interest": 935.02,
            "Remaining_balance": 249008.65,
            "Monthly_payment": 1266.71
        },.....,
        "status": 200
    }
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

        monthly_interest_rate = (interest / 100) / 12
        numerator = monthly_interest_rate * math.pow((1 + monthly_interest_rate), term_months)
        denominator = ((math.pow(1 + monthly_interest_rate, term_months)) - 1)

        EMI_raw = amount * (numerator / denominator)
        rounded_EMI = round(EMI_raw, 2)
        rounded_EMI_cents = int(rounded_EMI * 100)

        principal_cents = int(amount * 100)
        result_list = []
        for month in range(1, term_months + 1):
            monthly_interest_amount_cents = int(monthly_interest_rate * principal_cents)
            total_cents = principal_cents + monthly_interest_amount_cents
            remaining_balance_cents = total_cents - rounded_EMI_cents
            if remaining_balance_cents < 0:
                rounded_EMI = total_cents / 100.00
                remaining_balance_cents = 0
            monthly_object = {
                "Month": month,
                "Remaining_balance": remaining_balance_cents / 100.00,
                "Monthly_payment": rounded_EMI
            }
            result_list.append(monthly_object)
            principal_cents = remaining_balance_cents

        return {
            "message": "monthly loan amortization schedule created",
            "data": result_list,
            "status": 200
        }

    except Exception as e:
        return {e}
    finally:
        db_session.close()

@router.get("/summary/{loan_id}/month/{month_val}")
def get_loan_summary(loan_id: int, month_val: int):
    """
    creates a loan summary up to the specified month not inclusive
    :param loan_id:
    :param month_val:
    :return: {
    "data": {
        "Current_Principal": 246992.25,
        "Aggregate Amount of interest paid": 8392.64,
        "Aggregate AMount of principal paid": 3007.75
    },
    "status": 200
}
    """

    if not loan_id or not month_val:
        return {
            "message": "invalid request",
            "data": {},
            "status": 400
        }
    if month_val > 360:
        return {
            "message": "invalid month please send a month value <= 360",
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
        for month in range(1, month_val+1):
            monthly_interest_amount_cents = int(monthly_interest_rate * principal_cents)
            aggregate_amount_interest_paid += monthly_interest_amount_cents
            total_cents = principal_cents + monthly_interest_amount_cents
            remaining_balance_cents = total_cents - rounded_EMI_cents
            if remaining_balance_cents < 0:
                rounded_EMI = total_cents / 100.00
                remaining_balance_cents = 0
            principal_cents = remaining_balance_cents
        aggregate_amount_principal_paid = ((amount * 100) - principal_cents) / 100.00

        return {
            "message": "summary as of end of month " + str(month_val),
            "data": {
                "Current_Principal": principal_cents / 100.00,
                "Aggregate Amount of interest paid": aggregate_amount_interest_paid / 100.00,
                "Aggregate Amount of principal paid": aggregate_amount_principal_paid
            },
            "status": 200
        }

    except Exception as e:
        return {e}
    finally:
        db_session.close()
