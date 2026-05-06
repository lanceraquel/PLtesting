from app.models import ResearchTask
from app.research.query_builder import build_queries


def test_build_queries_includes_templates_and_keywords():
    task = ResearchTask(
        target_industry="healthcare",
        target_geography="Southeast Asia",
        si_keywords=["AI automation"],
    )

    queries = build_queries(task)

    assert "systems integrator healthcare Southeast Asia" in queries
    assert "AI automation systems integrator Southeast Asia" in queries
    assert len(queries) == len(set(queries))

