"""
QueryPlanner (Section 21 of the architecture doc).

Turns "research this brand" into a concrete list of search queries covering
each genome module area, so discovery isn't just one generic search.
"""


class QueryPlanner:
    _TOPICS = [
        "official website",
        "company history",
        "products",
        "leadership",
        "competitors",
        "marketing campaigns",
        "social media accounts",
        "latest news",
        "customer reviews",
        "financial information",
        "sustainability",
    ]

    def generate_queries(self, brand_name: str) -> list[str]:
        return [f"{brand_name} {topic}" for topic in self._TOPICS]