from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: Optional[str] = Field(index=True)
    first_name: Optional[str]
    last_name: Optional[str]
    photo_url: Optional[str]
