#!/usr/bin/env python3
import pandas as pd
import psycopg2
from datetime import datetime
import os
import numpy as np

# Chemin du fichier CSV
csv_file_path = '/app/data_fictive_drifted.csv'

# Chemin du fichier de suivi de la dernière ligne insérée
last_inserted_file = '/app/last_inserted_line.txt'

# Charger le fichier CSV
df = pd.read_csv(csv_file_path)

# Ajouter le timestamp et marquer les données comme non référentielles
df['timestamp'] = datetime.now()
df['is_ref'] = 'no'

# Supprimer les doublons basés sur num_acc
df.drop_duplicates(subset=['num_acc'], inplace=True)

# Arrondir les colonnes de type float aux entiers les plus proches, puis les convertir en int
float_cols = ['col', 'choc', 'manv', 'grav', 'trajet', 'circ', 'prof', 'plan', 'situ']
df[float_cols] = df[float_cols].round(0).astype(int)

# Convertir explicitement les autres colonnes en types natifs Python
df = df.astype({
    'num_acc': int, 'mois': int, 'jour': int, 'lum': int, 'agg': int, 'int': int, 'com': int, 
    'dep': int, 'hr': int, 'mn': int, 'catv': int, 'place': int, 'catu': int, 'an_nais': int, 
    'catr': int, 'nbv': int, 'lartpc': int, 'larrout': int
})

# Lire l'indice de la dernière ligne insérée depuis le fichier de suivi
if os.path.exists(last_inserted_file):
    with open(last_inserted_file, 'r') as f:
        content = f.read().strip()
        if content:  # Si le fichier n'est pas vide
            last_inserted_line = int(content)
        else:  # Si le fichier est vide
            last_inserted_line = -1
else:
    last_inserted_line = -1  # Si le fichier n'existe pas encore, commencer à la première ligne

# Calculer l'indice de la prochaine ligne à insérer
next_line = last_inserted_line + 1

# Vérifier si on a encore des lignes à insérer
if next_line >= len(df):
    print("Toutes les lignes ont déjà été insérées.")
else:
    # Extraire la ligne à insérer sous forme de dictionnaire
    row = df.iloc[next_line].to_dict()

    # Connexion à la base de données PostgreSQL
    try:
        conn = psycopg2.connect(
            host="db",
            port="5432",
            dbname="accidents",
            user="my_user",
            password="your_password"
        )
        cursor = conn.cursor()

        # Requête d'insertion
        insert_query = """
        INSERT INTO donnees_accidents (num_acc, mois, jour, lum, agg, int, col, com, dep, hr, mn,        
                                       catv, choc, manv, place, catu, grav, trajet, an_nais, catr,       
                                       circ, nbv, prof, plan, lartpc, larrout, situ, timestamp, is_ref)  
        VALUES (%(num_acc)s, %(mois)s, %(jour)s, %(lum)s, %(agg)s, %(int)s, %(col)s, %(com)s, %(dep)s, %(hr)s, %(mn)s, 
                %(catv)s, %(choc)s, %(manv)s, %(place)s, %(catu)s, %(grav)s, %(trajet)s, %(an_nais)s, %(catr)s, 
                %(circ)s, %(nbv)s, %(prof)s, %(plan)s, %(lartpc)s, %(larrout)s, %(situ)s, %(timestamp)s, %(is_ref)s)
        ON CONFLICT (num_acc) DO NOTHING;
        """

        # Exécuter l'insertion avec les valeurs extraites du dictionnaire
        cursor.execute(insert_query, row)
        conn.commit()

        print(f"Ligne {next_line + 1} insérée dans la table 'donnees_accidents'.")

        # Mettre à jour l'indice de la dernière ligne insérée dans le fichier
        with open(last_inserted_file, 'w') as f:
            f.write(str(next_line))

    except psycopg2.Error as error:
        print(f"Erreur lors de l'insertion dans PostgreSQL : {error}")

    finally:
        if conn:
            cursor.close()
            conn.close()
