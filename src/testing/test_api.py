import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch,AsyncMock
from main import app, users, pwd_context, PREDICTION_SERVICE_URL, RETRAIN_SERVICE_URL, MONITORING_SERVICE_URL

# Initialize the test client
client = TestClient(app)

# Sample credentials for users
VALID_CREDENTIALS_USER1 = ("user1", "datascientest")
VALID_CREDENTIALS_ADMIN = ("admin", "adminsecret")
INVALID_CREDENTIALS = ("user1", "wrongpassword")

############################################################################
# Test the /status endpoint with valid user credentials
def test_status_endpoint_valid_user():
    response = client.get("/status", auth=VALID_CREDENTIALS_USER1)
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur notre API Gateway, Sousou!"}

# Test the /status endpoint with invalid credentials
def test_status_endpoint_invalid_credentials():
    response = client.get("/status", auth=INVALID_CREDENTIALS)
    assert response.status_code == 401
    assert response.json() == {"detail": "Identifiant ou mot de passe incorrect"}
##############################################################################

@pytest.fixture
def mock_prediction_service():
    with patch("main.requests.post") as mock_post:
        yield mock_post

# Test the /prediction endpoint with a valid standard user and mock the prediction service
def test_prediction_endpoint(mock_prediction_service):
    mock_prediction_service.return_value.status_code = 200
    

    accident_data = {
        "place": 1,
        "catu": 2,
        "trajet": 10.0,
        "an_nais": 2016,
        "catv": 1,
        "choc": 1.0,
        "manv": 1.0,
        "mois": 5,
        "jour": 12,
        "lum": 2,
        "agg": 1,
        "int": 1,
        "col": 1.0,
        "com": 10,
        "dep": 75,
        "hr": 15,
        "mn": 30,
        "catr": 1,
        "circ": 1.0,
        "nbv": 2,
        "prof": 1.0,
        "plan": 1.0,
        "lartpc": 1,
        "larrout": 1,
        "situ": 1.0
    }

    response = client.post("/prediction", auth=VALID_CREDENTIALS_USER1, json=accident_data)
    assert response.status_code == 200
    #assert response.json()["Cet accident est de niveau de gravtité "] == 2
    
 ###########################################################################   
"""""
# Mocking the retrain service
@pytest.fixture
def mock_retrain_service():
    with patch("main.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        yield mock_post


@pytest.mark.asyncio
async def test_retrain_endpoint(mock_retrain_service):
    # Make sure the mock returns an async response
    mock_retrain_service.return_value.status_code = 200
    mock_retrain_service.return_value.json.return_value = {"message": "Retraining started"}

    # Await the client call to make sure it's properly handled as async
    response = await client.post("/retrain", auth=VALID_CREDENTIALS_ADMIN)
    
    assert response.status_code == 200
    assert response.json() == {"message": "Re-entrainement réussi"}

# Test access control for non-admin users trying to access admin-only endpoints
def test_retrain_endpoint_non_admin():
    response = client.post("/retrain", auth=VALID_CREDENTIALS_USER1)
    assert response.status_code == 403
    assert response.json() == {"detail": "Droits non autorisés"}
#########################################################################

# Mocking the monitoring service
@pytest.fixture
def mock_monitoring_service():
    with patch("main.httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        yield mock_get

@pytest.mark.asyncio
async def test_monitor_endpoint(mock_monitoring_service):
    # Make sure the mock returns an async response
    mock_monitoring_service.return_value.status_code = 200

    # Await the client call
    response = await client.get("/monitor", auth=VALID_CREDENTIALS_ADMIN)

    assert response.status_code == 200
    # accuracy_data = response.json()
    # assert accuracy_data["accuracy"] > 0.6
    

def test_monitor_endpoint_non_admin():
    response = client.get("/monitor", auth=VALID_CREDENTIALS_USER1)
    assert response.status_code == 403
    assert response.json() == {"detail": "Droits non autorisés"}
"""