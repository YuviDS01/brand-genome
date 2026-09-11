FROM python:3.12-slim

WORKDIR /app

# System deps needed by psycopg2 (binary wheel usually covers it, but keep
# build tools available in case a platform needs to compile) and Playwright's
# browser dependencies (installed separately, in a later step, once the real
# crawler lands — not needed yet for Steps 6-13).
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
