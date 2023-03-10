from sqlalchemy import Column, ForeignKey, Integer, String, Table, Float
from sqlalchemy.orm import relationship

from database import Base


association_table = Table(
    'user_loans',
    Base.metadata,
    Column('user_id', Integer, ForeignKey("users.id")),
    Column('loan_id', Integer, ForeignKey("loans.id"))
)

class UserModel(Base):
    __tablename__ = "users"

    id = Column('id', Integer, primary_key=True, index=True, unique=True)
    email = Column('email', String, unique=True, index=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)

    loans = relationship('LoanModel', secondary=association_table, back_populates='users')

class LoanModel(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    term_months = Column(Integer)
    owner_user_id = Column(Integer)
    interest = Column(Float)

    users = relationship('UserModel', secondary=association_table, back_populates='loans')
