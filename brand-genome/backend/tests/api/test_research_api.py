"""
Endpoint-level tests for /api/research/*, with the service layer mocked so
these run without a live Postgres. (A real end-to-end run against live
infrastructure was done manually for Step 18 -- see the walkthrough in that
step's writeup. These tests exist so regressions get caught automatically
going forward, not as a substitute for that.)
"""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from app.models.enums import JobStatus


def _fake_job(**overrides):
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        brand_name_input="Nike",
        brand_id=None,
        status=JobStatus.QUEUED,
        progress=0,
        current_task=None,
        message=None,
        sources_attempted=0,
        sources_successful=0,
        sources_failed=0,
        updated_at=now,
        stages=[],
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_create_research_job(client):
    fake_job = _fake_job()
    with patch("app.api.research.create_research_job", return_value=fake_job):
        resp = client.post("/api/research", json={"brand_name": "Nike"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["job_id"] == str(fake_job.id)
    assert body["status"] == "QUEUED"


def test_create_research_job_rejects_blank_name(client):
    resp = client.post("/api/research", json={"brand_name": "   "})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


def test_get_research_job_full(client):
    fake_job = _fake_job(status=JobStatus.COMPLETED, progress=100, brand_id=uuid.uuid4())
    with patch("app.api.research.get_research_job", return_value=fake_job):
        resp = client.get(f"/api/research/{fake_job.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "COMPLETED"
    assert body["brand_id"] == str(fake_job.brand_id)


def test_get_research_job_status_lite(client):
    fake_job = _fake_job()
    with patch("app.api.research.get_research_job", return_value=fake_job):
        resp = client.get(f"/api/research/{fake_job.id}/status")
    assert resp.status_code == 200
    # lite response should NOT include stage history
    assert "stages" not in resp.json()


def test_get_nonexistent_research_job_returns_404(client):
    with patch("app.api.research.get_research_job", return_value=None):
        resp = client.get(f"/api/research/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "job_not_found"


def test_get_research_job_malformed_uuid_returns_422(client):
    resp = client.get("/api/research/not-a-uuid")
    assert resp.status_code == 422