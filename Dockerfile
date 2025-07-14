# Dockerfile
FROM python:3.11.9-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "--app=app:create_app", "run", "--host=0.0.0.0", "--port=5000"]
