import pytest
from sklearn.ensemble import RandomForestClassifier
import numpy as np


# Ajout du chemin du répertoire parent de training.py
from ..scripts.Preprocessing import process_data
from ..scripts.Training import train_model, evaluate_model




# préaparation de data pour testing
file_path = "../data/data_2005a2021_final.csv"
X_train_resampled, X_test, y_train_resampled, y_test = process_data(file_path)

model, training_time = train_model(X_train_resampled, y_train_resampled)


#vérifier la précision du modèle
def test_evaluate_model():
    
    accuracy = evaluate_model(model, X_test, y_test)

    # Assert the accuracy is at least 0.60
    assert accuracy >= 0.60, f"l'accuracy est supérieure à 60%: {accuracy}"
