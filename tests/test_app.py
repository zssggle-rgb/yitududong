"""Flask 应用集成测试"""
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """测试首页"""
    rv = client.get("/")
    assert rv.status_code == 200
    assert "一图读懂".encode() in rv.data  # "一图读懂"

def test_health(client):
    """测试健康检查"""
    rv = client.get("/health")
    assert rv.status_code == 200
    assert b"ok" in rv.data

def test_upload_no_file(client):
    """测试无文件上传"""
    rv = client.post("/upload")
    assert rv.status_code == 400

def test_upload_empty_filename(client):
    """测试空文件名上传"""
    rv = client.post("/upload", data={"file": (b"", "")})
    assert rv.status_code == 400

def test_api_upload_no_file(client):
    rv = client.post("/api/upload")
    assert rv.status_code == 400
