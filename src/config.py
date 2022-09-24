from configparser import ConfigParser
from typing import Optional
from abc import ABC, abstractmethod

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
        return LoginPasswordPair(
            phoneOrEmail=self.login,
            password=self.password
        )


class SkyConfig(AbstractConfig):
    def get_path(self) -> str:
        return "sky.config"

    @property
    def token(self) -> Optional[str]:
        return token if (token := self._config_parser.get(self.get_path(), "token")) != "" else None

    def is_token(self) -> bool:
        return self.token != ""

    def set_token(self, token: str):
        self._config_parser.set(self.get_path(), "token", token)
        with open(self.get_config_path(), "w") as file:
            self._config_parser.write(file)


class TelegramConfig(AbstractConfig):
    def get_path(self) -> str:
        return "telegram.config"

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


def get_path_config(path: str) -> str:
    from os import listdir

    if path in listdir(".."):
        return "../" + path
    elif path in listdir("."):
        return "./" + path

    raise FileNotFoundError(f"`{name}` isn't exists..")
