"""
Endpoint-level tests for /api/brands/* and /api/brands/{id}/genome, with the
service layer mocked so these run without a live Postgres.
"""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException, status

from app.models.enums import BrandStatus


def _fake_brand(**overrides):
    defaults = dict(
        id=uuid.uuid4(),
        brand_name="Nike",
        slug="nike",
        status=BrandStatus.ready,
        last_crawled_at=None,
        last_updated_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _not_found(db, brand_id):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "brand_not_found", "message": f"No brand with id {brand_id}."},
    )


def test_get_brand(client):
    fake_brand = _fake_brand()
    with patch("app.services.dashboard_service.get_brand_or_404", return_value=fake_brand):
        resp = client.get(f"/api/brands/{fake_brand.id}")
    assert resp.status_code == 200
    assert resp.json()["brand_name"] == "Nike"


def test_get_nonexistent_brand_returns_404(client):
    bad_id = uuid.uuid4()
    with patch("app.services.dashboard_service.get_brand_or_404", side_effect=_not_found):
        resp = client.get(f"/api/brands/{bad_id}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "brand_not_found"


def test_empty_module_returns_empty_list_not_error(client):
    """A brand existing but having zero competitors is normal, not an error."""
    fake_brand = _fake_brand()
    with (
        patch("app.services.dashboard_service.get_brand_or_404", return_value=fake_brand),
        patch("app.services.dashboard_service.get_competitors", return_value=[]),
    ):
        resp = client.get(f"/api/brands/{fake_brand.id}/competitors")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_genome_aggregate(client):
    fake_brand = _fake_brand()
    fake_genome = {
        "brand_id": str(fake_brand.id),
        "brand_name": "Nike",
        "identity": {
            "legal_name": None, "logo_url": None, "tagline": None,
            "official_website": None, "industry": None, "category": None,
            "sub_category": None, "founded_year": 1964,
            "headquarters": "Beaverton, Oregon", "country": None,
            "parent_company": None, "founders": None, "key_people": None,
            "description": "Nike, Inc. is an American multinational corporation.",
        },
        "history": [], "products": [], "services": [], "audience": [],
        "positioning": None, "competitors": [], "campaigns": [],
        "digital_presence": {"official_website": None, "social_accounts": []},
        "sentiment": None, "news": [], "business": None, "sources": [],
        "meta": {"last_updated_at": None, "sources_successful": 6, "sources_failed": 1},
    }
    with (
        patch("app.services.dashboard_service.get_brand_or_404", return_value=fake_brand),
        patch("app.services.dashboard_service.get_genome", return_value=fake_genome),
    ):
        resp = client.get(f"/api/brands/{fake_brand.id}/genome")
    assert resp.status_code == 200
    body = resp.json()
    assert body["identity"]["founded_year"] == 1964
    assert body["meta"]["sources_successful"] == 6


def test_get_genome_for_nonexistent_brand_returns_404(client):
    bad_id = uuid.uuid4()
    with patch("app.services.dashboard_service.get_brand_or_404", side_effect=_not_found):
        resp = client.get(f"/api/brands/{bad_id}/genome")
    assert resp.status_code == 404