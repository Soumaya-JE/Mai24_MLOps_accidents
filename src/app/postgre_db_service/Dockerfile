FROM postgres:13

COPY data_2005a2021_final.csv /docker-entrypoint-initdb.d/
COPY init.sql /docker-entrypoint-initdb.d/

RUN chmod 644 /docker-entrypoint-initdb.d/data_2005a2021_final.csv

ENV POSTGRES_USER=my_user
ENV POSTGRES_PASSWORD=your_password
ENV POSTGRES_DB=accidents
