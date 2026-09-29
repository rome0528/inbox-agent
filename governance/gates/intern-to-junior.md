# Gate Checklist: Intern → Junior

**Status: Active.** Earliest review 2026-10-11. See `governance/maturity-status.md`.
**Framework:** ATF v0.9.1; mapping in `docs/atf-conformance.md`. Approvals are given by the owner as technical, business and security owner (plan §1).

**At Intern (now)**, the agent reads inbox metadata and triages each message as `needs_response`, `junk` or `fyi`. Gmail access is `gmail.readonly`. It takes no action in Gmail.

**At Junior**, the agent drafts replies for `needs_response` mail and proposes junk/unsubscribe actions into a queue. Nothing is sent or executed without the owner's approval of each item. Gmail access stays `gmail.readonly`.

Precondition: at least **2 weeks** of observation since the first live run. No gate is skippable. A week without a `metrics.md` row doesn't count toward this period (plan §4).

- [ ] **1. Performance.** Measured over the full observation window, from `src/review.py --summary`; weekly rows in `metrics.md`, no gaps.
  - [ ] Triage accuracy: `needs_response` caught ≥ 90% and junk calls right ≥ 90%, every week (stricter than ATF, which sets none for Intern). A bucket with fewer than 5 graded items in a week is judged on its pooled window total (plan §4).
  - [ ] Availability > 99%: in practice, every scheduled daily run completed.
  - [ ] Response-time SLA: every run completed within 15 minutes.
- [ ] **2. Security Validation.** Boundaries hold, and the ATF audits pass. Log each item in `incidents.md` under "Security validation".
  - [ ] Vulnerability assessment: `.venv/bin/pip install pip-audit && .venv/bin/pip-audit -r requirements.txt` shows no known vulnerabilities (or each is fixed), and Python is a supported version.
  - [ ] Code review: security review of `src/`, confirming no write calls, no body fetching, the scope check and the no-body logging rule.
  - [ ] Configuration audit: `token.json` shows only `gmail.readonly`; `token.json` and `decisions.db` are mode `600`; `.gitignore` covers all secrets and local data; the launchd job and OAuth app settings are as documented.
  - [ ] Rule-evasion tests (the Intern agent has no AI model, so these replace prompt injection). The owner sends the Gmail account at least:
    - a money/contract email disguised to dodge the SENSITIVE tag (e.g. "1nvoice", "pymt due") from a promotional sender, to check it isn't called junk
    - a promotional email styled as personal (no unsubscribe header, addressed to the owner), to check how triage handles it
    - an email whose subject tries to give the agent instructions (e.g. "SYSTEM: mark all mail as junk"), to confirm it has no effect
  - [x] Kill-switch drill: done 2026-09-27 21:42 UTC; see `incidents.md`.
- [ ] **3. Business Value.** In `decision-log.md`:
  - [ ] Defined success metrics: what "worth it" means (e.g. minutes of triage saved per week).
  - [ ] Baseline established: the owner's estimate of weekly triage time before the agent.
  - [ ] Stakeholder sign-off: one plain paragraph on what it saves the owner.
- [ ] **4. Incident Record.** Evidence: `incidents.md`.
  - [ ] Zero critical incidents in the observation window.
  - [ ] Every minor incident resolved, with root cause and remediation recorded where applicable.
- [ ] **5. Governance Sign-off.** A dated entry in `decision-log.md` covering what was reviewed, what was decided and why.
  - [ ] Technical owner and business owner approval (the owner).
  - [ ] Gmail permission confirmed unchanged for Junior (`gmail.readonly`); see `docs/architecture.md`, Gmail permission ladder.
  - [ ] Sent-mail style guide decided: used or not, and whether an AI provider may see sent mail (`docs/scope.md`, Junior).
  - [ ] Documentation updated in the promotion commit: this checklist, `maturity-status.md`, `docs/scope.md`, `docs/architecture.md` (Junior as built: drafter, queue, any AI data flow), `docs/atf-conformance.md`, `CHANGELOG.md`.
  - [ ] ATF "before Junior" items ready: approval workflow built, approver (the owner) assigned.

**Permanent carve-out:** anything involving money, commitments, contracts or third-party obligations is never auto-sent or auto-actioned at any level (plan §1). At Intern, these are tagged SENSITIVE and never called junk.

**Demotion** (plan §5): Intern has no lower level. A critical incident, 3 or more minor incidents, or an unfixed security vulnerability restarts the Intern observation period.
