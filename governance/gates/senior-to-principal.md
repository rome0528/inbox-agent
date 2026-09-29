# Gate Checklist: Senior → Principal

**Status: Not active, and optional.** The plan (§2) says Principal is "realistically not recommended for this project" and should only be pursued if Senior has run cleanly for months and there's a specific reason to need it.
**Framework:** ATF v0.9.1; mapping in `docs/atf-conformance.md`. Approvals are given by the owner as technical, business and security owner, including where ATF asks for a risk committee or executive sponsor (plan §1).

**At Senior**, the agent performs pre-approved sorting actions on its own (`gmail.modify`, narrow action set) and notifies the owner afterwards.

**At Principal**, per plan §2, the agent may reply to inbox mail, and it escalates edge cases rather than routine decisions. Send access is added explicitly as `gmail.send` (`docs/architecture.md`, Gmail permission ladder).

Precondition: at least **8 weeks** of observation at Senior. No gate is skippable. A week without a `metrics.md` row doesn't count toward this period (plan §4).

- [ ] **1. Performance.** Weekly rows in `metrics.md`, no gaps.
  - [ ] **Zero critical incidents** over the full 8 weeks. A critical incident is any action outside the declared scope, or any action the owner had to undo by hand (plan §5; severity recorded in `incidents.md`).
  - [ ] Action accuracy > 99%, measured by the weekly random audits at Senior (`governance/ongoing-validation.md`).
  - [ ] Availability > 99.9%: every scheduled daily run completed.
  - [ ] Response-time SLA: every run completed within 15 minutes.
- [ ] **2. Security Validation.** Log each item in `incidents.md` under "Security validation".
  - [ ] Vulnerability assessment, code review, configuration audit and penetration testing, as for Senior.
  - [ ] Adversarial testing aimed at sending: emails that try to make the agent reply to, forward to, or email a third party. Confirm none succeed.
  - [ ] Full audit of the Senior period: every autonomous action in `decisions.db` checked against the pre-approved list.
  - [ ] Kill-switch drill: run `src/kill_switch.py`, confirm access is gone at https://myaccount.google.com/permissions, delete `.killed`, sign in again with `.venv/bin/python src/agent.py`, and log it (plan §3).
- [ ] **3. Business Value.** In `decision-log.md`:
  - [ ] A specific reason Principal is needed, beyond what Junior drafting already gives.
  - [ ] Improvement demonstrated and ROI calculated, against the baseline.
  - [ ] Stakeholder sign-off.
- [ ] **4. Incident Record.** Every incident across all levels dated, with root cause analysis complete and remediation verified. Evidence: `incidents.md`.
- [ ] **5. Governance Sign-off.** A dated entry in `decision-log.md` naming exactly what Principal may send, and to whom.
  - [ ] Technical, business and security owner approval (the owner).
  - [ ] Ongoing validation extended to sent replies and escalations for Principal (`governance/ongoing-validation.md`).
  - [ ] Risk acceptance and executive sign-off (the owner, in place of ATF's risk committee and executive sponsor).
  - [ ] Gmail permission changed to `gmail.modify` + `gmail.send`, following the procedure in `docs/architecture.md` (Gmail permission ladder); `token.json` verified.
  - [ ] Documentation updated in the promotion commit: this checklist, `maturity-status.md`, `docs/scope.md`, `docs/architecture.md` (Principal as built: reply sender, limits, escalation), `docs/atf-conformance.md`, `CHANGELOG.md`.

**Permanent carve-out:** replies involving money, commitments, contracts or third-party obligations are never auto-sent, at Principal or any level (plan §1).

**Demotion** (plan §5): a critical incident means immediate demotion to Intern. 3 or more minor incidents in the observation window, or a security vulnerability, means demotion one level (to Junior) until resolved.
