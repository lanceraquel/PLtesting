# SI Research Agent

Cloud-deployable FastAPI and worker application for researching Systems Integrator leads, persisting them in PostgreSQL, deduplicating companies, scoring relevance, and exporting reviewable reports.

The starter search provider is intentionally replaceable. It produces deterministic evidence records so the API, worker, database, reports, and Railway deployment can be tested immediately. For production web research, plug an official search API into `app/research/search_providers.py` and provide credentials through environment variables.

## Features

- FastAPI endpoints for tasks, companies, results, reports, and health checks.
- PostgreSQL persistence through SQLAlchemy models and Alembic migrations.
- Background worker for queued research tasks.
- Railway-compatible one-shot runner for cron jobs.
- Modular research pipeline: query builder, search provider interface, extraction, dedupe, scoring, reports.
- Markdown, CSV, and JSON report generation.
- Tests and GitHub Actions workflow.

## Project Structure

```text
app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  api/
  research/
  reports/
  worker.py
  run_pending_tasks.py
alembic/
tests/
sample_task.json
sample_output_report.md
```

## Environment Variables

Copy `.env.example` to `.env` for local development. In Railway, configure the same variables in the service settings.

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@host:5432/si_research
OPENAI_API_KEY=
SEARCH_API_KEY=
USER_AGENT=SIResearchAgent/1.0 (+https://example.com/contact)
RATE_LIMIT_SECONDS=1.0
WORKER_POLL_INTERVAL_SECONDS=15
DEFAULT_MAX_RESULTS=25
REPORT_OUTPUT_DIR=reports
```

`OPENAI_API_KEY` is reserved for future LLM summarization or scoring. `SEARCH_API_KEY` is reserved for a compliant search provider such as Bing Web Search, SerpAPI, or Google Programmable Search. No secrets are committed.

## Local Run

Python 3.11+ is required.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The health endpoint is:

```bash
curl http://localhost:8000/health
```

Create a task:

```bash
curl -X POST http://localhost:8000/tasks ^
  -H "Content-Type: application/json" ^
  --data @sample_task.json
```

Run queued work once:

```bash
python -m app.run_pending_tasks
```

Run an always-on worker:

```bash
python -m app.worker
```

## API

- `POST /tasks` creates a research task.
- `GET /tasks` lists tasks.
- `GET /tasks/{task_id}` returns task details.
- `POST /tasks/{task_id}/run` queues a task for another run.
- `GET /tasks/{task_id}/results` lists scored results.
- `POST /tasks/{task_id}/reports` regenerates JSON, CSV, and Markdown reports.
- `GET /companies` lists discovered companies.
- `GET /companies/{company_id}` returns company details.
- `GET /health` checks API and database connectivity.

## Railway Deployment

1. Push this folder to a GitHub repository.
2. In Railway, create a new project from the GitHub repo.
3. Add a Railway PostgreSQL database.
4. Set `DATABASE_URL` to the Railway Postgres connection string. Railway may provide a `postgres://` URL; the app normalizes it automatically.
5. Set `USER_AGENT`, `RATE_LIMIT_SECONDS`, `WORKER_POLL_INTERVAL_SECONDS`, `DEFAULT_MAX_RESULTS`, and `REPORT_OUTPUT_DIR`.
6. Leave `OPENAI_API_KEY` and `SEARCH_API_KEY` blank until you add providers that use them.
7. Deploy the API service with start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

8. Run migrations after the database is available:

```bash
alembic upgrade head
```

9. Add a second Railway service for the always-on worker:

```bash
python -m app.worker
```

10. For Railway cron, use the one-shot runner:

```bash
python -m app.run_pending_tasks
```

Railway cron jobs should start, process pending work, and exit. The always-on worker should be used when you want continuous processing.

## Production Search Provider

The placeholder provider lives in `app/research/search_providers.py`. Replace `StarterSearchProvider` or update `get_search_provider()` to use an official web search API. Keep these constraints:

- Read API keys only from environment variables.
- Respect robots.txt and API terms.
- Use `USER_AGENT` and `RATE_LIMIT_SECONDS`.
- Avoid private, paywalled, or login-only data.
- Collect only public business contact information.
- Preserve evidence/source URLs for auditability.

## Scoring

Scores are stored from 0 to 100 with the full breakdown:

- SI relevance
- geography match
- industry match
- service match
- vendor partnerships
- evidence quality
- contact details
- maturity signals

The breakdown is persisted on each `research_results` record, so reviewers can see why a lead ranked highly.

## Tests

```bash
pytest
```

The test suite uses SQLite for speed. Railway and production deployments should use PostgreSQL.

