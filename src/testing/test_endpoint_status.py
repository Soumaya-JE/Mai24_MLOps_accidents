import pytest
import requests


# Sample credentials for users
VALID_CREDENTIALS_USER1 = ("user1", "datascientest")
VALID_CREDENTIALS_ADMIN = ("admin", "adminsecret")
INVALID_CREDENTIALS = ("user1", "wrongpassword")

# Défine API GATEWAY URL
API_GATEWAY_STATUS = "http://localhost:8000/status"


# Test the /status endpoint with valid user credentials
def test_status_endpoint_valid_user():
    response = requests.get(
        url=API_GATEWAY_STATUS,
        auth=VALID_CREDENTIALS_USER1  
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur notre API Gateway, Sousou!"}
   
# Test the /status endpoint with invalid credentials
def test_status_endpoint_invalid_credentials():
    response = requests.get(
        url=API_GATEWAY_STATUS,
        auth=INVALID_CREDENTIALS   
    )
    assert response.status_code == 401
    assert response.json() == {"detail":"Identifiant ou mot de passe incorrect"}
   

  

    