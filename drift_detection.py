import os
import pandas as pd
import numpy as np
from sklearn import datasets
import evidently
from evidently.report import Report
from evidently.metric_preset import DataQualityPreset
from evidently.ui.workspace import Workspace
from evidently.test_preset import DataQualityTestPreset
from evidently.metric_preset import DataDriftPreset


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

def generate_data_drift_report(reference_data: pd.DataFrame, new_data: pd.DataFrame, SAVE_FILE = True) -> (bool, Report):
    """
    Generate data drift report between reference and new datasets.
    
    :param reference_data: DataFrame containing the reference dataset.
    :param new_data: DataFrame containing the new dataset.
    :return: A tuple containing a boolean indicating if drift was detected, and the Report object.
    """
    data_drift_report = Report(metrics=[DataDriftPreset()])
    data_drift_report.run(reference_data=reference_data.drop('grav', axis=1), 
                          current_data=new_data.drop('grav', axis=1), column_mapping=None)
    report_json = data_drift_report.as_dict()
    drift_detected = report_json['metrics'][0]['result']['dataset_drift']
    
    # Save the report as HTML
    if SAVE_FILE:
        data_drift_report.save_html("data_drift_report.html")
    
    return drift_detected, data_drift_report

def add_report_to_workspace(workspace, project_name, project_description, report: Report):
    """
    Adds a report to an existing or new project in a workspace.
    """
    # Check if project already exists
    project = None
    for p in workspace.list_projects():
        if p.name == project_name:
            project = p
            break

    # Create a new project if it doesn't exist
    if project is None:
        project = workspace.create_project(project_name)
        project.description = project_description

    # Add report to the project
    workspace.add_report(project.id, report)
    print(f"New report added to project {project_name}")

def write_drift_status_to_file(status: str, file_path: str) -> None:
    """
    Write the drift detection status to a file.
    
    :param status: The drift status ('drift_detected' or 'no_drift').
    :param file_path: The path to the file where to write the status.
    """
    with open(file_path, 'w') as f:
        f.write(status)

if __name__ == "__main__":

    WORKSPACE_NAME = "my-workspace"
    PROJECT_NAME = "data_monitoring-v0"
    PROJECT_DESCRIPTION = "Evidently Dashboards"

    reference_path = os.path.join('src', 'data', 'processed', 'reference_from_train_data.csv')
    new_data_path = os.path.join('src', 'data', 'processed', 'new_data.csv')
    status_file_path = 'drift_detected.txt'
    
    reference_data, new_data = load_data(reference_path, new_data_path)
    drift_detected, data_drift_report = generate_data_drift_report(reference_data, new_data)
    
    if drift_detected:
        print("Data drift detected. Retraining the model.")
        write_drift_status_to_file('drift_detected', status_file_path)
    else:
        print("No data drift detected.")
        write_drift_status_to_file('no_drift', status_file_path)

    # Add report to workspace
    workspace = Workspace(WORKSPACE_NAME)
    add_report_to_workspace(workspace, PROJECT_NAME, PROJECT_DESCRIPTION, data_drift_report)
