from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2 import sql


# Définir l'application FastAPI
app = FastAPI()

# On se connecte à la base de données PostgreSQL
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="db",  
            database="accidents",
            user="my_user",
            password="your_password"
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")


# BaseModel pour correction de prediction
class CorrectionGravite(BaseModel):
    num_acc: int
    grav_corrigee: int  

@app.put("/correct_predict")
def correct_prediction(correction: CorrectionGravite):
    """
    Endpoint pour corriger manuellement la gravité d'un accident.

    Args:
    - correction : Les données de correction de l'accident (num_acc, grav_corrigee)

    Returns:
    - dict: Confirmation de la correction effectuée.
    """
    try:
        
        conn = get_db_connection()
        cur = conn.cursor()

        select_query = sql.SQL("""
            SELECT grav FROM predictions_accidents WHERE num_acc = {num_acc}
        """).format(num_acc=sql.Literal(correction.num_acc))

        cur.execute(select_query)
        accident_data = cur.fetchone()

        if accident_data is None:
            raise HTTPException(status_code=404, detail=f"Accident avec num_acc {correction.num_acc} non trouvé.")

        gravite_actuelle = accident_data[0]
        if gravite_actuelle == correction.grav_corrigee:
            return {"message": "La gravité est déjà correcte", "gravite_actuelle": gravite_actuelle}

        update_query = sql.SQL("""
            UPDATE predictions_accidents
            SET grav = {grav_corrigee}
            WHERE num_acc = {num_acc}
        """).format(
            grav_corrigee=sql.Literal(correction.grav_corrigee),
            num_acc=sql.Literal(correction.num_acc)
        )

        cur.execute(update_query)
        conn.commit()

        cur.close()
        conn.close()

        return {"message": "Gravité corrigée avec succès", "gravite_corrigee": correction.grav_corrigee}

    except Exception as db_error:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la base de données: {str(db_error)}")