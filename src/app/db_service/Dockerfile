# Utiliser l'image de base officielle Python
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
COPY main.py /app/
COPY data_fictive_drifted.csv /app/
#COPY run_insertion.sh /app/
COPY requirements.txt /app/
COPY last_inserted_line.txt /app/

# Installer les dépendances système et bibliothèques pour psycopg2 et pandas
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    cron \
    procps \
    grep \
    libatlas-base-dev  # Dépendance nécessaire pour numpy/scipy

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer pandas explicitement
RUN pip install pandas

# Donner les droits d'exécution au script Python
RUN chmod +x /app/main.py

# Créer un nouveau cron job qui exécute le script toutes les minutes
RUN echo "* * * * * root  /usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/insertion-cron

# Appliquer les permissions correctes au fichier cron job
RUN chmod 0644 /etc/cron.d/insertion-cron

# Créer un fichier log pour le cron job
RUN touch /var/log/cron.log

# Commande pour démarrer cron en avant-plan
CMD cron && tail -f /var/log/cron.log
