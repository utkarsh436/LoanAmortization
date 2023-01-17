import re
import models

def check_email(email):
    """
    Validate email address
    """
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # pass the regular expression
    # and the string into the fullmatch() method
    if (re.fullmatch(regex, email)):
        return True
    else:
        return False


def check_loan_details(loan_amount, loan_interest, loan_months):
    """
    loan amount has to be an integer value
    loan interest has to be a float value
    loan months has to be an integer value and can not be greater than 360 months (30 years)
    """
    if not isinstance(loan_amount, int):
        return False
    if not isinstance(loan_interest, float):
        return False
    if not isinstance(loan_months, int) or loan_months > 360:
        return False

    return True


def check_user_details(user_ids, owner, db_session):
    """
    validate user details
    :param user_ids: []
    :param owner: user id
    :param db_session: SessionLocal()
    :return: boolean
    """
    if not isinstance(owner, int):
        return False
    for id in user_ids:
        if not isinstance(id, int):
            return False
        user_obj = db_session.query(models.UserModel).filter(models.UserModel.id == id).first()
        if not user_obj:
            return False
    return True