from fastapi.testclient import TestClient

from app.main import app
from app.worker import process_one_pending_task


def test_task_can_be_created_and_processed():
    client = TestClient(app)
    payload = {
        "target_industry": "enterprise software",
        "target_geography": "Southeast Asia",
        "si_keywords": ["ERP", "CRM"],
        "exclusion_keywords": ["staffing only"],
        "company_size_preference": "mid-market or enterprise",
        "service_categories": ["ERP", "CRM", "cloud migration"],
        "max_results": 3,
        "output_format": "markdown",
    }

    create_response = client.post("/tasks", json=payload)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    assert process_one_pending_task() is True

    results_response = client.get(f"/tasks/{task_id}/results")
    assert results_response.status_code == 200
    results = results_response.json()
    assert len(results) > 0
    assert results[0]["scoring_breakdown"]["total"] == results[0]["relevance_score"]

    report_response = client.get(f"/tasks/{task_id}/reports/latest.docx")
    assert report_response.status_code == 200
    assert report_response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert report_response.content.startswith(b"PK")
