from app.models import ResearchTask
from app.research.extractor import ExtractedLead
from app.research.scorer import score_lead


def test_score_lead_returns_transparent_breakdown():
    task = ResearchTask(
        target_industry="enterprise",
        target_geography="Southeast Asia",
        si_keywords=["ERP", "CRM"],
        service_categories=["ERP", "CRM", "cloud migration"],
    )
    lead = ExtractedLead(
        company_name="SEA Cloud Integrator",
        website="https://sea.example.com",
        location="Singapore",
        countries_served=["Singapore"],
        services=["ERP", "CRM", "cloud migration"],
        vendor_partnerships=["Microsoft", "SAP"],
        industries_served=["enterprise"],
        contact_page_url="https://sea.example.com/contact",
        description="systems integrator for enterprise ERP and CRM",
        source_urls=["https://source.example.com"],
        confidence_score=90,
    )

    breakdown = score_lead(task, lead)

    assert breakdown["total"] > 70
    assert {"si_relevance", "geography_match", "service_match", "total"} <= set(breakdown)

