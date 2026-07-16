import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.session import Base, get_db
from app.infrastructure.database.models import EscritoDB, UsuarioDB, ComentarioDB

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_senda.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def fixture_db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        import os
        if os.path.exists("test_senda.db"):
            try:
                os.remove("test_senda.db")
            except OSError:
                pass

@pytest.fixture(name="client")
def fixture_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(name="tokens")
def fixture_tokens(client):
    admin_login = client.post("/api/v1/auth/developer-login", json={"email": "writer@example.com", "role": "admin"})
    admin_token = admin_login.json()["access_token"]
    
    r1_login = client.post("/api/v1/auth/developer-login", json={"email": "reader1@example.com", "role": "lector"})
    r1_token = r1_login.json()["access_token"]
    
    r2_login = client.post("/api/v1/auth/developer-login", json={"email": "reader2@example.com", "role": "lector"})
    r2_token = r2_login.json()["access_token"]
    
    return {
        "admin": {"Authorization": f"Bearer {admin_token}"},
        "reader1": {"Authorization": f"Bearer {r1_token}"},
        "reader2": {"Authorization": f"Bearer {r2_token}"}
    }

def test_comment_flow(client, tokens):
    create_writing_res = client.post(
        "/api/v1/writings/",
        json={"title": "Poema de Prueba", "content": "Contenido...", "status": "publicado"},
        headers=tokens["admin"]
    )
    writing_id = create_writing_res.json()["id"]

    comment_payload = {"content": "Excelente poema, felicitaciones!", "rating": 5}
    response = client.post(
        f"/api/v1/writings/{writing_id}/comments",
        json=comment_payload,
        headers=tokens["reader1"]
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == comment_payload["content"]
    assert data["rating"] == 5
    assert data["usuario_name"] == "Dev User Lector"
    comment_id = data["id"]

    list_res = client.get(f"/api/v1/writings/{writing_id}/comments")
    assert list_res.status_code == 200
    comments = list_res.json()
    assert len(comments) == 1
    assert comments[0]["content"] == comment_payload["content"]

    del_fail_res = client.delete(f"/api/v1/comments/{comment_id}", headers=tokens["reader2"])
    assert del_fail_res.status_code == 403

    del_success_res = client.delete(f"/api/v1/comments/{comment_id}", headers=tokens["reader1"])
    assert del_success_res.status_code == 204

    list_after_del = client.get(f"/api/v1/writings/{writing_id}/comments")
    assert len(list_after_del.json()) == 0

def test_admin_moderation(client, tokens):
    create_writing_res = client.post(
        "/api/v1/writings/",
        json={"title": "Poema de Prueba", "content": "Contenido...", "status": "publicado"},
        headers=tokens["admin"]
    )
    writing_id = create_writing_res.json()["id"]

    comment_res = client.post(
        f"/api/v1/writings/{writing_id}/comments",
        json={"content": "Comentario spam", "rating": 1},
        headers=tokens["reader1"]
    )
    comment_id = comment_res.json()["id"]

    del_res = client.delete(f"/api/v1/comments/{comment_id}", headers=tokens["admin"])
    assert del_res.status_code == 204

def test_comment_cascade_on_delete_writing(client, tokens):
    create_writing_res = client.post(
        "/api/v1/writings/",
        json={"title": "Poema Efimero", "content": "Contenido...", "status": "publicado"},
        headers=tokens["admin"]
    )
    writing_id = create_writing_res.json()["id"]

    client.post(
        f"/api/v1/writings/{writing_id}/comments",
        json={"content": "Lindo!"},
        headers=tokens["reader1"]
    )

    del_writing_res = client.delete(f"/api/v1/writings/{writing_id}", headers=tokens["admin"])
    assert del_writing_res.status_code == 204

    list_res = client.get(f"/api/v1/writings/{writing_id}/comments")
    assert list_res.status_code == 404

def test_comment_errors(client, tokens):
    response = client.post(
        "/api/v1/writings/999/comments",
        json={"content": "Hola"},
        headers=tokens["reader1"]
    )
    assert response.status_code == 404

    del_response = client.delete("/api/v1/comments/999", headers=tokens["reader1"])
    assert del_response.status_code == 404
