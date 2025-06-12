from ninja import Schema
from datetime import datetime


class PostSchema(Schema):
    id: int
    title: str
    content: str
    created_at: datetime


class PostInSchema(Schema):
    title: str
    content: str
