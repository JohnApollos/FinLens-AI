import os
import sys
import pytest
from starlette.testclient import TestClient

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import app
from backend.app.services.ingestion import extract_financial_metrics

client = TestClient(app)

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "model_loaded" in data

def test_api_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents_analyzed" in data
    assert "mean_solvency_score" in data

def test_api_history():
    response = client.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_sample_equity_ingestion():
    pdf_path = os.path.join("sample_reports", "Equity_Group_Holdings_2023_Financial_Report.pdf")
    assert os.path.exists(pdf_path), f"File {pdf_path} not found"
    
    extracted = extract_financial_metrics(pdf_path)
    assert extracted["is_valid"] is True
    assert len(extracted["validation_warnings"]) == 0
    # Assets must be scaled to trillions KES
    assert extracted["assets"] > 1.5e12
    # Borrowings must be scaled
    assert extracted["borrowings"] > 1e11
    # CAR must be a percentage between 10% and 30% (e.g. 18.1%)
    assert 10.0 <= extracted["capital_adequacy_ratio"] <= 30.0

def test_sample_eabl_ingestion():
    pdf_path = os.path.join("sample_reports", "EABL_2023_Annual_Report.pdf")
    assert os.path.exists(pdf_path), f"File {pdf_path} not found"
    
    extracted = extract_financial_metrics(pdf_path)
    assert extracted["is_valid"] is True
    assert len(extracted["validation_warnings"]) == 0
    # Revenue must be scaled to billions KES
    assert extracted["revenue"] > 1e11
    # Working capital extracted correctly
    assert extracted["working_capital"] != 0

def test_sample_jubilee_ingestion():
    pdf_path = os.path.join("sample_reports", "Jubilee_Insurance_2023_Annual_Report.pdf")
    assert os.path.exists(pdf_path), f"File {pdf_path} not found"
    
    extracted = extract_financial_metrics(pdf_path)
    assert extracted["is_valid"] is True
    assert len(extracted["validation_warnings"]) == 0
    # Solvency ratio must be a percentage between 100% and 300% (e.g. 165%)
    assert 100.0 <= extracted["solvency_ratio"] <= 300.0

def test_api_analyze_with_sample():
    pdf_path = os.path.join("sample_reports", "EABL_2023_Annual_Report.pdf")
    assert os.path.exists(pdf_path)
    
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
        
    response = client.post(
        "/analyze",
        files={"file": ("EABL_2023_Annual_Report.pdf", file_bytes, "application/pdf")},
        data={"sector": "Manufacturing", "gemini_key": ""}
    )
    assert response.status_code == 200
    res_json = response.json()
    assert "metrics" in res_json
    assert "analysis" in res_json
    assert "narrative" in res_json
    assert res_json["validation"]["is_valid"] is True

def test_api_report_generation_with_sample():
    pdf_path = os.path.join("sample_reports", "EABL_2023_Annual_Report.pdf")
    assert os.path.exists(pdf_path)
    
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
        
    response = client.post(
        "/report",
        files={"file": ("EABL_2023_Annual_Report.pdf", file_bytes, "application/pdf")},
        data={"sector": "Manufacturing", "gemini_key": ""}
    )
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
