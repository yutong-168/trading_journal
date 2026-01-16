FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r backend/requirements.txt

WORKDIR /app/backend

EXPOSE 5050

CMD ["python", "-m", "app.run"]
