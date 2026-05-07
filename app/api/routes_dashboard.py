from html import escape

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_session
from app.models import Company, ResearchResult, ResearchTask

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, task_id: int | None = None, session: Session = Depends(get_session)) -> HTMLResponse:
    tasks = list(session.scalars(select(ResearchTask).order_by(ResearchTask.created_at.desc()).limit(50)).all())
    selected_task_id = task_id or (tasks[0].id if tasks else None)
    companies = list(
        session.scalars(
            select(Company)
            .options(selectinload(Company.sources), selectinload(Company.contacts))
            .order_by(Company.confidence_score.desc(), Company.name.asc())
            .limit(100)
        ).all()
    )
    results: list[ResearchResult] = []
    if selected_task_id:
        results = list(
            session.scalars(
                select(ResearchResult)
                .where(ResearchResult.task_id == selected_task_id)
                .options(
                    selectinload(ResearchResult.company).selectinload(Company.sources),
                    selectinload(ResearchResult.company).selectinload(Company.contacts),
                )
                .order_by(ResearchResult.rank.asc().nullslast(), ResearchResult.relevance_score.desc())
                .limit(100)
            ).all()
        )

    total_companies = session.scalar(select(func.count(Company.id))) or 0
    total_tasks = session.scalar(select(func.count(ResearchTask.id))) or 0
    completed_tasks = session.scalar(select(func.count(ResearchTask.id)).where(ResearchTask.status == "completed")) or 0

    html = _render_dashboard(
        base_url=str(request.base_url).rstrip("/"),
        tasks=tasks,
        companies=companies,
        results=results,
        selected_task_id=selected_task_id,
        total_companies=total_companies,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
    )
    return HTMLResponse(html)


