import httpx

from app.config import Settings
from app.research.search_providers import SerpApiSearchProvider, StarterSearchProvider, get_search_provider


def test_provider_uses_starter_without_api_key():
    settings = Settings(SEARCH_API_KEY="")

    provider = get_search_provider(settings)

    assert isinstance(provider, StarterSearchProvider)


def test_provider_uses_serpapi_when_api_key_present():
    settings = Settings(SEARCH_API_KEY="test-key")

    provider = get_search_provider(settings)

    assert isinstance(provider, SerpApiSearchProvider)


def test_serpapi_provider_parses_organic_results(monkeypatch):
    def fake_get(url, params, headers, timeout):
        assert url == SerpApiSearchProvider.endpoint
        assert params["api_key"] == "test-key"
        assert params["q"] == "systems integrator Singapore"
        return httpx.Response(
            status_code=200,
            request=httpx.Request("GET", url),
            json={
                "organic_results": [
                    {
                        "title": "Acme SI",
                        "link": "https://acme.example.com",
                        "snippet": "ERP and CRM systems integrator in Singapore",
                    }
                ]
            },
        )

    monkeypatch.setattr(httpx, "get", fake_get)
    provider = SerpApiSearchProvider(Settings(SEARCH_API_KEY="test-key"))

    results = provider.search("systems integrator Singapore", max_results=5)

    assert len(results) == 1
    assert results[0].title == "Acme SI"
    assert results[0].url == "https://acme.example.com"
