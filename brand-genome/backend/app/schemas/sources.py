from app.schemas.common import SourceOut

# Re-exported under its own module so `GET /api/brands/{id}/sources` has an
# obvious home, even though SourceOut itself lives in common.py (it's reused
# by nearly every other module schema as an embedded field).
__all__ = ["SourceOut"]
