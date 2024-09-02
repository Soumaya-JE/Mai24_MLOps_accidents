FROM python:3.9-slim

WORKDIR /app

COPY monitoring_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY monitoring_service/ .

EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
