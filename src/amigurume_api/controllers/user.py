# using code from:
# - https://www.youtube.com/watch?v=aX-ayOb_Aho

from src.amigurume_api.db import User, db, BlockedToken
from sqlalchemy import select, update
from src.amigurume_api.utils import package_result, get_order_by, get_direction
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from flask import make_response


class UserController:
    def __init__(self):
        pass
        
    def get_all_users(self):
        order_by = get_order_by(request, User)
        direction = get_direction(request)
        print(order_by, direction)
        print(getattr(getattr(User, order_by), direction))
        with db.session() as session:
            result = session.execute(
                    select(User)
                    .order_by(getattr(getattr(User, order_by), direction)())
                ).all()
            users = package_result(result)
        for user in users:
            del user['password']
        return users
    
    def get_user(self, id):
        with db.session() as session:
            result = session.execute(select(User).where(User.id == id)).first()
            user = package_result(result)
        if user:
            del user['password']
        return user
        
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
            
            # create tokens
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)

            return {
                'id': user.id, 
                'username': user.username, 
                'email': user.email, 
                'tokens': {
                    'access': access_token,
                    'refresh': refresh_token
                }}
    
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
        
        # create tokens
        access_token = create_access_token(identity=user['username'])
        refresh_token = create_refresh_token(identity=user['username'])
        
        res = make_response({
            'username': user['username'],
            'clearance': user['clearance'],
            'access': access_token,
            'cookie': request.cookies.get('refresh')
        })
        # using code copied from chatGPT https://chatgpt.com/c/691342fc-371c-832d-8eb1-71fcadf5972f
        res.set_cookie('refresh', refresh_token, samesite='None', secure=True, httponly=True)
        return res
    
    # using code from https://www.youtube.com/watch?v=aX-ayOb_Aho
    def refresh_user(self):
        username = get_jwt_identity()
        with db.session() as session:
            find_user_result = session.execute(
                select(User)
                .where(User.username == username)
            ).first()
            if not find_user_result:
                return {'message': f'No user for token'}, 400
            user = package_result(find_user_result)
        access_token = create_access_token(identity=username)
        return {'access': access_token, 'username': user['username'], 'clearance': user['clearance']}
    
    # using code from https://www.youtube.com/watch?v=aX-ayOb_Aho
    def log_out_user(self):
        jti = get_jwt()['jti']
        tkn_type = get_jwt()['type']
        with db.session() as session:
            blocked_token = BlockedToken(jti = jti)
            session.add(blocked_token)
            session.commit()
            return {'message': f'{tkn_type.capitalize()} token logged out'}