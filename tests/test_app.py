from fastapi.testclient import TestClient

from main import create_app


client = TestClient(create_app())


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_renders() -> None:
    response = client.get("/")
    assert response.status_code == 404

def test_transactions_api_exists() -> None:
    response = client.get("/api/v1/transactions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_transaction_detail_api_exists() -> None:
    response = client.get("/api/v1/transactions/TX1001")
    assert response.status_code == 200
    assert response.json()["id"] == "TX1001"


def test_evaluation_api_exists() -> None:
    response = client.get("/api/v1/evaluation")
    assert response.status_code == 200
    assert "metrics" in response.json()


def test_audit_api_exists() -> None:
    response = client.get("/api/v1/audit")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_settings_api_exists() -> None:
    response = client.get("/api/v1/settings")
    assert response.status_code == 200
    body = response.json()
    assert "model_context" in body
    assert "model_leaderboard" in body


def test_settings_upload_validation_route() -> None:
    csv_content = "step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud\n1,CASH_OUT,1000,A,B,2000,1000,C,0,1000,0,0\n2,TRANSFER,8000,D,E,5000,500,F,100,8200,1,0\n"
    response = client.post(
        "/api/v1/settings/test-data",
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["rows"]


def test_settings_model_test_route() -> None:
    response = client.post(
        "/api/v1/settings/test-model",
        json={
            "step": "6",
            "type": "TRANSFER",
            "amount": "9100",
            "oldbalanceOrg": "6000",
            "newbalanceOrig": "1200",
            "oldbalanceDest": "400",
            "newbalanceDest": "9500",
        },
    )
    assert response.status_code == 200
    assert response.json()["decision"] in {"REVIEW", "ALLOW"}


def test_metrics_route_exists() -> None:
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert response.json()["transactions"] == 12482


def test_review_workflow_updates_transaction_status() -> None:
    response = client.post("/api/v1/reviews/TX1001", json={"reviewer_outcome": "Confirm risky"})
    assert response.status_code == 200
    assert response.json()["review_status"] == "Confirm risky"
