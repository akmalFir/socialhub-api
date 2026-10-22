from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import PostModel
from app.schemas import PostCreate, PostResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SocialHub API",
    description="A minimal social media API for a DevOps portfolio.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "name": "SocialHub API",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post(
    "/api/v1/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
):
    post = PostModel(**payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@app.get("/api/v1/posts", response_model=list[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    statement = select(PostModel).order_by(PostModel.id.desc())
    return list(db.scalars(statement).all())


@app.get("/api/v1/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = db.get(PostModel, post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@app.delete(
    "/api/v1/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = db.get(PostModel, post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
