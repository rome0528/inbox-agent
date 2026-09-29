# Decision Log

Newest first. Weekly reviews get one line, even "not promoting yet" (plan §7). Promotion decisions get a full entry: what was reviewed, what was decided, why (Gate 5).

## 2026-09-27: Deployed at Intern; governance baseline

- **Decision:** deploy the inbox agent at **Intern** (read-only), governed by the promotion plan (version 1.0) and the Agentic Trust Framework v0.9.1 (`docs/atf-conformance.md`). Observation starts with the first live run, 2026-09-27 20:45 UTC; earliest Junior review 2026-10-11.
- **Roles:** the owner is technical owner, business owner and security owner.
- **Scope confirmed:** the OAuth token holds `gmail.readonly` only, and the code has no send, delete, modify or label calls. Message bodies are never fetched or logged; subjects are the only email content stored.
- **Use case:** sort the inbox first, draft replies at Junior, act at Senior, and reply at Principal (optional). The money/commitment carve-out holds at every level (plan §1).
- **Gate 1 for Junior:** `needs_response` caught ≥ 90% and junk calls right ≥ 90%, every week; availability > 99%; runs within 15 minutes. Calls are graded weekly with `src/review.py`.
- **Kill switch:** live drill passed at 21:42 UTC and re-authorized read-only (`incidents.md`).
- **Operations:** runs daily at 07:00 via launchd, with a notification on failure. Weekly review on Sundays.
