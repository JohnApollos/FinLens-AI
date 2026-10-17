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

def test_chromadb_regulatory_retrieval():
    from backend.app.services.narrative import retrieve_regulatory_context
    banking_ctx = retrieve_regulatory_context("Banking")
    assert "Basel" in banking_ctx or "Capital Adequacy" in banking_ctx
    ins_ctx = retrieve_regulatory_context("Insurance")
    assert "Insurance Regulatory Authority" in ins_ctx or "IRA" in ins_ctx

def test_compile_pdf_report_direct(tmp_path):
    from backend.app.services.report import compile_pdf_report
    from backend.app.services.analysis import evaluate_financial_health
    from backend.app.services.narrative import generate_offline_narrative

    stmt = {
        "company_name": "Unit Test Co",
        "assets": 1000000.0,
        "liabilities": 400000.0,
        "equity": 600000.0,
        "revenue": 500000.0,
        "expenses": 420000.0,
        "net_income": 80000.0,
        "working_capital": 200000.0,
        "retained_earnings": 300000.0,
        "cash": 100000.0,
        "borrowings": 50000.0,
        "sic": "Manufacturing"
    }
    analysis = evaluate_financial_health(stmt, identifier="unit_test")
    narrative = generate_offline_narrative("Unit Test Co", "Manufacturing", analysis["ratios"], analysis["solvency"], analysis["anomaly"])
    pdf_out = str(tmp_path / "test_report.pdf")
    compile_pdf_report(pdf_out, "Unit Test Co", "Manufacturing", "FY 2023", "KES", stmt, analysis, narrative)
    assert os.path.exists(pdf_out)
    assert os.path.getsize(pdf_out) > 10000
