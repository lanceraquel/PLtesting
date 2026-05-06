You are Codex acting as a senior full-stack engineer and agent-systems architect.

Build a production-ready “SI Research Agent” that runs in the cloud, not on my local machine.

Context:
- “SI” means Systems Integrator.
- The agent should research and collect Systems Integrator leads from the web.
- The project will live in GitHub.
- Railway will deploy the app from GitHub and keep the worker/API running virtually.
- The system should be deployable with Railway using environment variables.
- Do not assume any local-only runtime. Everything must be runnable from the repo and deployable to Railway.

Goal:
Create a GitHub-ready application that can:
1. Search for Systems Integrators based on configurable criteria.
2. Extract useful lead/company data.
3. Save results persistently.
4. Deduplicate results.
5. Score or rank each SI lead.
6. Produce a reviewable report.
7. Run repeatedly in the cloud via Railway.
8. Expose a minimal API/dashboard so I can trigger research tasks and inspect results.

Preferred stack:
- Python 3.11+
- FastAPI for API endpoints
- PostgreSQL for storage
- SQLAlchemy or SQLModel for database access
- Alembic for migrations
- Pydantic for config/models
- A background worker process for running research jobs
- Optional: Playwright only if needed; otherwise keep browser automation minimal
- Use Dockerfile and/or Railway-compatible configuration
- Include tests

Core features:

A. Research task input
Create a way to define a research task with:
- target industry
- target geography
- SI keywords
- exclusion keywords
- company size preference
- service categories
- maximum results
- freshness/date filters when possible
- output format preference

Example task:
“Find 100 Systems Integrators in Southeast Asia focused on ERP, CRM, cloud migration, cybersecurity, and AI automation. Prioritize companies serving mid-market or enterprise clients. Exclude staffing-only agencies.”

B. Search strategy
Implement a modular search pipeline that can use query templates such as:
- “systems integrator [industry] [location]”
- “ERP systems integrator [location]”
- “CRM implementation partner [location]”
- “cloud migration systems integrator [location]”
- “cybersecurity systems integrator [location]”
- “Microsoft partner systems integrator [location]”
- “Salesforce implementation partner [location]”
- “NetSuite partner [location]”
- “SAP implementation partner [location]”
- “Odoo partner [location]”

Important:
- Keep search providers abstracted behind an interface.
- Create a simple provider implementation that can be replaced later.
- If paid APIs are needed later, read API keys from environment variables only.
- Do not hardcode secrets.

C. Data extraction
For every potential SI, extract and normalize:
- company name
- website
- location / headquarters
- countries served
- services offered
- vendor partnerships, if visible
- industries served
- contact page URL
- LinkedIn URL, if found
- email, only if publicly available
- phone, only if publicly available
- short company description
- evidence/source URLs
- confidence score
- relevance score
- notes explaining why this is likely an SI

D. Deduplication
Deduplicate by:
- normalized domain
- normalized company name
- LinkedIn URL
- fuzzy name matching

E. Lead scoring
Create a transparent scoring model from 0 to 100 based on:
- relevance to Systems Integrator work
- match to requested geography
- match to requested industry
- number/quality of services found
- recognized vendor partnerships
- evidence quality
- availability of contact details
- company maturity signals

Store the scoring breakdown, not just the final score.

F. Persistence
Use PostgreSQL with these tables or equivalent:
- research_tasks
- companies
- company_sources
- company_contacts
- research_results
- run_logs

G. API
Create FastAPI endpoints:
- POST /tasks — create a research task
- GET /tasks — list tasks
- GET /tasks/{task_id} — get task details
- POST /tasks/{task_id}/run — manually start a research run
- GET /tasks/{task_id}/results — list results
- GET /companies — list discovered companies
- GET /companies/{company_id} — get company detail
- GET /health — health check

H. Worker
Create a worker that can:
- poll for queued tasks
- run research jobs
- update task status
- log progress
- recover safely after crashes
- avoid duplicate concurrent runs of the same task

The worker should support two Railway deployment patterns:
1. Always-on worker service:
   - start command: python -m app.worker
2. Cron-compatible one-shot runner:
   - start command: python -m app.run_pending_tasks
   - exits after processing due work

Railway cron jobs expect a process that performs work and exits, so include the one-shot runner as an option. The always-on worker is acceptable when I want the agent continuously available.

I. Reports
Generate reports in:
- JSON
- CSV
- Markdown

Each report should include:
- task summary
- search queries used
- companies found
- top-ranked SIs
- scoring breakdown
- source URLs
- caveats / low-confidence results

J. Safety and compliance
- Respect robots.txt where applicable.
- Use reasonable rate limits.
- Add user-agent configuration.
- Do not scrape private, paywalled, or login-only data.
- Do not collect sensitive personal data.
- Only collect business contact information that is publicly available.
- Keep full evidence/source URLs for auditability.
- Add clear comments where a future developer can plug in official APIs.

K. Railway deployment
Add:
- Dockerfile or Railway-compatible start commands
- README section for Railway deployment
- Required environment variables:
  - DATABASE_URL
  - OPENAI_API_KEY, optional, only if using LLM summarization/scoring
  - SEARCH_API_KEY, optional placeholder
  - USER_AGENT
  - RATE_LIMIT_SECONDS
  - WORKER_POLL_INTERVAL_SECONDS
  - DEFAULT_MAX_RESULTS
- Health check endpoint
- Migration command instructions
- Separate API and worker service instructions

L. GitHub readiness
Add:
- README.md
- .env.example
- .gitignore
- requirements.txt or pyproject.toml
- tests
- clear project structure
- sample research task JSON
- sample output report
- GitHub Actions workflow for tests

M. Architecture preference
Use this structure unless there is a better reason not to:

app/
  main.py
  config.py
  database.py
  models.py
  schemas.py
  api/
    routes_tasks.py
    routes_companies.py
    routes_health.py
  research/
    search_providers.py
    query_builder.py
    extractor.py
    dedupe.py
    scorer.py
    pipeline.py
  reports/
    exporter.py
  worker.py
  run_pending_tasks.py
  logging_config.py
tests/
  test_query_builder.py
  test_dedupe.py
  test_scorer.py
  test_api_health.py
alembic/
README.md
.env.example
Dockerfile
railway.json, if useful
.github/workflows/tests.yml

N. Acceptance criteria
The task is complete only when:
- The app starts locally with documented commands.
- The app can be deployed to Railway from GitHub.
- The API health endpoint works.
- A task can be created.
- A worker can process the task.
- Results are stored in PostgreSQL.
- A Markdown and CSV report can be generated.
- Tests pass.
- README explains exactly how to connect GitHub, deploy on Railway, configure variables, run migrations, and run API + worker services.
- No secrets are committed.
- The code is modular enough to replace the search provider later.

Implementation instructions:
1. Inspect the repository first.
2. If the repo is empty, create the project from scratch.
3. Make small, clean commits or a single clear PR-ready change.
4. Include comments where future API integrations should be added.
5. Use environment variables for all credentials.
6. Prefer simple, reliable code over complex agent abstractions.
7. After implementation, run tests and fix failures.
8. Summarize what was built, how to deploy it, and what still needs real API keys or production credentials.

Do not ask me questions unless a blocker prevents implementation. Make reasonable assumptions and document them in README.md.

Important deployment requirement:
This agent must be designed to run on Railway, not on a local machine. GitHub will be the source repository, Codex will make changes through GitHub, and Railway will deploy and run the API, worker, database, and optional cron jobs in the cloud.
