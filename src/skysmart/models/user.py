from pydantic import BaseModel, Field


class UserInformation(BaseModel):
    name: str = Field(...)
    surname: str = Field(...)


class LoginPasswordPair(BaseModel):
    login: str = Field(..., alias="phoneOrEmail")
    password: str = Field(...)
