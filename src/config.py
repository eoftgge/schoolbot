from abc import ABC, abstractmethod
from configparser import ConfigParser

from .skysmart.models.user import LoginPasswordPair


class AbstractConfig(ABC):
    def __init__(self, config_parser: ConfigParser, config_path: str):
        self._config_parser = config_parser
        self._config_path = config_path

    def get_config_path(self) -> str:
        return self._config_path

    @abstractmethod
    def get_path(self) -> str:
        ...


class UserConfig(AbstractConfig):
    def get_path(self) -> str:
        return "user.config"

    @property
    def login(self) -> str:
        return self._config_parser.get(self.get_path(), "login")

    @property
    def password(self) -> str:
        return self._config_parser.get(self.get_path(), "password")

    def as_null(self):
        self._config_parser.set(self.get_path(), "login", "******")
        self._config_parser.set(self.get_path(), "password", "******")
        with open(self.get_config_path(), "w") as file:
            self._config_parser.write(file)

    def to_pair(self) -> LoginPasswordPair:
        return LoginPasswordPair(login=self.login, password=self.password)


class SkyConfig(AbstractConfig):
    def get_path(self) -> str:
        return "sky.config"


class TelegramConfig(AbstractConfig):
    def get_path(self) -> str:
        return "telegram.config"

    @property
    def token(self) -> str:
        return self._config_parser.get(self.get_path(), "token")


class GptConfig(AbstractConfig):
    def get_path(self) -> str:
        return "chat-gpt.config"

    @property
    def token(self) -> str:
        return self._config_parser.get(self.get_path(), "token")


class Config:
    def __init__(self, path: str):
        self._config_parser = ConfigParser()
        self._config_parser.read(path)
        self._config_path = path

    @property
    def telegram_config(self) -> TelegramConfig:
        return TelegramConfig(self._config_parser, self._config_path)

    @property
    def user_config(self) -> UserConfig:
        return UserConfig(self._config_parser, self._config_path)

    @property
    def sky_config(self) -> SkyConfig:
        return SkyConfig(self._config_parser, self._config_path)

    @property
    def gpt_config(self) -> GptConfig:
        return GptConfig(self._config_parser, self._config_path)


def get_path_config(path: str) -> str:
    from os import listdir

    if path in listdir(".."):
        return "../" + path
    elif path in listdir("."):
        return "./" + path

    raise FileNotFoundError(f"`{path}` isn't exists..")
