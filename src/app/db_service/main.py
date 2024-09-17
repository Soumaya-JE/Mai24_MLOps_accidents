import pandas as pd
import psycopg2
from psycopg2 import sql
from datetime import datetime

df = pd.read_csv('data_fictive_drifted.csv')

# On ajoute la date et l heure d insertion du fichier fictif dans la table data_accidents
df['timestamp'] = datetime.now()  
df['is_ref'] = 'no'  

# On supprime les éventuels doublons crées lors de la simulation de données dans la colonne 'num_acc'
df.drop_duplicates(subset=['num_acc'], inplace=True)

# On se conencte avec psycopg2 à notre bdd
try:
    conn = psycopg2.connect(
        host="localhost",        
        port="5432",             
        dbname="accidents",      
        user="my_user",          
        password="your_password" 
    )
    cursor = conn.cursor()

    # On insère nos données
    insert_query = """
    INSERT INTO donnees_accidents (num_acc, mois, jour, lum, agg, int, col, com, dep, hr, mn, 
                                   catv, choc, manv, place, catu, grav, trajet, an_nais, catr, 
                                   circ, nbv, prof, plan, lartpc, larrout, situ, timestamp, is_ref) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (num_acc) DO NOTHING;
    """

    data_tuples = [(
        row['num_acc'], row['mois'], row['jour'], row['lum'], row['agg'], row['int'], 
        row['col'], row['com'], row['dep'], row['hr'], row['mn'], row['catv'], 
        row['choc'], row['manv'], row['place'], row['catu'], row['grav'], row['trajet'], 
        row['an_nais'], row['catr'], row['circ'], row['nbv'], row['prof'], row['plan'], 
        row['lartpc'], row['larrout'], row['situ'], row['timestamp'], row['is_ref']
    ) for _, row in df.iterrows()]

    # Exécuter les insertions en une seule transaction
    cursor.executemany(insert_query, data_tuples)

    # Valider les transactions
    conn.commit()

    print(f"{len(df)} nouvelles lignes insérées dans la table 'donnees_accidents'.")

except Exception as error:
    print(f"Erreur lors de la connexion ou de l'insertion dans PostgreSQL : {error}")

finally:
    if conn:
        cursor.close()
        conn.close()
