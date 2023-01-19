from fastapi import HTTPException

import models

from database import SessionLocal
from utils import calculate_emi


class DataService:
    """
    provides separate methods to access the database to retrieve data
    """

    def __init__(self, model):
        self._model = model

    def write_user(self, email, first_name, last_name):
        """
        creates a new user entry into users table after validating user does not already exist based on email
        :param email:
        :param first_name:
        :param last_name:
        :return:
        """
        db_session = SessionLocal()

        try:
            # check if user already exists if so then return user object
            user_obj = db_session.query(self._model).filter(self._model.email == email).first()
            if user_obj:
                raise HTTPException(status_code=400, detail="user already exists")
            user_model = self._model(email=email, first_name=first_name, last_name=last_name)
            db_session.add(user_model)
            db_session.commit()
            db_session.refresh(user_model)

            return {
                "data": user_model
            }
        except Exception as e:
            raise e
        finally:
            db_session.close()

    def get_user(self, user_id):
        """
        retrieves a specific user based on user_id
        :param user_id:
        :return:
        """
        db_session = SessionLocal()
        try:
            result = db_session.query(self._model).filter(self._model.id == user_id).first()
            if not result:
                raise HTTPException(status_code=404, detail="no user object found for given user id")
            return {
                "message": "user found",
                "data": {result},
                "status": 200
            }
        except Exception as e:
            raise e
        finally:
            db_session.close()

    def get_all_users(self):
        """
        retrieves all users within the db
        :return:
        """
        db_session = SessionLocal()
        try:
            result = db_session.query(self._model).all()
            if not result:
                return {
                    "message": "no users",
                    "data": {},
                    "status": 200
                }
            return {
                "message": "all users",
                "data": result,
                "status": 200
            }
        except Exception as e:
            raise e
        finally:
            db_session.close()

    def create_loan(self, user_ids, loan_amount, loan_interest, loan_months, owner_user_id):
        """
        creates a loan entry in the loan table with the given params
        :param user_ids:
        :param loan_amount:
        :param loan_interest:
        :param loan_months:
        :param owner_user_id:
        :return:
        """
        db_session = SessionLocal()
        try:
            loan_model = self._model(amount=loan_amount, interest=loan_interest, term_months=loan_months,
                                     owner_user_id=owner_user_id)
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
                    "owner_user_id": loan_model.owner_user_id
                },
                "status": 200
            }
        except Exception as e:
            raise e
        finally:
            db_session.close()

    def get_loan(self, loan_id):
        """
        gets a single loan object based on loan id from the database
        :param loan_id:
        :return:
        """
        db_session = SessionLocal()
        try:
            result = db_session.query(self._model).filter(self._model.id == loan_id).first()
            result.users
            if not result:
                raise HTTPException(status_code=400, detail="no loan found")
            return {
                "message": "loan found",
                "data": {
                    "loan_details": result
                },
                "status": 200
            }
        except Exception as e:
            raise e
        finally:
            db_session.close()

    def get_user_loans(self, user_id):
        """
        gets all loans associated to a user
        :param user_id:
        :return:
        """
        db_session = SessionLocal()
        try:
            user_obj = db_session.query(models.UserModel).filter(models.UserModel.id == user_id).first()
            if not user_obj:
                raise HTTPException(status_code=404, detail="no user object found for given user id")
            res_arr = user_obj.loans
            if res_arr:
                return {
                    "message": "loans found",
                    "loans": res_arr,
                    "status": 200
                }
            else:
                raise HTTPException(status_code=404, detail="no loans for given user_id")
        except Exception as e:
            raise e
        finally:
            db_session.close()

    def share_loan(self, user_id, loan_id):
        """
        shares the loan for a specified user and loan by creating an association between them
        :param user_id:
        :param loan_id:
        :return:
        """
        db_session = SessionLocal()
        try:
            loan_obj = db_session.query(self._model).filter(self._model.id == loan_id).first()
            user_obj = db_session.query(models.UserModel).filter(models.UserModel.id == user_id).first()

            if not user_obj:
                raise HTTPException(status_code=404, detail="user not found")
            if not loan_obj:
                raise HTTPException(status_code=404, detail="loan not found")
            user_obj.loans.append(loan_obj)

            return {
                "message": "loan shared",
                "data": {
                    "loan_id": loan_obj.id
                },
                "status": 200
            }

        except Exception as e:
            raise e
        finally:
            db_session.close()

    def get_loan_schedule(self, loan_id):
        """
        retriences the loan object if it exists and creates a amortization schedule
        :param loan_id:
        :return:
        """
        db_session = SessionLocal()
        try:
            loan_obj = db_session.query(self._model).filter(self._model.id == loan_id).first()
            if not loan_obj:
                raise HTTPException(status_code=404, detail="loan not found")
            amount = loan_obj.amount
            term_months = loan_obj.term_months
            interest = loan_obj.interest

            emi_result = calculate_emi(amount, term_months, interest)
            emi_raw = emi_result.get("EMI_raw")
            monthly_interest_rate = emi_result.get("monthly_interest_rate")

            rounded_emi = round(emi_raw, 2)
            rounded_emi_cents = int(rounded_emi * 100)

            principal_cents = int(amount * 100)
            result_list = []
            for month in range(1, term_months + 1):
                monthly_interest_amount_cents = int(monthly_interest_rate * principal_cents)
                total_cents = principal_cents + monthly_interest_amount_cents
                remaining_balance_cents = total_cents - rounded_emi_cents
                if remaining_balance_cents < 0:
                    rounded_emi = total_cents / 100.00
                    remaining_balance_cents = 0
                monthly_object = {
                    "Month": month,
                    "Remaining_balance": remaining_balance_cents / 100.00,
                    "Monthly_payment": rounded_emi
                }
                result_list.append(monthly_object)
                principal_cents = remaining_balance_cents

            return {
                "message": "monthly loan amortization schedule created",
                "data": result_list,
                "status": 200
            }

        except Exception as e:
            raise ev
        finally:
            db_session.close()

    def get_loan_summary(self, loan_id, month_val):
        """
         calculates the end of month loan summary for an existing loan
        :param loan_id:
        :param month_val:
        :return:
        """

        db_session = SessionLocal()
        try:
            loan_obj = db_session.query(self._model).filter(self._model.id == loan_id).first()

            if not loan_obj:
                raise HTTPException(status_code=404, detail="loan not found")
            term_months = loan_obj.term_months
            amount = loan_obj.amount
            interest = loan_obj.interest

            emi_result = calculate_emi(amount, term_months, interest)
            emi_raw = emi_result.get("EMI_raw")
            monthly_interest_rate = emi_result.get("monthly_interest_rate")

            rounded_emi = round(emi_raw, 2)
            rounded_emi_cents = int(rounded_emi * 100)

            principal_cents = int(amount * 100)

            aggregate_amount_interest_paid = 0
            for month in range(1, month_val + 1):
                monthly_interest_amount_cents = int(monthly_interest_rate * principal_cents)
                aggregate_amount_interest_paid += monthly_interest_amount_cents
                total_cents = principal_cents + monthly_interest_amount_cents
                remaining_balance_cents = total_cents - rounded_emi_cents
                if remaining_balance_cents < 0:
                    rounded_emi = total_cents / 100.00
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
            raise e
        finally:
            db_session.close()
