# ── СТАДИЯ 1: builder ──────────────────────────────────────────
FROM python:3.12 AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python -m pytest tests/ -v

# ── СТАДИЯ 2: runtime ──────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PORT=8080 \
    DATA_FILE=/app/data/books.json

# Теперь копируем пакеты из глобального python, не из /root/.local
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/app.py .

EXPOSE 8080
CMD ["python", "app.py"]