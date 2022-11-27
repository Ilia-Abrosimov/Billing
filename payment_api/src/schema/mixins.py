import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default) -> str:
    """Fast json dumps."""
    return orjson.dumps(v, default=default).decode()


class OrjsonModel(BaseModel):
    """Fast json serializer."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
