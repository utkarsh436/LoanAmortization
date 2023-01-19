# LOAN AMORTIZATION APP
This is a FASTAPi application builds a loan amortization schedule for loans

## USER API's
- GET /users : is a get all users can take an option paramter: ?email=foo@gmail.com to retrieve a user by the email address 
- POST /users: creates a user object 
  ````
    Sample payload:
            {
                "email": "foo@gmail.com",
                "first_name": "foo",
                "last_name": "bar",
            }
  ```` 
- GET /users/{user_id}: retrieves user information for a specific user based on the id 
- GET /users/{user_id}/loans : retrieves all the loans associated to a user

## LOAN API's

- POST /loans : creates a loan object based on payload and existing users
    ```
    sample payload 
    {
        "loan_detail": {
            "amount": 250000,
            "interest": 4.5,
            "months": 360
        },
        "user_detail": {
            "user_ids": [1,2],
            "owner_user_id" : 1
        }
    }
    ```
- GET /loans/{loan_id}: retrieves a specific loan object and the users associated to that loan
- POST /loans/share : shares an existing loan from the given loan id with the user id from the payload. Note the user and loan must already exist!
   ```
   sample payload
  
   {
        "loan_id": 1
        "user_id": 2
    }
    
   ```
GET /loans/schedule/{loan_id}: retrieves the amortization schedule for an existing loan
GET /loans/summary/{loan_id}/month/{month_val}:calculates the end of month loan summary for an existing loan


# TO RUN
- pip install -r requirements.txt
- run the ./run.sh file or execute this command: uvicorn main:app --reload
