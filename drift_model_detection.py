import os
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from evidently.report import Report
from evidently.metric_preset import ClassificationPreset
from evidently.ui.workspace import Workspace

def load_data(reference_path: str, new_data_path: str) -> (pd.DataFrame, pd.DataFrame):
    """
    Load reference and new data from specified paths.
    
    :param reference_path: Path to the reference dataset.
    :param new_data_path: Path to the new dataset.
    :return: A tuple of DataFrames (reference_data, new_data).
    """
    print(f"Loading reference data from: {os.path.abspath(reference_path)}")
    print(f"Loading new data from: {os.path.abspath(new_data_path)}")

    reference_data = pd.read_csv(reference_path)
    new_data = pd.read_csv(new_data_path)
    return reference_data, new_data

def load_model():
    """
    Load the pre-trained model.
    """
    model_path = os.path.join('models', 'model_rf_clf.pkl')
    model = joblib.load(model_path)

    if isinstance(model, dict):
        model = model.get('model')
        if model is None:
            raise ValueError("The loaded model is not valid or could not be found in the dictionary.")

    return model

def get_prediction(model, reference_data, current_data):
    """
    Generates predictions for reference and current data using the loaded model.
    """
    # Create a copy of the dataframes to avoid modifying the original data
    reference_data = reference_data.copy()
    current_data = current_data.copy()

    # Generate predictions for reference and current data
    reference_data['prediction'] = model.predict_proba(reference_data.drop(columns=['target']))[:, 1]
    current_data['prediction'] = model.predict_proba(current_data.drop(columns=['target']))[:, 1]

    return reference_data, current_data

def generate_classification_report(reference_data, current_data):
    """
    Generates a classification report using Evidently.
    """
    classification_report = Report(metrics=[
        ClassificationPreset(probas_threshold=0.5),
    ])

    classification_report.run(reference_data=reference_data, current_data=current_data)

    return classification_report

def add_report_to_workspace(workspace, project_name, project_description, report):
    """
    Adds a report to an existing or new project in a workspace.
    """
    project = None
    for p in workspace.list_projects():
        if p.name == project_name:
            project = p
            break

    if project is None:
        project = workspace.create_project(project_name)
        project.description = project_description

    workspace.add_report(project.id, report)
    print(f"New report added to project {project_name}")

if __name__ == "__main__":
    # Defining workspace and project details
    WORKSPACE_NAME = "my-workspace"
    PROJECT_NAME = "data_monitoring-v0"
    PROJECT_DESCRIPTION = "Evidently Dashboards"

    # Load reference and new data
    reference_data, new_data = load_data('src/data/processed/reference_from_train_data.csv', 
                                         'src/data/processed/new_data.csv')

    # Load the pre-trained model
    model = load_model()

    # Generate predictions for reference and current data
    reference_data, current_data = get_prediction(model, reference_data, new_data)

    # Generate the classification report
    classification_report = generate_classification_report(reference_data, current_data)

    # Set up the workspace
    workspace = Workspace(WORKSPACE_NAME)

    # Add report to the workspace
    add_report_to_workspace(workspace, PROJECT_NAME, PROJECT_DESCRIPTION, classification_report)
