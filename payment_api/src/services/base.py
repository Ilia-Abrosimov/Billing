from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, session: AsyncSession):
        self.session = session
