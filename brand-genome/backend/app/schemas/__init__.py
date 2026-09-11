"""
Pydantic schemas -- the request/response contract layer between the FastAPI
app and the outside world (frontend, or anyone calling the API directly).

These are intentionally decoupled from the SQLAlchemy models in app/models:
some fields here (image_urls, media_urls, logo_url, source_url on NewsItemOut,
etc.) are *resolved* values built by a service function from an ORM object's
relationships, not a straight column-for-column mirror. Only the enums are
shared directly with app/models/enums.py, since duplicating that vocabulary
would risk drift.
"""
