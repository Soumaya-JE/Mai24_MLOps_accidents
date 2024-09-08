from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import joblib
import os

app = FastAPI()

# Charger le modèle depuis le fichier pickle
MODEL_PATH = "/app/models/model_rf_clf.pkl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Le fichier de modèle {MODEL_PATH} n'existe pas.")

with open(MODEL_PATH, 'rb') as model_file:
    model_data = joblib.load(model_file)
    if not isinstance(model_data, dict):
        raise ValueError("Le fichier pickle ne contient pas de dictionnaire.")

    model = model_data.get('model')
    accuracy = model_data.get('accuracy')
    retrain_timestamp = model_data.get('retrain_timestamp') 

    if model is None or accuracy is None:
        raise ValueError("Le dictionnaire chargé ne contient pas les clés 'model' et 'accuracy'.")

# Définir l'hôte autorisé (API Gateway)
ALLOWED_HOST = "api_gateway"

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
async def predict(request: Request, accident: DonneesAccident):

    if request.headers.get("Host") != ALLOWED_HOST:
        raise HTTPException(status_code=403, detail="Accès interdit")
    
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
        return {"Cet accident est de niveau de gravité": prediction.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {e}")
    
