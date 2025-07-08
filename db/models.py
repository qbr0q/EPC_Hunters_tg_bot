# -*- coding: utf-8 -*-
from sqlmodel import SQLModel, create_engine, Field
from datetime import datetime


class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    # timestamp: datetime
    # request_type: str
    # prompt: str | None
    # template_id: int | None
    # tokens_used: int
    is_admin: bool


class Templates(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    prompt: str


engine = create_engine("sqlite:///db/db.sqlite3")
SQLModel.metadata.create_all(engine)
