FROM python:3.9-slim

WORKDIR /app

COPY db_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY db_service/ .

EXPOSE 5432
CMD ["python", "main.py"]
