from apiflask import APIBlueprint, abort
from pydantic.error_wrappers import ValidationError
import logging

from src.api.v1.schemas import RoleOut, UUIDSchema, RoleIn
from src.services import role as role_service
from src.services.jwt_service import check_role_jwt, auth
from src.core.config import api_settings

roles_route = APIBlueprint(
    name='roles',
    import_name=__name__,
    tag={"name": "Roles", "description": "CRUD для системы ролей"}
)


def validate_uuid(role_id):
    try:
        UUIDSchema(role_id=role_id)
    except ValidationError as err:
        abort(400, message='validation error', detail=err.errors())


@roles_route.get('/')
@roles_route.output(RoleOut(many=True))
@roles_route.auth_required(auth)
@check_role_jwt(api_settings.superuser_role_name)
def get_roles():
    return role_service.get_roles_from_db()


@roles_route.get('/<role_id>')
@roles_route.output(RoleOut)
@roles_route.auth_required(auth)
@check_role_jwt(api_settings.superuser_role_name)
def get_role(role_id):
    validate_uuid(role_id)
    return role_service.get_role_by_id(role_id)


@roles_route.post('/')
@roles_route.input(RoleIn)
@roles_route.output(RoleOut, status_code=201)
@roles_route.auth_required(auth)
@check_role_jwt(api_settings.superuser_role_name)
def create_role(data):
    role = role_service.get_role_by_name(data['name'])
    if role:
        abort(400, message='role already exists')

    role = role_service.create_role_in_db(data)
    return role


@roles_route.delete('/<role_id>')
@roles_route.output({}, status_code=204)
@roles_route.auth_required(auth)
@check_role_jwt(api_settings.superuser_role_name)
def delete_role(role_id):
    validate_uuid(role_id)
    role_service.delete_role_by_id(role_id)
    return ''


@roles_route.patch('/<role_id>')
@roles_route.input(RoleIn)
@roles_route.output(RoleOut)
@roles_route.auth_required(auth)
@check_role_jwt(api_settings.superuser_role_name)
def change_role(role_id, data):
    validate_uuid(role_id)
    role = role_service.change_role_by_id(data, role_id)
    return role
