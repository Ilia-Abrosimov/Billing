from uuid import UUID

from apiflask import Schema, fields as af_fields, PaginationSchema
from apiflask.validators import Length, Email, Range
from marshmallow import fields as mm_fields
from pydantic import BaseModel


class UUIDSchema(BaseModel):
    role_id: UUID


class RoleOut(Schema):
    id = af_fields.UUID()
    name = af_fields.String()
    description = af_fields.String()


class RoleIn(Schema):
    name = af_fields.String(required=True)
    description = af_fields.String(required=False)


class UserIn(Schema):
    email = mm_fields.Email()
    password = af_fields.String()


class UserOut(Schema):
    id = af_fields.UUID()
    email = mm_fields.Email()


class AuthOut(Schema):
    user_agent = af_fields.String()
    updated_at = mm_fields.DateTime()


class AuthHistoryOut(Schema):
    items = af_fields.List(af_fields.Nested(AuthOut))
    pagination = af_fields.Nested(PaginationSchema)


class RoleName(Schema):
    name = af_fields.String(required=True)
    date = af_fields.String(required=True)


class LoginInfo(Schema):
    """Модель для информации, которую Юзер передает при авторизации"""
    email = af_fields.Email(required=True,
                            validate=Email(error="Переданная информация не является правильным емэйлом"))
    password = af_fields.String(required=True, validate=Length(min=8))


class AuthHistoryQuery(Schema):
    page = af_fields.Integer(load_default=1)
    per_page = af_fields.Integer(load_default=20, validate=Range(max=100))


class Token(Schema):
    message = af_fields.String()
    access_token = af_fields.String()
    refresh_token = af_fields.String()
