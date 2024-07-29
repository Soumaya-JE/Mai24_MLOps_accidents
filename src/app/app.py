import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
from contextlib import asynccontextmanager
import logging

columns = ['grav', 'catr', 'col', 'agg', 'manv', 'circ', 'lum', 'trajet', 'place', 'catu', 'plan', 'choc', 'situ', 'catv', 'int', 'prof']
dict_res = {1: 'Indemne ou blessé léger', 2: 'Tué', 3:'Blessé hospitalisé '}
model_path = './models/model_rf_clf.pkl'
model = None

@asynccontextmanager # sert à gérer les événements de cycle de vie de l'application
async def lifespan(app: FastAPI):
    global model
    try:
        with open(model_path, 'rb') as model_file:
            model = pickle.load(model_file)
        logging.info("Modele charge correctement")
    except FileNotFoundError as e:
        logging.error(f"Modele non trouvé: {e}")
    

app = FastAPI(lifespan=lifespan)


class DataInput(BaseModel):
    data: list

@app.get("/")
async def root():
    return {"message": "Bienvenue sur notre API de prédiction de risques !"}

@app.post("/predict")
async def predict(input_data: DataInput):
    try:
        if model is None:
            raise HTTPException(status_code=500, detail="Le modele n est pas charge")
        df = pd.DataFrame(input_data.data, columns=columns)
        predictions = model.predict(df)
        results = [dict_res[pred] for pred in predictions]
    
        return {"predictions": results}
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)