from datetime import datetime

from flask import current_app
from sqlalchemy import or_
from src.core.utils import useragent_device_parser
from src.db.pg_db import db
from src.models.models import AuthHistory, Role, User, UsersRoles


def create_user_in_db(**kwargs):
    user = User(**kwargs)
    db.session.add(user)
    db.session.commit()
    guest_role = Role.query.filter_by(name='guest').first()
    add_role_to_user(user, guest_role)
    return user


def update_user_in_db(user, **kwargs):
    for key, value in kwargs.items():
        setattr(user, key, value)
    db.session.commit()
    return user


def get_user_or_404(**kwargs):
    return User.query.filter_by(**kwargs).first_or_404()


def get_user(**kwargs):
    return User.query.filter_by(**kwargs).first()


def update_history(user_agent, user_id):
    history = AuthHistory.query.filter_by(user_id=user_id, user_agent=user_agent).first()
    if not history:
        history = AuthHistory(user_id=user_id, user_agent=user_agent)
    history.updated_at = datetime.utcnow()
    ua = useragent_device_parser(user_agent)
    history.user_device_type = ua
    db.session.add(history)
    db.session.commit()


def get_auth_history_by_user_id(user_id, page, per_page):
    return AuthHistory.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)


def add_role_to_user(user, role, date=None):
    if role not in user.roles:
        # user.roles.append(role)
        if date is not None:
            user_role = UsersRoles(user_id=user.id, role_id=role.id, expired_at=datetime.strptime(date, '%Y-%m-%d'))
        else:
            user_role = UsersRoles(user_id=user.id, role_id=role.id)
        # db.session.commit()
        db.session.add(user_role)
        db.session.commit()
        return True
    return False


def remove_role_from_user(user, role):
    if role in user.roles:
        user.roles.remove(role)
        db.session.commit()
        return True
    return False


def get_actual_user_roles(user):
    user_roles = [role.name for role in user.roles]
    if current_app.config['SUPERUSER_ROLE_NAME'] in user_roles:
        return user.roles
    user_roles = db.session.query(UsersRoles.id,
                                  Role.name).filter(UsersRoles.user_id == user.id).filter(or_(UsersRoles.expired_at >= datetime.utcnow(),
                                                                                              UsersRoles.expired_at == None)).outerjoin(Role)
    return user_roles
