from src.amigurume_api.db import User, db
from sqlalchemy import select, update
from src.amigurume_api.utils import package_result
from flask import request

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
        
    def change_user_clearance(self, id):
        clearance = "admin"
        try:
            to_user = request.args['to-user']
            if to_user != '0':
                clearance = "user"
        except KeyError:
            pass
        
        with db.session() as session:
            result = session.execute(
                update(User)
                .where(User.id == id)
                .values(clearance = clearance)
                .returning(User)
            )
            session.commit()
            if not result.all():
                return {'message': 'No user updated'}
        
        return {'message': f'User (id: {id}) clearance set to {clearance}'}
    