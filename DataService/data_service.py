from database import SessionLocal


class DataService:

    def __init__(self, model):
        self._model = model

    def write_user(self, email, first_name, last_name):
        db_session = SessionLocal()

        try:
            # check if user already exists if so then return user object
            user_obj = db_session.query(self._model).filter(self._model.email == email).first()
            if user_obj:
                return {
                    "message": "user already exists",
                    "data": {
                        user_obj
                    },
                    "status": 400
                }

            user_model = self._model(email=email, first_name=first_name, last_name=last_name)
            db_session.add(user_model)
            db_session.commit()
            db_session.refresh(user_model)

            return {
                "data": user_model
            }
        except Exception as e:
            return {
                "message": str(e),
                "data": {},
                "status": 400
            }
        finally:
            db_session.close()

    def get_user(self, user_id):
        db_session = SessionLocal()
        try:
            result = db_session.query(self._model).filter(self._model.id == user_id).first()
            if not result:
                return {
                    "message": "no user found",
                    "data": {},
                    "status": 404
                }
            return {
                "message": "user found",
                "data": {result},
                "status": 200
            }
        except Exception as e:
            return {e}
        finally:
            db_session.close()

    def get_all_users(self):
        db_session = SessionLocal()
        try:
            result = db_session.query(self._model).all()
            if not result:
                return {
                    "message": "no user found",
                    "data": {},
                    "status": 404
                }
            return {
                "message": "all users",
                "data": result,
                "status": 200
            }
        except Exception as e:
            return {e}
        finally:
            db_session.close()
