from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient


# Définir l'application FastAPI
app = FastAPI()

# Charger le modèle
mlflow.set_tracking_uri("http://mlflow_service:5000") 
client = MlflowClient()

def load_production_model_and_evaluate(model_name="model_rf_clf"):
    # Charger toutes les  versions du modele et chercher le tag "is_production"
    try:
        versions = client.search_model_versions(f"name='{model_name}'")
    except mlflow.exceptions.RestException as e:
        print(f"Model '{model_name}' not found in the registry. No production model to evaluate.")
        return None, None
    
    
    prod_model_info = None
    for version in versions:
        if version.tags.get("is_production") == "true":
            prod_model_info = version
            break

    if not prod_model_info:
        print(f"No model tagged as 'is_production=true' exists for '{model_name}'.")
        return None, None
    
    prod_model_version = prod_model_info.version
    print(f"Loading model version {prod_model_version} (tagged as production).")

    model_uri = f"models:/{model_name}/{prod_model_version}"

    prod_model = mlflow.pyfunc.load_model(model_uri)
    return prod_model
 

class DonneesAccident(BaseModel):
    place: int
    catu: int
    trajet: float
    an_nais: int
    catv: int
    choc: float
    manv: float
    mois: int
    jour: int
    lum: int
    agg: int
    int: int
    col: float
    com: int
    dep: int
    hr: int
    mn: int
    catr: int
    circ: float
    nbv: int
    prof: float
    plan: float
    lartpc: int
    larrout: int
    situ: float

@app.post("/predict")
def predict(accident: DonneesAccident):
    """
    Endpoint pour prédire la gravité de l'accident.

    Args:
    - accident : Les données de l'accident défini selon le BaseModel

    Returns:
    - dict: La prédiction de la gravité de l'accident.
    """
    model=load_production_model_and_evaluate(model_name="model_rf_clf")
    try:
        features = [
            accident.place, accident.catu, accident.trajet,
            accident.an_nais, accident.catv, accident.choc, accident.manv,
            accident.mois, accident.jour, accident.lum, accident.agg,
            accident.int, accident.col, accident.com, accident.dep,
            accident.hr, accident.mn, accident.catr, accident.circ,
            accident.nbv, accident.prof, accident.plan, accident.lartpc,
            accident.larrout, accident.situ
    ]
        prediction = model.predict([features])
        return {"Cet accident est de niveau de gravité": int(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))