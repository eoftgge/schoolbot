from typing import Optional

from pydantic import BaseModel, Field


class UserInformation(BaseModel):
    name: Optional[str] = Field(None)
    surname: Optional[str] = Field(None)


class LoginPasswordPair(BaseModel):
    login: str = Field(..., alias="email", validation_alias="login")
    password: str = Field(...)
