from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from bs4 import BeautifulSoup

from .error import Error
from .user import UserInformation


class ExerciseXml(BaseModel):
    content: str = Field(...)
    uuid: str = Field(None)
    title: Optional[str] = Field(None)
    is_random: Optional[bool] = Field(None, alias="isRandom")
    is_interactive: Optional[bool] = Field(None, alias="isInteractive")
    exercise_id: Optional[int] = Field(None, alias="stepRevId")
    soup: Optional[BeautifulSoup] = None

    class Config:
        arbitrary_types_allowed = True


class TitleClass(BaseModel):
    title: str


class MetaClass(BaseModel):
    uuids: List[str] = Field(..., alias="stepUuids")
    subject: TitleClass = Field(...)
    teacher: UserInformation = Field(...)
    steps_meta: Dict[str, TitleClass] = Field(..., alias="stepsMeta")


class ExerciseMeta(BaseModel):
    errors: List[Error] = Field(list())
    success: bool = Field(True)
    meta: Optional[MetaClass] = Field(None)
