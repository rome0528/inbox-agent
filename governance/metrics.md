# Weekly Metrics

One row per weekly review (Sundays). A week without a row doesn't count toward the minimum observation period (plan §4). In a week where a bucket has fewer than 5 graded items, note "pooled" in Notes; that bucket is judged on the window total (plan §4).

Source: grade with `.venv/bin/python src/review.py --days 7`, then report with `.venv/bin/python src/review.py --summary --days 7`.

- **Reviewed:** triage calls the owner graded this week.
- **Accuracy:** share of graded calls where the agent's bucket matched yours.
- **Replies caught:** of the emails that really needed a reply, the share the agent marked `needs_response`.
- **Junk right:** of the agent's `junk` calls, the share that really were junk.
- **Acceptance:** share of proposed actions the owner approved. Junior and above only; n/a at Intern.
- **Audit accuracy:** share of randomly audited autonomous actions (and, at Principal, sent replies) that were correct. Senior and above only; see `governance/ongoing-validation.md`.
- **Availability:** completed scheduled daily runs ÷ scheduled daily runs (ATF Gate 1: >99% for Intern → Junior, which in practice means every scheduled run).
- **Run-time SLA:** met if every run completed within 15 minutes.
- **Failed runs:** runs that started and failed (from `review.py`), plus any failure notifications seen in `logs/agent.log`.
- **Incidents:** entries added to `incidents.md` this week, by severity.

| Week ending | Level | Classifier | Reviewed | Accuracy | Replies caught | Junk right | Acceptance | Audit accuracy | Availability | Run-time SLA | Failed runs | Incidents | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
