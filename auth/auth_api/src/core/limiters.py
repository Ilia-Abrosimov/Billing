from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.core.config import api_settings


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[api_settings.limiter_config],
    storage_uri="memory://",
)
