import models
from fastapi import FastAPI
from database import engine

from routers import users, loans

app = FastAPI()
app.include_router(users.router)
app.include_router(loans.router)
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def homepage():
    return {
        "Welcome to loan amortization app"
}