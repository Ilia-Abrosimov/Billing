from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, AnyUrl


class UserOut(BaseModel):
    id: UUID
    email: EmailStr


class RoleOut(BaseModel):
    id: UUID
    name: str
    description: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    message: str


class Auth(BaseModel):
    updated_at: datetime
    user_agent: str


class Paginator(BaseModel):
    current: AnyUrl
    first: AnyUrl
    last: AnyUrl
    next: AnyUrl | str
    page: int
    pages: int
    per_page: int
    prev: AnyUrl | str
    total: int


class AuthHistory(BaseModel):
    items: list[Auth]
    pagination: Paginator
