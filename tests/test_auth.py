import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.session import Base, get_db
from app.infrastructure.database.models import EscritoDB, UsuarioDB
from app.infrastructure.security.jwt_service import create_access_token
from datetime import timedelta

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

def test_developer_login_admin(client):
    response = client.post(
        "/api/v1/auth/developer-login",
        json={"email": "writer@example.com", "role": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"

def test_developer_login_reader(client):
    response = client.post(
        "/api/v1/auth/developer-login",
        json={"email": "reader@example.com", "role": "lector"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "lector"

def test_protected_routes_anonymous(client):
    response = client.post(
        "/api/v1/writings/",
        json={"title": "Poema", "content": "...", "status": "publicado"}
    )
    assert response.status_code == 401

def test_protected_routes_reader(client):
    login_res = client.post(
        "/api/v1/auth/developer-login",
        json={"email": "reader@example.com", "role": "lector"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/writings/",
        json={"title": "Poema", "content": "...", "status": "publicado"},
        headers=headers
    )
    assert response.status_code == 403

def test_protected_routes_admin(client):
    login_res = client.post(
        "/api/v1/auth/developer-login",
        json={"email": "writer@example.com", "role": "admin"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/writings/",
        json={"title": "Poema por Admin", "content": "...", "status": "publicado"},
        headers=headers
    )
    assert response.status_code == 201
    writing_id = response.json()["id"]

    del_response = client.delete(f"/api/v1/writings/{writing_id}", headers=headers)
    assert del_response.status_code == 204

def test_draft_visibility(client):
    login_res = client.post(
        "/api/v1/auth/developer-login",
        json={"email": "writer@example.com", "role": "admin"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/v1/writings/",
        json={"title": "Borrador Secreto", "content": "...", "status": "borrador"},
        headers=headers
    )
    writing_id = create_res.json()["id"]

    res_list_anon = client.get("/api/v1/writings/?status=borrador")
    assert res_list_anon.status_code == 403

    reader_login = client.post(
        "/api/v1/auth/developer-login",
        json={"email": "reader@example.com", "role": "lector"}
    )
    reader_token = reader_login.json()["access_token"]
    reader_headers = {"Authorization": f"Bearer {reader_token}"}
    
    res_list_reader = client.get("/api/v1/writings/?status=borrador", headers=reader_headers)
    assert res_list_reader.status_code == 403

    res_list_admin = client.get("/api/v1/writings/?status=borrador", headers=headers)
    assert res_list_admin.status_code == 200
    assert len(res_list_admin.json()) == 1

    res_get_anon = client.get(f"/api/v1/writings/{writing_id}")
    assert res_get_anon.status_code == 403

    res_get_reader = client.get(f"/api/v1/writings/{writing_id}", headers=reader_headers)
    assert res_get_reader.status_code == 403

    res_get_admin = client.get(f"/api/v1/writings/{writing_id}", headers=headers)
    assert res_get_admin.status_code == 200
    assert res_get_admin.json()["title"] == "Borrador Secreto"

def test_invalid_and_expired_token(client):
    expired_token = create_access_token(
        data={"sub": "1", "email": "test@example.com", "role": "admin"},
        expires_delta=timedelta(seconds=-10)
    )
    response = client.post(
        "/api/v1/writings/",
        json={"title": "Poema", "content": "...", "status": "publicado"},
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "expirado" in response.json()["detail"]

    response_invalid = client.post(
        "/api/v1/writings/",
        json={"title": "Poema", "content": "...", "status": "publicado"},
        headers={"Authorization": "Bearer completelyinvalidtoken"}
    )
    assert response_invalid.status_code == 401
