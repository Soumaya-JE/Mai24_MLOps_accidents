from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import httpx

app = FastAPI()

# Définir les URLs des services internes
PREDICTION_SERVICE_URL = "http://prediction_service:8001/predict"
RETRAIN_SERVICE_URL = "http://retrain_service:8003/retrain"
DB_SERVICE_URL = "http://db_service:5432/query"
MONITORING_SERVICE_URL = "http://monitoring_service:8002/monitor"

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

# Définir la classe de données pour la prédiction
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

# Endpoints de l'API Gateway

################################## statut de l'API Gateway ###################################

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = users.get(credentials.username)
    if not user or not pwd_context.verify(credentials.password, user['hashed_password']):
        raise HTTPException(
            status_code=401,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

@app.get("/predict")
async def predict(request: Request, user: dict = Depends(get_current_user)):
    if user['role'] not in ['standard', 'admin']:
        raise HTTPException(status_code=403, detail="Droits non autorisés")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(PREDICTION_SERVICE_URL, json=await request.json())
        return response.json()

@app.post("/retrain")
async def retrain(request: Request, user: dict = Depends(get_current_user)):
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Droits non autorisés")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(RETRAIN_SERVICE_URL, json=await request.json())
        return response.json()

@app.get("/query")
async def query_db(request: Request, user: dict = Depends(get_current_user)):
    if user['role'] not in ['admin']:
        raise HTTPException(status_code=403, detail="Droits non autorisés")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(DB_SERVICE_URL)
        return response.json()

@app.get("/monitor")
async def monitor(request: Request, user: dict = Depends(get_current_user)):
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Droits non autorisés")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(MONITORING_SERVICE_URL)
        return response.json()