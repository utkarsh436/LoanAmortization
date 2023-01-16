from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)

class Loan(Base):
    __tablename__ = "loan"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(String, unique=True, index=True)
    loan_terms_months = Column(String)

# class user_loans(Base):
#     __tablename__ = "user_loans"
#
#     id = Column(Integer, primary_key=True, index=True)
#     owner = Column(Integer)
#     user_id = Column(Integer, ForeignKey("users.id"))
#
#
#     # loan_id = relationship()
