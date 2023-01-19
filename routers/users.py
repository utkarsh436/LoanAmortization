from fastapi import APIRouter, Request, HTTPException

import models
from DataService.data_service import DataService
from utils import check_email

router = APIRouter(prefix="/users")

@router.get("/")
async def get_all_users():
    """
    gets all users in the database
    :return:
    """
    try:
        data_service = DataService(models.UserModel)
        result = data_service.get_all_users()
        return result
    except Exception as e:
        raise e

@router.post("/")
async def create_user(request: Request):
    """
    creates a user
    Required an email, password, first_name, last_name
    Sample payload:
    {
        "email": "foo@gmail.com",
        "first_name": "foo",
        "last_name": "bar",
    }
    :param request:
    :return: {
            "data": {
                "first_name": "foo",
                "email": "foo@gmail.com",
                "hashed_password": "password",
                "id": 1,
                "last_name": "bar"
            }
        }
    """
    payload = await request.json()
    if not payload:
        raise HTTPException(status_code=400, detail="invalid payload")
    try:
        email = payload.get("email")
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")

        if not email or not first_name or not last_name:
            raise Exception("missing parameters")
        if not check_email(email):
            raise Exception("invalid email address")

        data_service = DataService(models.UserModel)
        result = data_service.write_user(email=email, first_name=first_name, last_name=last_name)

        return result
    except Exception as e:
        raise e
@router.get("/{user_id}")
async def get_user(user_id: int):
    """
    Gets the user information for a specific user based on the id
    :param user_id:
    :return: user object
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="no user id passed")
    try:
        data_service = DataService(models.UserModel)
        result = data_service.get_user(user_id=user_id)
        return result
    except Exception as e:
        raise e

@router.get("/{user_id}/loans")
def get_user_loans(user_id: int):
    """
    gets all loan objects for a user
    :param user_id:
    :return: array of loan objects associated to user
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="no user id passed")
    try:
        data_service = DataService(models.UserModel)
        result = data_service.get_user_loans(user_id)
        return result
    except Exception as e:
        raise e

