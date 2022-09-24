from logging import getLogger

from ..config import Config
from .session import SkySmartSession

logger = getLogger(__name__)


async def create_session(config: Config) -> SkySmartSession:
    session = SkySmartSession(access_token=config.sky_config.token)
    result = await session.authenticate(pair=config.user_config.to_pair())

    if result is not None:
        config.sky_config.set_token(result)
        config.user_config.as_null()
        session.access_token = result

    return session
