from fastapi.testclient import TestClient
from main import app
import unittest
from utils_helper import create_user_helper, create_loan_helper

client = TestClient(app)
class LoansRoutesTests(unittest.TestCase):
    def test_create_loan_success(self):
        user_response, user_email = create_user_helper()
        user_id = user_response.json().get("data").get("id")
        loan_create_response = create_loan_helper([user_id], user_id)
        assert loan_create_response.json().get("message") == "loan created"
    def test_create_loan_fail_missing_payload(self):
        response = client.post("/loans", json={})
        assert response.json().get("detail") == "invalid payload"
        assert response.status_code == 400
    def test_create_loan_fail_missing_loan_details(self):
        response = client.post("/loans", json={
        "user_detail": {
            "user_ids": 1,
            "owner_user_id": 1
        }
    })
        assert response.json().get("detail") == "invalid payload"
        assert response.status_code == 400
    def test_create_loan_fail_missing_user_details(self):
        response = client.post("/loans", json={
        "loan_detail": {
            "amount": 250000,
            "interest": 4.5,
            "months": 360
        }
    })
        assert response.json().get("detail") == "invalid payload"
        assert response.status_code == 400

    def test_create_loan_fail_missing_loan_amount(self):
        response = client.post("/loans", json={
        "loan_detail": {
            "interest": 4.5,
            "months": 360
        },
        "user_detail": {
            "user_ids": 1,
            "owner_user_id": 1
        }
    })
        assert response.json().get("detail") == "missing loan details"
        assert response.status_code == 400
    def test_create_loan_fail_missing_loan_interest(self):
        response = client.post("/loans", json={
        "loan_detail": {
            "amount": 2400000,
            "months": 360
        },
        "user_detail": {
            "user_ids": 1,
            "owner_user_id": 1
        }
    })
        assert response.json().get("detail") == "missing loan details"
        assert response.status_code == 400
    def test_create_loan_fail_missing_loan_interest_months(self):
        response = client.post("/loans", json={
        "loan_detail": {
            "amount": 2400000,
            "interest": 4.5
        },
        "user_detail": {
            "user_ids": 1,
            "owner_user_id": 1
        }
    })
        assert response.json().get("detail") == "missing loan details"
        assert response.status_code == 400

    def test_create_loan_fail_missing_user_ids(self):
        response = client.post("/loans", json={
            "loan_detail": {
                "amount": 250000,
                "interest": 4.5,
                "months": 360
            },
            "user_detail": {
                "owner_user_id": 1
            }
        })
        assert response.json().get("detail") == "missing user id details"
        assert response.status_code == 400
    def test_create_loan_fail_missing_user_ids_empty_list(self):
        response = client.post("/loans", json={
            "loan_detail": {
                "amount": 250000,
                "interest": 4.5,
                "months": 360
            },
            "user_detail": {
                "user_ids": [],
                "owner_user_id": 1
            }
        })
        assert response.json().get("detail") == "missing user id details"
        assert response.status_code == 400
    def test_create_loan_fail_missing_owner_user_id(self):
        response = client.post("/loans", json={
            "loan_detail": {
                "amount": 250000,
                "interest": 4.5,
                "months": 360
            },
            "user_detail": {
                "user_ids": [1],
            }
        })
        assert response.json().get("detail") == "missing user id details"
        assert response.status_code == 400

    def test_create_loan_fail_user_does_not_exist(self):
        response = client.post("/loans", json={
            "loan_detail": {
                "amount": 250000,
                "interest": 4.5,
                "months": 360
            },
            "user_detail": {
                "user_ids": [500],
                "owner_user_id": 500
            }
        })
        assert response.json().get("detail") == "no user object found for given user id"
        assert response.status_code == 404

    def test_get_loan(self):
        user_response, user_email = create_user_helper()
        user_id = user_response.json().get("data").get("id")
        loan_create_response = create_loan_helper([user_id], user_id)
        loan_id = loan_create_response.json().get("data").get("id")
        url = """/loans/{}""".format(loan_id)
        response = client.get(url)
        assert response.json().get("message") == "loan found"

    def test_share_loan(self):
        user_response1, user_email1 = create_user_helper()
        user_id1 = user_response1.json().get("data").get("id")

        loan_create_response = create_loan_helper([user_id1], user_id1)
        loan_id = loan_create_response.json().get("data").get("id")

        user_response2, user_email2 = create_user_helper()
        user_id2 = user_response2.json().get("data").get("id")

        response = client.post("/loans/share", json={
            "user_id": user_id2,
            "loan_id": loan_id
        })
        assert response.json().get("message") == "loan shared"

    def test_get_loan_schedule(self):
        user_response, user_email = create_user_helper()
        user_id = user_response.json().get("data").get("id")
        loan_create_response = create_loan_helper([user_id], user_id)
        loan_id = loan_create_response.json().get("data").get("id")
        response = client.get("/loans/schedule/{}".format(loan_id))

        loan_month = loan_create_response.json().get("data").get("term_months")
        last_month_obj = response.json().get("data")[loan_month-1]

        assert response.json().get("message") == "monthly loan amortization schedule created"
        assert last_month_obj.get("Month") == loan_month
        assert last_month_obj.get("Remaining_balance") == 0

    def test_get_loan_summary(self):
        user_response, user_email = create_user_helper()
        user_id = user_response.json().get("data").get("id")
        loan_create_response = create_loan_helper([user_id], user_id)
        loan_id = loan_create_response.json().get("data").get("id")
        response = client.get("/loans/summary/{}/month/{}".format(loan_id, 10))
        assert response.status_code == 200
        assert response.json().get("message") == 'summary as of end of month 10'


if __name__ == '__main__':
    unittest.main()
