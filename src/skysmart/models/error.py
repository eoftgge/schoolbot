from typing import List, Optional
from pydantic import BaseModel, Field


class Error(BaseModel):
    property_path: str = Field(...)
    message: str = Field(...)
    error_code: Optional[int] = Field(None, alias="errorCode")
