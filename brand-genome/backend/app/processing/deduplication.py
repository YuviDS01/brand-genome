def deduplicate_raw_pages(raw_pages: list) -> list:
    """Drop raw pages whose content_hash we've already seen -- e.g. the same
    page discovered independently via two different search queries."""
    seen: set[str] = set()
    unique = []
    for page in raw_pages:
        if page.content_hash in seen:
            continue
        seen.add(page.content_hash)
        unique.append(page)
    return unique