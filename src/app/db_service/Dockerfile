FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY run_insertion.sh .

RUN chmod +x run_insertion.sh

RUN apt-get update && apt-get install -y cron

RUN echo "* * * * * /app/db_service/run_insertion.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/data_insertion_cron

RUN chmod 0644 /etc/cron.d/data_insertion_cron

RUN touch /var/log/cron.log

CMD ["cron", "-f"]
