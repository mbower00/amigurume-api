from sqlalchemy import select
from src.amigurume_api.db import db, User
from src.amigurume_api.utils import package_result

def check_clearance(username, allowed = ['admin']):
    with db.session() as session:
        result = session.execute(
            select(User)
            .where(User.username == username)
        ).first()
        user = package_result(result)
    return user['clearance'] in allowed