from fastapi.testclient import TestClient
from main import app
import random
import string

client = TestClient(app)
def create_user_helper():
    letters = string.ascii_lowercase
    email = ''.join(random.choice(letters) for i in range(10)) + '@gmail.com'

    response = client.post("/users", json={
        "email": email,
        "first_name": "kajhsd",
        "last_name": "ajkshd"
    })
    return response, email


def create_loan_helper(user_ids, owner_user_id):
    response = client.post("/loans", json={
        "loan_detail": {
            "amount": 250000,
            "interest": 4.5,
            "months": 360
        },
        "user_detail": {
            "user_ids": user_ids,
            "owner_user_id": owner_user_id
        }
    })
    return response
