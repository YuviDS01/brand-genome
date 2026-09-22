"""
Validation-only tests for the research request schema. No DB/service layer
involved -- these exercise ResearchCreateRequest directly, which is where
the actual validation logic lives (Step 17's edge-case fixes).
"""

import pytest
from pydantic import ValidationError

from app.schemas.research import ResearchCreateRequest


def test_valid_brand_name_is_accepted():
    req = ResearchCreateRequest(brand_name="Nike")
    assert req.brand_name == "Nike"


def test_brand_name_is_trimmed():
    req = ResearchCreateRequest(brand_name="  Nike  ")
    assert req.brand_name == "Nike"


def test_blank_brand_name_is_rejected():
    with pytest.raises(ValidationError):
        ResearchCreateRequest(brand_name="   ")


def test_empty_brand_name_is_rejected():
    with pytest.raises(ValidationError):
        ResearchCreateRequest(brand_name="")


def test_missing_brand_name_is_rejected():
    with pytest.raises(ValidationError):
        ResearchCreateRequest()


def test_malformed_website_url_is_rejected():
    with pytest.raises(ValidationError):
        ResearchCreateRequest(brand_name="Nike", website_url="not-a-url")


def test_website_url_is_optional():
    req = ResearchCreateRequest(brand_name="Nike")
    assert req.website_url is None


def test_valid_website_url_is_accepted():
    req = ResearchCreateRequest(brand_name="Nike", website_url="https://www.nike.com")
    assert str(req.website_url).rstrip("/") == "https://www.nike.com"