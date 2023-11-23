import json
import logging
from typing import Dict, Optional, Self

import user_agent
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from src.skysmart.models.user import LoginPasswordPair, UserInformation
from src.skysmart.models.xml import ExerciseMeta, ExerciseXml

from .constants import INFORMATION, LOGIN_REQUEST, PREVIEW, XML

logger = logging.getLogger(__name__)


class SkySmartSession:
    def __init__(self, client: Optional[ClientSession] = None):
        self.access_token: Optional[str] = None
        self.client = client or ClientSession()

    @classmethod
    async def from_pair(cls, pair: LoginPasswordPair) -> Self:
        session = cls()
        await session.authenticate(pair)
        return session

    @staticmethod
    def _cleanup(text: str) -> str:
        while "\n\n" in text:
            text = text.replace("\n\n", "\n")
        return text.strip()

    @staticmethod
    def _get_headers(content_type: Optional[str] = None) -> Dict[str, str]:
        return {
            "Content-Type": content_type or "application/json",
            "Accept": "application/json; charset=UTF-8",
            "User-Agent": user_agent.generate_user_agent(),
        }

    def _get_headers_with_token(
        self, content_type: Optional[str] = None
    ) -> Dict[str, str]:
        return {
            "Content-Type": content_type or "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
        }

    def _is_check_errors(self, response: Dict):
        pass  # TODO

    def is_token(self) -> bool:
        return self.access_token is not None

    def reset_access_token(self, access_token: str):
        self.access_token = access_token

    async def authenticate(self, pair: LoginPasswordPair) -> Optional[str]:
        """
        Authenticate(reset) and get access token
        :param pair: bind login and password
        :return: jwt token for future requests
        """
        self.access_token = await self.get_access_token(pair)
        logger.debug(f"The value of access_token: {self.access_token}")
        return self.access_token

    async def get_access_token(self, pair: LoginPasswordPair) -> Optional[str]:
        """
        Get access token from SkySmartSession
        :param pair: bind login and password
        :return: access token
        """
        async with self.client.request(
            method="POST",
            url=LOGIN_REQUEST,
            data=pair.model_dump_json(by_alias=True),
            headers={"User-Agent": user_agent.generate_user_agent()},
        ) as response:
            response: dict = await response.json()
            logger.debug(f"Sent a request, and got the response: {response}")
            return response.get("jwtToken")

    async def get_information(self) -> UserInformation:
        """
        Get information about user
        :return: information about teacher/student
        """
        async with self.client.request(
            method="POST", url=INFORMATION, headers=self._get_headers_with_token()
        ) as response:
            response = await response.json()
            logger.debug(f"Sent a request, and got the response: {response}")
            return UserInformation(**response)

    async def get_answer_xml_uuids(self, task: str) -> ExerciseMeta:
        """
        Get answer XML uuids from task
        :return: answers $$$$
        """
        async with self.client.request(
            method="POST",
            url=PREVIEW,
            headers=self._get_headers_with_token(),
            data=json.dumps({"taskHash": task}),
        ) as response:
            response = await response.json()
            logger.debug(f"Sent a request, and got the response: {response}")
            return ExerciseMeta(**response)

    async def get_answer_xml(self, uuid: str, exercise: ExerciseMeta) -> ExerciseXml:
        """
        Get answer from meta and uuid
        :return: xml
        """
        async with self.client.request(
            method="GET",
            url=XML + uuid,
            headers=self._get_headers_with_token("plain/text"),
        ) as response:
            response = await response.json()
            logger.debug(f"Sent a request (XML), and got the response: {response}")
            response = ExerciseXml(**response)
            content = self._cleanup(response.content)
            response.soup = BeautifulSoup(content, "lxml")
            response.title = exercise.meta.steps_meta[uuid].title
            response.uuid = uuid
            return response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
