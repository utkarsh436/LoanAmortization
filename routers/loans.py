from fastapi import APIRouter, Request

import models
from DataService.data_service import DataService
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
        owner_user_id = user_detail.get("owner_user_id")

        if not user_ids or len(user_ids) == 0 or not owner_user_id:
            raise Exception("missing user id details")
        if not check_user_details(user_ids, owner_user_id):
            raise Exception("invalid used detail")

        loan_data_service = DataService(models.LoanModel)
        result = loan_data_service.create_loan(user_ids=user_ids, loan_amount=loan_amount, loan_interest=loan_interest,
                                               loan_months=loan_months, owner_user_id=owner_user_id)
        return result

    except Exception as e:
        return e


@router.get("/{loan_id}")
async def get_loan(loan_id: int):
    """
    retrieves a loan object for a specified loan id
    :param loan_id:
    :return:
    "message": "loan found",
    "data": {
        "loan_details": {
            "amount": 450000.0,
            "owner_user_id": 1,
            "id": 1,
            "term_months": 360,
            "interest": 4.5,
            "users": [
                {
                    "last_name": "bar1",
                    "email": "abc@gmail.com",
                    "first_name": "foo1",
                    "id": 1
                },
                {
                    "last_name": "bar2",
                    "email": "def@gmail.com",
                    "first_name": "foo2",
                    "id": 2
                }
            ]
        }
    },
    "status": 200
}
    """
    if not loan_id:
        return {
            "message": "no loan id passed",
            "data": {},
            "status": 400
        }
    try:

        data_service = DataService(models.LoanModel)
        result = data_service.get_loan(loan_id)
        return result
    except Exception as e:
        return {e}

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
    try:
        payload = await request.json()
        user_id = payload.get('user_id')
        loan_id = payload.get('loan_id')
        if not user_id or not loan_id:
            return {
                "message": "invalid payload",
                "data": {},
                "status": 400
            }
        data_service = DataService(models.LoanModel)
        result = data_service.share_loan(user_id=user_id, loan_id=loan_id)
        return result

    except Exception as e:
        return {e}

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
    try:

        data_service = DataService(models.LoanModel)
        result = data_service.get_loan_schedule(loan_id)
        return result

    except Exception as e:
        return {e}

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
        data_service = DataService(models.LoanModel)
        result = data_service.get_loan_summary(loan_id, month_val)
        return result

    except Exception as e:
        return {e}
    finally:
        db_session.close()
