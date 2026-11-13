FROM node:22-alpine AS frontend

WORKDIR /build

COPY trading-engine-frontend/package*.json ./
RUN npm ci --include=dev

COPY trading-engine-frontend/ ./
RUN VITE_API_URL=/ npm run build


FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY --from=frontend /build/dist ./frontend/

WORKDIR /app/src/v1

CMD ["sh", "-c", "python -m alembic upgrade head && exec python -m uvicorn main:app --host 0.0.0.0 --port \"${PORT:-8000}\" --workers 1"]
