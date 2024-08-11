from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.sql import select
from databases import Database

DATABASE_URL = "sqlite:///./test.db"

database = Database(DATABASE_URL)
metadata = MetaData()

posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("content", String, index=True),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()

class PostIn(BaseModel):
    title: str
    content: str

class Post(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/posts", response_model=List[Post])
async def get_posts():
    query = posts.select()
    return await database.fetch_all(query)

@app.post("/posts", response_model=Post)
async def create_post(post: PostIn):
    query = posts.insert().values(title=post.title, content=post.content)
    last_record_id = await database.execute(query)
    return {**post.dict(), "id": last_record_id}

@app.get("/posts/{post_id}", response_model=Post)
async def read_post(post_id: int):
    query = posts.select().where(posts.c.id == post_id)
    post = await database.fetch_one(query)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(post_id: int, updated_post: PostIn):
    query = posts.update().where(posts.c.id == post_id).values(title=updated_post.title, content=updated_post.content)
    await database.execute(query)
    return {**updated_post.dict(), "id": post_id}

@app.delete("/posts/{post_id}", response_model=Post)
async def delete_post(post_id: int):
    query = posts.select().where(posts.c.id == post_id)
    post = await database.fetch_one(query)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    query = posts.delete().where(posts.c.id == post_id)
    await database.execute(query)
    return post
