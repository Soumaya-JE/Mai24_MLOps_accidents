from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, '../../models/model_rf_clf.pkl')
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Le fichier de modèle {model_path} n'existe pas.")
model = joblib.load(model_path)

# on définit une classe de requête avec les données minimales permettant de faire tourner notre modèle
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

# endpoint d accueil
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur notre API de prédiction de la gravité des accidents routiers"}

# endpoint pour la prédiction
@app.post("/predict")
def predict(accident: DonneesAccident):
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
        return {"prediction": int(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)