# Changelog

## 1.0: 2026-09-27

Initial release, at the **Intern** level.

### Agent
- Read-only Gmail client: `gmail.readonly` only, message metadata only (bodies and snippets are never fetched or kept), exact-match scope check, one connection per run.
- Triage classifier v2: each inbox message is marked `needs_response`, `junk` or `fyi`, with SENSITIVE tagging for money and contract subjects.
- Decision log (`decisions.db`): the plan's schema, a no-body rule, hashed message IDs so nothing is triaged twice, and grading reviews.
- Weekly grading and summary (`src/review.py`): accuracy per bucket, small-sample flags, availability and run-time SLA.
- Kill switch: blocks restarts, halts a running agent, revokes the Google token and logs the event. Standard library only.
- Daily scheduled run via launchd at 07:00, with a failure notification. Unattended runs never open a sign-in page.

### Governance
- Promotion plan 1.0, following the Agentic Trust Framework v0.9.1.
- Gate checklists for all three promotions, ongoing validation after promotion, maturity status, and formats for metrics, incidents and the decision log.

### Docs
- README, `CLAUDE.md`, scope by level, architecture (including the Gmail permission ladder and planned architecture), ATF conformance crosswalk.

### Security
- Credentials, tokens, `decisions.db`, logs and runtime files are git-ignored; the token and database are owner-only.
- Pinned dependencies (`requirements.txt`).
- Live kill-switch drill passed: token revoked, access confirmed removed, re-authorized with `gmail.readonly`.
