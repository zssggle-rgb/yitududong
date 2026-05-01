"""
Tests for app/main.py - M01 FastAPI 端点
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["module"] == "M01"


class TestIndexPage:
    def test_index_returns_html(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")


class TestReferenceExtract:
    def test_reference_extract_returns_structure(self):
        resp = client.get("/reference-extract")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["module"] == "M01"
        assert "data" in data
        assert data["data"]["title"] != ""
        assert data["data"]["source"] != ""

    def test_reference_extract_has_key_sections(self):
        resp = client.get("/reference-extract")
        data = resp.json()
        assert len(data["data"]["key_sections"]) >= 1

    def test_reference_extract_has_key_points(self):
        resp = client.get("/reference-extract")
        data = resp.json()
        assert len(data["data"]["key_points"]) >= 1


class TestUploadValidation:
    def test_upload_no_file_400(self):
        resp = client.post("/upload")
        # FastAPI returns 422 for missing required field
        assert resp.status_code == 422

    def test_upload_unsupported_format(self):
        from io import BytesIO
        resp = client.post(
            "/upload",
            files={"file": ("test.txt", BytesIO(b"hello"), "text/plain")},
        )
        # Should return 400 with error
        assert resp.status_code == 400
        data = resp.json()
        assert data["success"] is False
        assert "code" in data