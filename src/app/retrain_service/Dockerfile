FROM python:3.9-slim

WORKDIR /app

COPY retrain_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY retrain_service/ .

EXPOSE 8003
CMD ["python", "main.py"]
