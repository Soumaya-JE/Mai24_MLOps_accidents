from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import joblib
import os
from passlib.context import CryptContext

app = FastAPI()

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = {
    "user1": {
        "username": "user1",
        "name": "Sousou",
        "hashed_password": pwd_context.hash('datascientest'),
        "role": "standard",
    },
    "user2": {
        "username": "user2",
        "name": "Mim",
        "hashed_password": pwd_context.hash('secret'),
        "role": "standard",
    },
    "admin": {
        "username": "admin",
        "name": "Admin",
        "hashed_password": pwd_context.hash('adminsecret'),
        "role": "admin",
    }
}

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    user = users.get(username)
    if not user or not pwd_context.verify(credentials.password, user['hashed_password']):
        raise HTTPException(
            status_code=401,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

model_path = "model_rf_clf.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Le fichier de modèle {model_path} n'existe pas.")

with open(model_path, 'rb') as model_file:
    model = joblib.load(model_file)

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
def predict(accident: DonneesAccident, user: dict = Depends(get_current_user)):
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

