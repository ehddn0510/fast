from sqlalchemy import Table, Column, Integer, String
from .database import metadata

posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("content", String, index=True)
)
