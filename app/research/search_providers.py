from dataclasses import dataclass
from typing import Protocol
import re
from urllib.parse import quote_plus

from app.config import Settings


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    query: str


class SearchProvider(Protocol):
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        ...


class StarterSearchProvider:
    """Deterministic provider used until an official search API is configured.

    Future integration point: replace this class with a provider backed by
    Bing Web Search, SerpAPI, Google Programmable Search, or another compliant
    API. Keep credentials in environment variables only.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        vendors = ["Microsoft", "Salesforce", "SAP", "NetSuite", "Odoo", "AWS"]
        services = ["ERP", "CRM", "cloud migration", "cybersecurity", "AI automation"]
        countries = ["Singapore", "Philippines", "Malaysia", "Thailand", "Indonesia", "Vietnam"]
        results: list[SearchResult] = []
        limit = max(1, min(max_results, 6))
        for index in range(limit):
            country = countries[index % len(countries)]
            service = services[index % len(services)]
            vendor = vendors[index % len(vendors)]
            slug = quote_plus(query.lower())
            domain_slug = re.sub(r"[^a-z0-9]+", "-", f"{country}-{service}-{index + 1}".lower()).strip("-")
            name = f"{country} {service.title()} Integration Partners"
            results.append(
                SearchResult(
                    title=name,
                    url=f"https://{domain_slug}.example.com/search-evidence/{slug}",
                    snippet=(
                        f"{name} is described as a systems integrator serving {country} "
                        f"with {service}, implementation, managed services, and {vendor} partner capabilities."
                    ),
                    query=query,
                )
            )
        return results


def get_search_provider(settings: Settings) -> SearchProvider:
    return StarterSearchProvider(settings)
