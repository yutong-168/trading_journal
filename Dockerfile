FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r backend/requirements.txt

# 关键：把工作目录切到 backend
WORKDIR /app/backend

EXPOSE 5000

CMD ["python", "-m", "app.run"]
