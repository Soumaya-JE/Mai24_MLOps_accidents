import joblib
import os
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

app = FastAPI()

model_path = "../../models/model_rf_clf.pkl"

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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

def get_current_active_user(user: dict = Depends(get_current_user)):
    if user.get("role") not in ["standard", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilisateur inactif",
        )
    return user

def get_current_admin_user(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits non autorisés",
        )
    return user

@app.get("/monitor")
def monitor_model(user: dict = Depends(get_current_admin_user)):
    """
    Endpoint pour surveiller l'accuracy du modèle.
    
    Accessible uniquement aux admin.

    Args:
    - user : L'utilisateur récupéré à partir de la dépendance `get_current_admin_user`.

    Returns:
    - dict: Contient l'accuracy actuelle du modèle et l'horodatage du réentraînement.
    """
    return {
        "accuracy": accuracy,
        "last_retrained": retrain_timestamp
    }
