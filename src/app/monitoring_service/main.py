import joblib
import os
from fastapi import Depends, FastAPI, HTTPException, Request



app = FastAPI()

ALLOWED_HOST = "api_gateway"

model_path = "/app/models/model_rf_clf.pkl"

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Le fichier de modèle {model_path} n'existe pas.")

with open(model_path, 'rb') as model_file:
    model_data = joblib.load(model_file)
    if not isinstance(model_data, dict):
        raise ValueError("Le fichier pickle ne contient pas de dictionnaire.")

    model = model_data.get('model')
    accuracy = model_data.get('accuracy')
    retrain_timestamp = model_data.get('retrain_timestamp')

    if model is None or accuracy is None:
        raise ValueError("Le dictionnaire chargé ne contient pas les clés 'model' et 'accuracy'.")

@app.get("/monitor")
async def monitor_model(request: Request):
    if request.headers.get("Host") != ALLOWED_HOST:
        raise HTTPException(status_code=403, detail="Accès interdit")

    return {
        "accuracy": accuracy,
        "last_retrained": retrain_timestamp
    }