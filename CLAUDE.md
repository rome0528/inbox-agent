# CLAUDE.md

Personal Gmail triage agent that earns autonomy through a governed promotion path: Intern → Junior → Senior → Principal. The project is about **agentic maturation**: it isn't agentic at Intern (rule-based, no autonomy) and becomes agentic only as autonomy is earned at each gate. Don't describe the current system as an autonomous agent. Governed by the Agentic Trust Framework (ATF) v0.9.1; `docs/atf-conformance.md` maps each requirement, so keep it updated when governance changes. Start with `README.md`, then `docs/scope.md` and `docs/architecture.md`.

## Current state

- **Level: Intern (read-only).** Scope is `gmail.readonly` only; the agent reads metadata and never changes Gmail. Source of truth: `governance/maturity-status.md`.
- Triage classifier **v2** (`needs_response` / `junk` / `fyi`, with SENSITIVE tagging) in `src/agent.py`.
- Gate 1 thresholds for Junior: ≥ 90% replies caught, ≥ 90% junk calls right, every week. Earliest Junior review: 2026-10-11.
- Runs daily at 07:00 via launchd (`scripts/`). The owner grades calls on Sundays with `src/review.py`.

## Guardrails (non-negotiable)

- **The Gmail permission (`SCOPES` in `src/gmail_client.py`) changes only at a signed-off promotion or demotion**, by the procedure in `docs/architecture.md` (Gmail permission ladder). Never widen it otherwise.
- **No new capability without sign-off.** Don't add a Gmail scope, any write call (send, modify, label, delete, draft), body fetching, or a new data flow (e.g. sending email to an AI API) unless `governance/decision-log.md` has a dated promotion or decision that authorizes it. If asked to, point to the gate checklist in `governance/gates/` first.
- **Money/commitment carve-out is permanent.** SENSITIVE mail is never auto-sent or auto-actioned at any level, and never suggested as junk (plan §1).
- **No email content anywhere.** Never write message bodies, and never write real subject lines, into code, logs, docs, commits or chat. `decisions.db` stores subjects only, through `src/decision_log.py`.
- **Don't read secrets or personal data.** Don't open `token.json` or `credentials.json` values, and don't query subject lines from `decisions.db`. Aggregate counts are fine.
- **Before every commit**, confirm none of these are staged: `credentials.json`, `token.json`, `decisions.db*`, `logs/`, `.venv/`, `agent.pid`, `.killed`. Stage files explicitly; never `git add -A`.
- **Demotion rules are binding** (plan §5, from ATF): a critical incident → Intern; 3+ minor incidents or a security vulnerability → down one level. Don't talk the owner out of it or skip steps of the procedure.
- **No silent learning.** Triage rules, the sent-mail style guide, AI models and limits change only in versioned, owner-approved steps, each logged as a system change (`governance/ongoing-validation.md`). The style guide never contains quoted email text.
- **Kill switch must keep working.** `src/kill_switch.py` stays standard-library only and must always halt, block restarts, and revoke.

## How to work here

- Python: `.venv/bin/python`, pinned deps in `requirements.txt`. Run from the repo root: `.venv/bin/python src/agent.py`.
- Test changes in a scratch copy with a stubbed `gmail_client` rather than against the real inbox, and don't touch the real `decisions.db` in tests.
- Changing triage rules: bump `CLASSIFIER_VERSION` in `src/agent.py`, and note it in `governance/decision-log.md` and `CHANGELOG.md`. Gate metrics are split by classifier version.
- Keep the `decisions` table schema exactly as in `governance/agentic-promotion-plan.md` §8. Extra data goes in separate tables.
- When behavior, scope or data flow changes, update `docs/scope.md`, `docs/architecture.md` and `CHANGELOG.md` in the same commit.
- Governance evidence (`metrics.md`, `incidents.md`, `decision-log.md`) records the owner's decisions and observations. Don't invent entries or check gate boxes on the owner's behalf.
- The repo must stay outside `~/Documents` (macOS blocks launchd there).