def _render_dashboard(
    *,
    base_url: str,
    tasks: list[ResearchTask],
    companies: list[Company],
    results: list[ResearchResult],
    selected_task_id: int | None,
    total_companies: int,
    total_tasks: int,
    completed_tasks: int,
) -> str:
    task_rows = "\n".join(_task_row(task, selected_task_id) for task in tasks) or _empty_row("No tasks yet", 8)
    result_rows = "\n".join(_result_row(result) for result in results) or _empty_row("No results for this task yet", 7)
    company_rows = "\n".join(_company_row(company) for company in companies) or _empty_row("No companies discovered yet", 6)
    selected_task = next((task for task in tasks if task.id == selected_task_id), None)
    selected_summary = (
        f"Task {selected_task.id}: {escape(selected_task.target_geography)} / {escape(selected_task.target_industry)}"
        if selected_task
        else "No task selected"
    )
    report_link = (
        f"""<a href="/tasks/{selected_task.id}/reports/latest.docx">Download latest DOCX</a>"""
        if selected_task and selected_task.status == "completed"
        else "DOCX appears after a completed run"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SI Research Agent Dashboard</title>
  <style>
    :root {{
      --bg: #f5f7f2;
      --ink: #16201c;
      --muted: #68736d;
      --line: #d9ded6;
      --panel: #ffffff;
      --panel-2: #eef3ea;
      --accent: #0f6b57;
      --accent-2: #d46b35;
      --danger: #a13d2d;
      --shadow: 0 18px 40px rgba(28, 45, 38, 0.10);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        linear-gradient(135deg, rgba(15,107,87,.10), transparent 36%),
        linear-gradient(315deg, rgba(212,107,53,.10), transparent 34%),
        var(--bg);
      color: var(--ink);
      font-family: "Aptos", "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    header {{
      padding: 28px clamp(18px, 4vw, 54px) 18px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 20px;
    }}
    h1 {{ margin: 0; font-size: clamp(28px, 4vw, 46px); letter-spacing: 0; }}
    h2 {{ margin: 0 0 14px; font-size: 18px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    .subtle {{ color: var(--muted); font-size: 14px; }}
    .shell {{ padding: 0 clamp(18px, 4vw, 54px) 42px; }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .stat {{ background: var(--panel); border: 1px solid var(--line); padding: 16px; box-shadow: var(--shadow); }}
    .stat strong {{ display: block; font-size: 30px; }}
    .grid {{ display: grid; grid-template-columns: minmax(320px, 420px) 1fr; gap: 18px; align-items: start; }}
    section {{ background: var(--panel); border: 1px solid var(--line); box-shadow: var(--shadow); }}
    .panel-body {{ padding: 18px; }}
    label {{ display: block; margin: 12px 0 6px; color: var(--muted); font-size: 13px; font-weight: 700; }}
    input, textarea {{
      width: 100%;
      border: 1px solid var(--line);
      background: #fbfcfa;
      color: var(--ink);
      padding: 10px 11px;
      font: inherit;
    }}
    textarea {{ min-height: 78px; resize: vertical; }}
    button {{
      border: 0;
      background: var(--accent);
      color: #fff;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
      margin-top: 14px;
    }}
    button.secondary {{ background: var(--ink); padding: 7px 10px; margin: 0; font-size: 12px; }}
    .message {{ margin-top: 12px; color: var(--muted); font-size: 13px; min-height: 18px; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-top: 1px solid var(--line); padding: 10px 12px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); background: var(--panel-2); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
    .status {{ display: inline-block; padding: 3px 8px; background: var(--panel-2); font-size: 12px; font-weight: 700; }}
    .status.failed {{ color: var(--danger); }}
    .status.completed {{ color: var(--accent); }}
    .stack {{ display: grid; gap: 18px; }}
    .toolbar {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 14px 18px; border-bottom: 1px solid var(--line); }}
    .pill {{ display: inline-block; border: 1px solid var(--line); padding: 4px 8px; margin: 2px; background: #fbfcfa; font-size: 12px; }}
    @media (max-width: 940px) {{
      header {{ display: block; }}
      .stats, .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>SI Research Agent</h1>
      <div class="subtle">Cloud dashboard backed by Railway Postgres</div>
    </div>
    <div class="subtle">
      <a href="{base_url}/docs">API docs</a> · <a href="{base_url}/health">Health</a> · <a href="{base_url}/companies">Companies JSON</a>
    </div>
  </header>
  <main class="shell">
    <div class="stats">
      <div class="stat"><span class="subtle">Tasks</span><strong>{total_tasks}</strong></div>
      <div class="stat"><span class="subtle">Completed</span><strong>{completed_tasks}</strong></div>
      <div class="stat"><span class="subtle">Companies</span><strong>{total_companies}</strong></div>
    </div>
    <div class="grid">
      <section>
        <div class="toolbar"><h2>Create Research Task</h2></div>
        <div class="panel-body">
          <form id="task-form">
            <label>Target industry</label>
            <input name="target_industry" value="mid-market and enterprise technology buyers">
            <label>Target geography</label>
            <input name="target_geography" value="Southeast Asia">
            <label>SI keywords, comma-separated</label>
            <textarea name="si_keywords">ERP, CRM, cloud migration, cybersecurity, AI automation</textarea>
            <label>Exclusion keywords, comma-separated</label>
            <textarea name="exclusion_keywords">staffing only, recruitment agency</textarea>
            <label>Company size preference</label>
            <input name="company_size_preference" value="mid-market or enterprise">
            <label>Service categories, comma-separated</label>
            <textarea name="service_categories">ERP, CRM, cloud migration, cybersecurity, AI automation</textarea>
            <label>Maximum results</label>
            <input name="max_results" type="number" min="1" max="500" value="25">
            <label>Run interval, minutes</label>
            <input name="run_interval_minutes" type="number" min="15" value="60">
            <button type="submit">Create Task</button>
            <div id="form-message" class="message"></div>
          </form>
        </div>
      </section>
      <div class="stack">
        <section>
          <div class="toolbar"><h2>Tasks</h2><span class="subtle">Worker processes queued tasks automatically</span></div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Status</th><th>Geography</th><th>Industry</th><th>Max</th><th>Interval</th><th>Next Run</th><th>Action</th></tr></thead>
              <tbody>{task_rows}</tbody>
            </table>
          </div>
        </section>
        <section>
          <div class="toolbar"><h2>Results</h2><span class="subtle">{selected_summary} · {report_link}</span></div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>Rank</th><th>Company</th><th>Score</th><th>Website</th><th>Services</th><th>Sources</th><th>Notes</th></tr></thead>
              <tbody>{result_rows}</tbody>
            </table>
          </div>
        </section>
        <section>
          <div class="toolbar"><h2>Companies</h2><span class="subtle">Latest 100 discovered companies</span></div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>Name</th><th>Website</th><th>HQ</th><th>Confidence</th><th>Services</th><th>Sources</th></tr></thead>
              <tbody>{company_rows}</tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  </main>
  <script>
    const splitList = (value) => value.split(",").map((item) => item.trim()).filter(Boolean);
    document.querySelector("#task-form").addEventListener("submit", async (event) => {{
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const message = document.querySelector("#form-message");
      const payload = {{
        target_industry: form.get("target_industry"),
        target_geography: form.get("target_geography"),
        si_keywords: splitList(form.get("si_keywords") || ""),
        exclusion_keywords: splitList(form.get("exclusion_keywords") || ""),
        company_size_preference: form.get("company_size_preference"),
        service_categories: splitList(form.get("service_categories") || ""),
        max_results: Number(form.get("max_results") || 25),
        run_interval_minutes: Number(form.get("run_interval_minutes") || 60),
        output_format: "markdown"
      }};
      message.textContent = "Creating task...";
      const response = await fetch("/tasks", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(payload)
      }});
      if (!response.ok) {{
        message.textContent = "Task creation failed.";
        return;
      }}
      const task = await response.json();
      message.textContent = `Task ${{task.id}} queued. Refreshing...`;
      window.location.href = `/dashboard?task_id=${{task.id}}`;
    }});
    async function rerunTask(taskId) {{
      await fetch(`/tasks/${{taskId}}/run`, {{ method: "POST" }});
      window.location.href = `/dashboard?task_id=${{taskId}}`;
    }}
  </script>
</body>
</html>"""


def _task_row(task: ResearchTask, selected_task_id: int | None) -> str:
    selected = " selected" if task.id == selected_task_id else ""
    return f"""<tr{selected}>
      <td><a href="/dashboard?task_id={task.id}">{task.id}</a></td>
      <td><span class="status {escape(task.status)}">{escape(task.status)}</span></td>
      <td>{escape(task.target_geography)}</td>
      <td>{escape(task.target_industry)}</td>
      <td>{task.max_results}</td>
      <td>{task.run_interval_minutes or "Manual"} min</td>
      <td>{escape(str(task.next_run_at or "Queued"))}</td>
      <td><button class="secondary" onclick="rerunTask({task.id})">Run</button></td>
    </tr>"""


def _result_row(result: ResearchResult) -> str:
    company = result.company
    sources = ", ".join(_link(source.source_url, "source") for source in company.sources[:3]) or "None"
    return f"""<tr>
      <td>{result.rank or ""}</td>
      <td>{escape(company.name)}</td>
      <td>{result.relevance_score:.1f}</td>
      <td>{_link(company.website, "website") if company.website else "Unknown"}</td>
      <td>{_pills(company.services)}</td>
      <td>{sources}</td>
      <td>{escape(result.notes or company.notes or "")}</td>
    </tr>"""


def _company_row(company: Company) -> str:
    sources = ", ".join(_link(source.source_url, "source") for source in company.sources[:2]) or "None"
    return f"""<tr>
      <td>{escape(company.name)}</td>
      <td>{_link(company.website, "website") if company.website else "Unknown"}</td>
      <td>{escape(company.headquarters or "Unknown")}</td>
      <td>{company.confidence_score:.1f}</td>
      <td>{_pills(company.services)}</td>
      <td>{sources}</td>
    </tr>"""


def _empty_row(message: str, colspan: int) -> str:
    return f"""<tr><td colspan="{colspan}" class="subtle">{escape(message)}</td></tr>"""


def _link(url: str | None, label: str) -> str:
    if not url:
        return ""
    safe_url = escape(url, quote=True)
    return f"""<a href="{safe_url}" target="_blank" rel="noreferrer">{escape(label)}</a>"""


def _pills(values: list[str]) -> str:
    if not values:
        return "Unknown"
    return " ".join(f"""<span class="pill">{escape(value)}</span>""" for value in values[:6])
