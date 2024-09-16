FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY data_fictive.py .
COPY data_fictive.csv .

CMD ["python", "data_fictive.py"]