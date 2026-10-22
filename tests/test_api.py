import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import PostModel


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        db.execute(delete(PostModel))
        db.commit()

    with TestClient(app) as test_client:
        yield test_client

    with SessionLocal() as db:
        db.execute(delete(PostModel))
        db.commit()


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_post(client):
    response = client.post(
        "/api/v1/posts",
        json={
            "username": "akmal",
            "content": "My first SocialHub post",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "akmal"
    assert response.json()["content"] == "My first SocialHub post"
    assert "id" in response.json()


def test_list_posts(client):
    client.post(
        "/api/v1/posts",
        json={
            "username": "akmal",
            "content": "Hello SocialHub",
        },
    )

    response = client.get("/api/v1/posts")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_missing_post_returns_404(client):
    response = client.get("/api/v1/posts/999999")

    assert response.status_code == 404


def test_empty_content_is_rejected(client):
    response = client.post(
        "/api/v1/posts",
        json={
            "username": "akmal",
            "content": "",
        },
    )

    assert response.status_code == 422


def test_delete_post(client):
    created = client.post(
        "/api/v1/posts",
        json={
            "username": "akmal",
            "content": "This post will be deleted",
        },
    )
    post_id = created.json()["id"]

    response = client.delete(f"/api/v1/posts/{post_id}")

    assert response.status_code == 204
    assert client.get(f"/api/v1/posts/{post_id}").status_code == 404
