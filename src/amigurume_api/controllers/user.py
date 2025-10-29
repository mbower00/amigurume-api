from src.amigurume_api.db import User, db
from sqlalchemy import select
from src.amigurume_api.utils import package_result

class UserController:
    def __init__(self):
        pass
        
    def get_all_users(self):
        with db.session() as session:
            result = session.execute(select(User )).all()
            return package_result(result)
    
    def get_user(self, id):
        with db.session() as session:
            result = session.execute(select(User).where(User.id == id)).first()
            return package_result(result)