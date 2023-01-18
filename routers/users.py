from fastapi import APIRouter, Request

import models
from DataService.data_service import DataService
from database import SessionLocal
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
        return {e}

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
        return {
            "message": "invalid payload",
            "data": {},
            "status": 404
        }
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
        return e
@router.get("/{user_id}")
async def get_user(user_id: int):
    """
    Gets the user information for a specific user based on the id
    :param user_id:
    :return: user object
    """
    if not user_id:
        return {
            "message": "no user id passed",
            "data": {},
            "status": 404
        }

    try:
        data_service = DataService(models.UserModel)
        result = data_service.get_user(user_id=user_id)
        return result
    except Exception as e:
        return {e}
