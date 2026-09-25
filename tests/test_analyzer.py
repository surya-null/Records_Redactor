from fastapi.testclient import TestClient

from records_redactor.analyzer import analyze_text
from records_redactor.main import app


def test_root_describes_api():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "Upload a patient-record PDF" in response.text
    assert "Analyze document" in response.text


def test_flags_out_of_range_results_and_pii():
    result = analyze_text(
        "Patient DOB: 01/02/1980. MRN: ABC-1234. Hemoglobin: 10.2 g/dL. "
        "Glucose: 85 mg/dL. Contact jane@example.com or 555-123-4567.",
        [{"name": "Hemoglobin", "aliases": [], "unit": "g/dL", "low": 12, "high": 17.5},
         {"name": "Glucose", "aliases": [], "unit": "mg/dL", "low": 70, "high": 99}],
    )

    assert result["abnormal_results"] == [{
        "test": "Hemoglobin", "value": 10.2, "unit": "g/dL", "low": 12, "high": 17.5,
        "status": "low", "source_text": "Hemoglobin: 10.2 g/dL",
    }]
    assert result["pii_detected"] is True
    assert {finding["category"] for finding in result["pii_findings"]} == {
        "date_of_birth", "medical_record_number", "email", "phone",
    }


def test_normal_results_are_not_reported():
    result = analyze_text("Glucose 85 mg/dL", [{"name": "Glucose", "aliases": [], "unit": "mg/dL", "low": 70, "high": 99}])
    assert result["abnormal_results"] == []
    assert result["pii_detected"] is False