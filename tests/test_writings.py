import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.session import Base, get_db
from app.infrastructure.database.models import EscritoDB

# Use a file-based SQLite database for testing to ensure table visibility
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
        engine.dispose()  # Close all connections in the pool
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

def test_create_writing(client):
    payload = {
        "title": "Poema de Invierno",
        "content": "El frio susurra en la noche...",
        "status": "borrador"
    }
    response = client.post("/api/v1/writings/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["status"] == "borrador"
    assert "id" in data

def test_get_writing(client):
    # First create one
    payload = {
        "title": "Canto de Otono",
        "content": "Hojas amarillas que caen...",
        "status": "publicado"
    }
    create_res = client.post("/api/v1/writings/", json=payload)
    writing_id = create_res.json()["id"]

    # Get it
    response = client.get(f"/api/v1/writings/{writing_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]

def test_get_writing_not_found(client):
    response = client.get("/api/v1/writings/999")
    assert response.status_code == 404
    assert "no existe" in response.json()["detail"]

def test_update_writing(client):
    # First create
    create_res = client.post(
        "/api/v1/writings/",
        json={"title": "Original", "content": "Original Content", "status": "borrador"}
    )
    writing_id = create_res.json()["id"]

    # Update
    update_payload = {
        "title": "Modificado",
        "content": "Modificado Content",
        "status": "publicado"
    }
    response = client.put(f"/api/v1/writings/{writing_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Modificado"
    assert data["status"] == "publicado"

def test_delete_writing(client):
    # First create
    create_res = client.post(
        "/api/v1/writings/",
        json={"title": "To Delete", "content": "Delete this", "status": "borrador"}
    )
    writing_id = create_res.json()["id"]

    # Delete
    response = client.delete(f"/api/v1/writings/{writing_id}")
    assert response.status_code == 204

    # Verify not found
    response_get = client.get(f"/api/v1/writings/{writing_id}")
    assert response_get.status_code == 404

def test_list_writings_and_feed(client):
    # Create two writings: one draft, one published
    client.post("/api/v1/writings/", json={"title": "Borrador 1", "content": "...", "status": "borrador"})
    client.post("/api/v1/writings/", json={"title": "Publicado 1", "content": "...", "status": "publicado"})

    # List all
    res_all = client.get("/api/v1/writings/")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 2

    # List only published
    res_pub = client.get("/api/v1/writings/?status=publicado")
    assert res_pub.status_code == 200
    assert len(res_pub.json()) == 1
    assert res_pub.json()[0]["title"] == "Publicado 1"

def test_search_writings(client):
    # Create writings
    client.post("/api/v1/writings/", json={"title": "Cazador de Estrellas", "content": "...", "status": "publicado"})
    client.post("/api/v1/writings/", json={"title": "Ensayo sobre la Ceguera", "content": "...", "status": "publicado"})
    client.post("/api/v1/writings/", json={"title": "Borrador Secreto", "content": "Cazador...", "status": "borrador"})

    # Search for "Cazador" (should only return the published one)
    response = client.get("/api/v1/writings/search?q=Cazador")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Cazador de Estrellas"
