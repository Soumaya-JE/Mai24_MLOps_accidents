import pandas as pd
import psycopg2
from datetime import datetime

df = pd.read_csv('data_fictive_drifted.csv')

# On supprime les éventuels doublons crées lors de la simulation de données dans la colonne 'num_acc'
df.drop_duplicates(subset=['num_acc'], inplace=True)

# Index pour suivre quelle ligne insérer
index = 0

def insert_row():
    global index
    if index < len(df):

        row = df.iloc[index]
        data = {
            'num_acc': row['num_acc'],
            'mois': row['mois'],
            'jour': row['jour'],
            'lum': row['lum'],
            'agg': row['agg'],
            'int': row['int'],
            'col': row['col'],
            'com': row['com'],
            'dep': row['dep'],
            'hr': row['hr'],
            'mn': row['mn'],
            'catv': row['catv'],
            'choc': row['choc'],
            'manv': row['manv'],
            'place': row['place'],
            'catu': row['catu'],
            'grav': row['grav'],
            'trajet': row['trajet'],
            'an_nais': row['an_nais'],
            'catr': row['catr'],
            'circ': row['circ'],
            'nbv': row['nbv'],
            'prof': row['prof'],
            'plan': row['plan'],
            'lartpc': row['lartpc'],
            'larrout': row['larrout'],
            'situ': row['situ'],
            'timestamp': datetime.now(),
            'is_ref': 'no'
        }

        # Connexion à la base de données accidents
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5432",
                dbname="accidents",
                user="my_user",
                password="your_password"
            )
            cursor = conn.cursor()

            insert_query = """
            INSERT INTO donnees_accidents (num_acc, mois, jour, lum, agg, int, col, com, dep, hr, mn, 
                                           catv, choc, manv, place, catu, grav, trajet, an_nais, catr, 
                                           circ, nbv, prof, plan, lartpc, larrout, situ, timestamp, is_ref) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (num_acc) DO NOTHING;
            """
            cursor.execute(insert_query, tuple(data.values()))
            conn.commit()

            print(f"Ligne insérée : {data['num_acc']}")

        except Exception as error:
            print(f"Erreur lors de l'insertion : {error}")

        finally:
            if conn:
                cursor.close()
                conn.close()

        index += 1
    else:
        print("Toutes les lignes ont été insérées.")

if __name__ == "__main__":
    insert_row()

