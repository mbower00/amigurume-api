# using code from:
# - https://www.youtube.com/watch?v=aX-ayOb_Aho

from src.amigurume_api.db import User, db
from sqlalchemy import select, update
from src.amigurume_api.utils import package_result
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token


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
    
    def sign_up_user(self):
        data = request.get_json()

        # clean and validate data
        try:
            data["email"] = data["email"].strip()
            data["password"] = data["password"].strip()
            data["username"] = data["username"].strip()
        except KeyError:
            return {'message': 'Must provide username, password, and email'}, 400
        except AttributeError:
            return {'message': 'username, password, and email must be strings'}, 400

        # hash the password
        data['password'] = generate_password_hash(data['password'])

        with db.session() as session:
            # ensure the user is new
            find_user_result = session.execute(
                select(User)
                .where(User.username == data['username'])
            ).first()
            if find_user_result:
                return {'message': f'Username: {data["username"]} is taken'}, 400

            # create the new user
            user = User(username = data['username'], 
                        password = data['password'], 
                        email = data['email'],
                        clearance = 'user')
            session.add(user)
            session.commit()
            # TODO: return jwt
            return {'id': user.id, 'username': user.username, 'email': user.email}
    
    def log_in_user(self):
        data = request.get_json()

        # clean and validate data
        try:
            data["password"] = data["password"].strip()
            data["username"] = data["username"].strip()
        except KeyError:
            return {'message': 'Must provide username and password'}, 400
        except AttributeError:
            return {'message': 'username and password must be strings'}, 400
        
        # get the user
        with db.session() as session:
            find_user_result = session.execute(
                select(User)
                .where(User.username == data['username'])
            ).first()
            if not find_user_result:
                return {'message': f'No user with username: {data["username"]}'}, 400
            user = package_result(find_user_result)

        # check password
        if not check_password_hash(user['password'], data['password']):
            return {'message': 'Incorrect password'}, 400 

        return 'done'