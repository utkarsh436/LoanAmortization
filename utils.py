import math
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


def calculate_emi(amount, term_months, interest):
    """
    calculates the emi or monthly payment
    :param amount:
    :param term_months:
    :param interest:
    :return:
    """
    monthly_interest_rate = (interest / 100) / 12
    numerator = monthly_interest_rate * math.pow((1 + monthly_interest_rate), term_months)
    denominator = ((math.pow(1 + monthly_interest_rate, term_months)) - 1)

    EMI_raw = amount * (numerator / denominator)
    result = {
        "EMI_raw": EMI_raw,
        "monthly_interest_rate": monthly_interest_rate
    }
    return result


def check_user_details(user_ids, owner_user_id):
    """
    validate user details and validates user exists
    :param user_ids: []
    :param owner_user_id: owners user id
    :return: boolean
    """
    from DataService.data_service import DataService
    data_service = DataService(models.UserModel)
    if not isinstance(owner_user_id, int):
        return False
    for id in user_ids:
        if not isinstance(id, int):
            return False
        user_obj = data_service.get_user(id)
        if not user_obj:
            return False
    return True
