from app.schemas.common import ORMBase, SourceOut


class BusinessInformationOut(ORMBase):
    employee_count: int | None = None
    revenue: float | None = None
    revenue_growth: float | None = None
    valuation: float | None = None
    market_cap: float | None = None
    countries_operated: list | None = None
    stores: int | None = None
    subsidiaries: list | None = None
    financial_highlights: dict | None = None
    sources: list[SourceOut] = []
