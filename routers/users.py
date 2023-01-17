from fastapi import APIRouter, Request

import models
from database import SessionLocal
from utils import check_email

router = APIRouter(prefix="/users")

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
        "password": "password"
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
    db_session = SessionLocal()
    if not payload:
        return {
            "message": "invalid payload",
            "data": {},
            "status": 404
        }
    try:
        email = payload.get("email")
        password = payload.get("password")
        first_name = payload.get("first_name")
        last_name = payload.get("last_name")

        if not email or not password or not first_name or not last_name:
            raise Exception("missing parameters")
        if not check_email(email):
            raise Exception("invalid email address")

        # check if user already exists if so then return user object
        user_obj = db_session.query(models.UserModel).filter(models.UserModel.email == email).first()
        if user_obj:
            return {
                "message": "user already exists",
                "data": {
                    user_obj
                },
                "status": 400
            }

        user_model = models.UserModel(email=email, hashed_password=password, first_name=first_name, last_name=last_name)
        db_session.add(user_model)
        db_session.commit()
        db_session.refresh(user_model)

        return {
            "data": user_model
        }
    except Exception as e:
        return {
            "message": str(e),
            "data": {},
            "status": 400
        }
    finally:
        db_session.close()
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
            "message": "user found",
            "data": {result},
            "status": 200
        }
    except Exception as e:
        return {e}
    finally:
        db_session.close()
