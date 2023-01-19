from fastapi.testclient import TestClient
from main import app
import unittest
from utils_helper import create_user_helper, create_loan_helper

client = TestClient(app)
class UsersRoutesTests(unittest.TestCase):
    def test_homepage(self):
        response = client.get("/")
        assert response.status_code == 200
    def test_create_user_success(self):
        response, email = create_user_helper()
        assert response.json().get("data").get("email") == email

    def test_create_user_exists_fail(self):
        response1, email1 = create_user_helper()
        assert response1.json().get("data").get("email") == email1

        response = client.post("/users", json={
            "email": email1,
            "first_name": "kajhsd",
            "last_name": "ajkshd"
        })
        assert response.json().get("message") == "user already exists"

    def test_get_user_by_id_success(self):
        response, email = create_user_helper()
        assert response.json().get("data").get("email") == email

        id = response.json().get("data").get("id")
        url = """/users/{}""".format(id)
        response = client.get(url)
        assert response.json().get("message") == "user found"

    def test_get_user_by_email_success(self):
        response, email = create_user_helper()
        assert response.json().get("data").get("email") == email

        email = response.json().get("data").get("email")
        url = """/users?email={}""".format(email)
        response = client.get(url)
        assert response.json().get("message") == "user found"

    def test_get_user_fail(self):
        response = client.get("/users/500")
        assert response.json().get("detail") == "no user object found for given user id"
    def test_get_all_users(self):
        create_user_helper()
        create_user_helper()
        response = client.get("/users")
        length = len(response.json())
        assert length > 0
    def test_get_loans_users(self):
        response, email = create_user_helper()
        user_id = response.json().get("data").get("id")
        loan_create_response = create_loan_helper([user_id], user_id)
        assert loan_create_response.json().get("message") == "loan created"
        url = """users/{}/loans""".format(user_id)
        user_loans_repsonse = client.get(url)
        loans_arr = user_loans_repsonse.json().get("loans")
        assert len(loans_arr) > 0


if __name__ == '__main__':
    unittest.main()
