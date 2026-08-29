from fastapi.testclient import TestClient

from main import create_app


client = TestClient(create_app())


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_renders() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "ai-risk-manager" in response.text


def test_transactions_route_exists() -> None:
    response = client.get("/transactions")
    assert response.status_code == 200
    assert "Transaction Queue" in response.text


def test_transaction_detail_route_exists() -> None:
    response = client.get("/transactions/TX1001")
    assert response.status_code == 200
    assert "TX1001" in response.text


def test_evaluation_route_exists() -> None:
    response = client.get("/evaluation")
    assert response.status_code == 200
    assert "Evaluation" in response.text


def test_audit_route_exists() -> None:
    response = client.get("/audit")
    assert response.status_code == 200
    assert "Audit Log" in response.text


def test_settings_route_exists() -> None:
    response = client.get("/settings")
    assert response.status_code == 200
    assert "Settings" in response.text
    assert "ai-risk-manager-v1" in response.text or "HistGradientBoostingClassifier" in response.text
    assert "Upload CSV" in response.text


def test_settings_upload_validation_route() -> None:
    csv_content = "step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud\n1,CASH_OUT,1000,A,B,2000,1000,C,0,1000,0,0\n2,TRANSFER,8000,D,E,5000,500,F,100,8200,1,0\n"
    response = client.post(
        "/settings/test-data",
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    assert "Rows" in response.text


def test_settings_model_test_route() -> None:
    response = client.post(
        "/settings/test-model",
        data={
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
    assert "Risk score" in response.text or "Decision" in response.text


def test_metrics_route_exists() -> None:
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert response.json()["transactions"] == 12482


def test_review_workflow_updates_transaction_status() -> None:
    response = client.post("/reviews/TX1001", data={"reviewer_outcome": "Confirm risky"})
    assert response.status_code == 200
    assert "Review status: Confirm risky" in response.text
