import os
from fastapi import Depends, FastAPI, HTTPException
import pandas as pd
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
from evidently.report import Report
import requests
import psycopg2
from psycopg2 import sql
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient


# Fonction pour obtenir une connexion à la database
def get_db_connection():
    connection = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "accidents"),
        user=os.getenv("POSTGRES_USER", "my_user"),
        password=os.getenv("POSTGRES_PASSWORD", "your_password"),
        host=os.getenv("POSTGRES_HOST", "db"),  
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    return connection

# Fonction pour charger les données depuis la database

def load_data_from_db():
    """
    Charger les données de la table 'donnees_accidents' à partir de la base de données PostgreSQL.
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Charger les données de référence
            cursor.execute("SELECT * FROM donnees_accidents WHERE is_ref = 'yes';")
            reference_data = cursor.fetchall()

            # Charger les nouvelles données
            cursor.execute("SELECT * FROM donnees_accidents WHERE is_ref = 'no';")
            new_data = cursor.fetchall()

            # Convertir les résultats en DataFrame
            colnames = [desc[0] for desc in cursor.description]
            reference_df = pd.DataFrame(reference_data, columns=colnames)
            new_data_df = pd.DataFrame(new_data, columns=colnames)
            # Définir la colonne num_acc comme index
            reference_df = reference_df.set_index('num_acc')
            new_data_df = new_data_df.set_index('num_acc')

    finally:
        connection.close()

    return reference_df, new_data_df


app = FastAPI()
#charger les chemins
status_file_path = 'drift_detected.txt'

# URL de l'API de réentraînement
RETRAIN_API_URL = "http://retrain_service:8003/retrain"

#charger le modèle
mlflow.set_tracking_uri("http://mlflow_service:5000") 
client = MlflowClient()

def load_production_accuracy_model(model_name="model_rf_clf"):
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
    run_id = prod_model_info.run_id
    print(f"Loading model version {prod_model_version} (tagged as production).")

    model_uri = f"models:/{model_name}/{prod_model_version}"
    prod_model = mlflow.pyfunc.load_model(model_uri)

    #load accuracy
    try:
        run = client.get_run(run_id)
        prod_model_accuracy = run.data.metrics.get("new_model_accuracy")  
        if prod_model_accuracy is not None:
            print(f"Retrieved accuracy from MLflow: {prod_model_accuracy}")
            return prod_model_accuracy, prod_model_version
        else:
            print("Accuracy metric not found in MLflow for this run. Evaluating model on test data.")
    except Exception as e:
        print(f"Could not retrieve metrics from MLflow: {e}")
    return prod_model_accuracy,prod_model 

#fonction pour générer des prédiction
def get_prediction(model, reference_data, current_data):
    """
    Générer des prédictions pour reference et current data.
    """
    # Créer une copie de dataframes tpour éviter la modification de l'originale
    reference_data = reference_data.copy()
    current_data = current_data.copy()

    # Générer des prédictions pour reference et current data.
    reference_data['prediction'] = model.predict(reference_data.drop(columns=['grav','timestamp','is_ref']))
    current_data['prediction'] = model.predict(current_data.drop(columns=['grav','timestamp','is_ref']))

    return reference_data, current_data


# Fonction pour détecter le data drift
def detect_data_drift(reference_data: pd.DataFrame, new_data,SAVE_FILE = True):
    """
    Détecter le drift des données entre le jeu de données de référence et le nouveau jeu de données.
    
    :param reference_data: DataFrame contenant les données de référence.
    :param new_data: DataFrame contenant les nouvelles données.
    :return: Booléen indiquant si un drift a été détecté.
    """
    data_drift_report = Report(metrics=[DataDriftPreset()])
    data_drift_report.run(reference_data=reference_data.drop(['target','timestamp','is_ref'], axis=1), 
                          current_data=new_data.drop(['target','timestamp','is_ref'], axis=1), column_mapping=None)
    report_json = data_drift_report.as_dict()
    drift_detected = report_json['metrics'][0]['result']['dataset_drift']
    # Save the report as HTML
    if SAVE_FILE:
        data_drift_report.save_html("data_drift_report.html")
    return drift_detected

# Fonction pour écrire le statut du drift dans un fichier
def write_drift_status_to_file(status: str, file_path: str):
    """
    Écrire le statut de la détection de drift dans un fichier.
    
    :param status: Le statut du drift ('drift_detected' ou 'no_drift').
    :param file_path: Le chemin vers le fichier où écrire le statut.
    """
    with open(file_path, 'w') as f:
        f.write(status)



#fonction pour détecter le modèle drift
def detect_model_drift(reference_data: pd.DataFrame, new_data: pd.DataFrame) -> bool:
    """
    Utilise Evidently pour détecter la dérive des performances du modèle.
    """
    classification_perf_report = Report(metrics=[ClassificationPreset()])
    classification_perf_report.run(reference_data=reference_data, current_data=new_data, column_mapping=None)
    
    # Extraire les résultats sous forme de dictionnaire
    report_json = classification_perf_report.as_dict()
    
    
    print(report_json)
    
    performance_metrics = report_json['metrics'][0]['result']


    if 'accuracy' in performance_metrics:
        current_accuracy = performance_metrics['accuracy']['current']
        reference_accuracy = performance_metrics['accuracy']['reference']
        
        # Vérifier si la précision actuelle est inférieure à 90% de la précision de référence
        if current_accuracy < reference_accuracy * 0.8:
            return True
    else:
        print("Accuracy metric is missing from the report.")
        return False
    
    return False
    

# Fonction pour envoyer une requête à l'API de réentraînement
def trigger_retraining():
    """
    #Fonction qui envoie une requête à l'API de réentraînement
    """
    try:
        response = requests.post(RETRAIN_API_URL)
        if response.status_code == 200:
            print("Réentraînement lancé avec succès via l'API.")
        else:
            print(f"Échec du réentraînement via l'API. Statut: {response.status_code}")
    except Exception as e:
        print(f"Erreur lors de la tentative d'appel à l'API de réentraînement: {str(e)}")
        


#définir un endpoint pour évaluer la performance du modèle et vérifier s'il y a un drift

@app.get("/monitor")
def monitor():
    """
    Endpoint pour surveiller l'accuracy du modèle,vérifier qu'il y a pas de drift (data+model).
    
    Accessible uniquement aux admin.

    Si il ya un drift il déclenche un retraning en evoyant un request à l'api de retrain

    Args:
    - user : L'utilisateur récupéré à partir de la dépendance `get_current_admin_user`.

    Returns:
    - dict: Contient l'accuracy actuelle du modèle et la présence du drift ou non
    """
    #charger l'accuracy
    prod_model_accuracy, model =load_production_accuracy_model(model_name="model_rf_clf")
    # Charger les données depuis la base de données
    reference_data, new_data = load_data_from_db()

    # Ajouter des prédictions aux ensembles de données
    reference_data, new_data = get_prediction(model, reference_data,new_data)
    


    # Renommer les colonnes pour correspondre aux attentes d'Evidently (grav > target)
    reference_data.rename(columns={'grav': 'target'}, inplace=True)
    new_data.rename(columns={'grav': 'target'}, inplace=True)

    
    # Vérifier s'il y a une dérive des données
    data_drift_detected = detect_data_drift(reference_data, new_data)
    
    # Vérifier s'il y a une dérive des performances du modèle
    model_drift_detected = detect_model_drift(reference_data, new_data)
    
    if data_drift_detected or model_drift_detected:
        status = "drift_detected"
        write_drift_status_to_file(status, status_file_path)
        trigger_retraining()
        return {
            "accuracy": prod_model_accuracy,
            "data_drift": data_drift_detected,
            "model_drift": model_drift_detected,
            "message": "Drift detected. Model retraining initiated."
        }
    else:
        status = "no_drift"
        write_drift_status_to_file(status, status_file_path)
        return {
            "accuracy": prod_model_accuracy,
            "data_drift": data_drift_detected,
            "model_drift": model_drift_detected,
            "message": "No drift detected."
        }





