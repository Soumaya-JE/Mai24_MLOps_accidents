from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import subprocess

app = FastAPI()

# Définir l'hôte autorisé (API Gateway)
ALLOWED_HOST = "api_gateway"

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

@app.post("/retrain")
async def retrain(request: Request, user: dict = Depends(get_current_user)):
    # Vérifier que la requête provient de l'API Gateway
    if request.headers.get("Host") != ALLOWED_HOST:
        raise HTTPException(status_code=403, detail="Accès interdit")
    
    # Vérifier le rôle de l'utilisateur
    if user['role'] != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Droits non autorisés",
        )
    
    try:
        # Exécuter le script de réentraînement
        subprocess.run(["python", "train.py"], check=True)
        return {"message": "Re-entrainement réussi"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du re-entrainement: {e}")