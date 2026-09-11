from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Every error response follows this shape (Section 6 of the architecture doc)."""

    error: ErrorDetail
