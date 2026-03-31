import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MAINLAYER_API_KEY", "test-key")
os.environ.setdefault("MAINLAYER_RESOURCE_ID", "test-resource")


def _make_app():
    with patch("mainlayer.MainlayerClient"):
        from src.main import app
        return app


@pytest.fixture(autouse=True)
def reset_quota():
    """Reset the in-memory quota store before each test."""
    import src.mainlayer_tiers as tiers
    tiers._quota.clear()
    yield


@pytest.fixture()
def authorized_client():
    app = _make_app()
    access_mock = MagicMock()
    access_mock.authorized = True
    with patch("src.main.ml") as ml_mock, \
         patch("src.mainlayer_tiers.get_client") as gc_mock:
        ml_mock.resources.verify_access = AsyncMock(return_value=access_mock)
        gc_mock.return_value.resources.verify_access = AsyncMock(return_value=access_mock)
        with TestClient(app) as client:
            yield client


@pytest.fixture()
def unauthorized_client():
    app = _make_app()
    access_mock = MagicMock()
    access_mock.authorized = False
    with patch("src.main.ml") as ml_mock, \
         patch("src.mainlayer_tiers.get_client") as gc_mock:
        ml_mock.resources.verify_access = AsyncMock(return_value=access_mock)
        gc_mock.return_value.resources.verify_access = AsyncMock(return_value=access_mock)
        with TestClient(app) as client:
            yield client


def test_health():
    app = _make_app()
    with TestClient(app) as client:
        resp = client.get("/health")
    assert resp.status_code == 200


def test_free_tier_search():
    app = _make_app()
    with patch("mainlayer.MainlayerClient"):
        with TestClient(app) as client:
            resp = client.get("/search", params={"q": "python"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["tier"] == "free"
    assert len(data["results"]) <= 3
    assert "quota_remaining" in data


def test_free_tier_quota_exhaustion():
    from src.mainlayer_tiers import FREE_DAILY_LIMIT
    app = _make_app()
    with patch("mainlayer.MainlayerClient"):
        with TestClient(app) as client:
            for _ in range(FREE_DAILY_LIMIT):
                r = client.get("/search", params={"q": "test"})
                assert r.status_code == 200

            over_limit = client.get("/search", params={"q": "test"})
            assert over_limit.status_code == 429


def test_paid_tier_search(authorized_client):
    resp = authorized_client.get(
        "/search",
        params={"q": "machine learning", "limit": 5},
        headers={"x-mainlayer-token": "valid-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tier"] == "paid"
    assert "quota_remaining" not in data or data.get("quota_remaining") is None


def test_paid_tier_unauthorized(unauthorized_client):
    resp = unauthorized_client.get(
        "/search",
        params={"q": "test"},
        headers={"x-mainlayer-token": "bad-token"},
    )
    assert resp.status_code == 402


def test_missing_query():
    app = _make_app()
    with patch("mainlayer.MainlayerClient"):
        with TestClient(app) as client:
            resp = client.get("/search")
    assert resp.status_code == 422
