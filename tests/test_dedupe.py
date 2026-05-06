from app.models import Company
from app.research.dedupe import normalize_domain, normalize_name, names_match
from app.research.extractor import ExtractedLead
from app.research.dedupe import find_existing_company


def test_normalize_domain_removes_scheme_and_www():
    assert normalize_domain("https://www.example.com/path") == "example.com"


def test_normalize_name_removes_legal_suffixes():
    assert normalize_name("Acme Systems Integrators Pte Ltd.") == "acme systems integrators"


def test_find_existing_company_by_fuzzy_name():
    lead = ExtractedLead(company_name="Acme System Integration", website=None, location=None)
    company = Company(name="Acme Systems Integration Ltd", normalized_name="acme systems integration")

    assert names_match(company.name, lead.company_name)
    assert find_existing_company(lead, [company]) is company

