# ATF Conformance Crosswalk

How this project maps to the **Agentic Trust Framework (ATF)**, requirement by requirement.

**Framework references**
- Specification: *Agentic Trust Framework*, **v0.9.1 (Public Review Draft, April 2026)**, https://github.com/massivescale-ai/agentic-trust-framework, licensed CC BY 4.0. Requirements below are from `MATURITY_MODEL.md` in that repository.
- Introduction: Josh Woodruff, "The Agentic Trust Framework: Zero Trust Governance for AI Agents," Cloud Security Alliance blog, 2026-02-02, https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents

**Last reviewed:** 2026-09-27, against v0.9.1. Re-check this crosswalk when ATF publishes a new version.

**Status key**
- **Meets:** implemented as ATF specifies.
- **Stricter:** goes beyond ATF.
- **Adapted:** meets the intent at solo scale; the adaptation is stated.
- **Open:** not yet met; the item says when it's due.

## Solo-scale roles

This is a one-person deployment. **The owner holds the technical owner, business owner and security owner roles.** Where ATF asks for approval from a security team, risk committee or executive sponsor, the owner gives that approval in those roles, recorded as a dated entry in `governance/decision-log.md`.

## Maturity levels

| ATF level | ATF definition | This project | Status |
|---|---|---|---|
| Intern | Read-only; analyze and flag; can't modify external systems | `gmail.readonly` only, metadata only; triages and flags; no Gmail write calls exist in the code | Meets |
| Junior | Recommends with reasoning; explicit human approval before execution; may execute after approval | Drafts and proposals go into a queue; each needs owner approval. Gmail stays `gmail.readonly`, so the owner carries out approved actions, not the agent. | Stricter |
| Senior | Executes approved action types within guardrails; notifies. (Continuous validation isn't required by ATF until Principal.) | `gmail.modify` for a pre-approved action list only; notifies after. `gmail.modify` also permits sending and trashing, so the code allowlist and tests do the confining. Continuous validation from Senior, not only Principal (`governance/ongoing-validation.md`). | Stricter (planned) |
| Principal | Autonomous within domain; escalates edge cases; continuous validation | Reads and replies to inbox mail within limits set at sign-off; escalates edge cases (`docs/scope.md`). Continuous validation: weekly random audit (> 99%), every escalation reviewed, quarterly re-validation (`governance/ongoing-validation.md`) | Meets (planned) |
| All levels | (not in ATF) | Money, commitments, contracts and third-party obligations are never auto-sent or auto-actioned (plan §1) | Stricter |

## Deployment checklist ("Before Deploying Any Agent")

| ATF item | This project | Status |
|---|---|---|
| Agent registered in identity system | Dedicated Google OAuth client (Desktop app) is the agent's identity | Adapted |
| Unique identifier assigned | OAuth client ID (kept in the git-ignored `credentials.json`) | Adapted |
| Ownership documented | Solo-scale roles, above | Meets |
| Purpose and scope defined | `docs/scope.md` | Meets |
| Initial maturity level set (always Intern) | Intern, 2026-09-27 | Meets |
| Governance controls configured | Scope check in code, no-body logging rule, gates, decision log | Meets |
| Monitoring enabled | `decisions.db` run rows, `logs/agent.log`, failure notification, weekly availability report | Meets |
| Incident response procedures defined | `governance/incidents.md`; demotion procedure (plan §5) | Meets |
| Kill switch tested | Tested against a stand-in agent before the first live run; **first live test against the real token on 2026-09-27 21:42 UTC, after deployment** | Meets, late: the live test came after the first live run rather than before |

## Promotion gates

Thresholds that apply "every week" use the small-sample rule in plan §4 (fewer than 5 items in a week → judged on the pooled window total).

### Gate 1: Performance

| ATF metric | Intern → Junior | Junior → Senior | Senior → Principal | Status |
|---|---|---|---|---|
| Minimum time at level | 2 weeks | 4 weeks | 8 weeks | Meets. A missed weekly row doesn't count toward it (plan §4). |
| Accuracy | ATF: N/A. Here: ≥90% replies caught and ≥90% junk calls right, every week | >95% acceptance | >99% action accuracy | Intern: Stricter. Others: Meets. |
| Availability | >99% | >99.5% | >99.9% | Adapted: completed scheduled daily runs ÷ scheduled daily runs (`review.py --summary`). For a daily job these round to **100%**: one missed run fails the gate. |
| Response time SLA | Met | Met | Met | Adapted: each run completes within 15 minutes (`review.py --summary`) |

### Gate 2: Security validation

| ATF requirement | Junior | Senior | Principal | This project |
|---|---|---|---|---|
| Vulnerability assessment | ✓ | ✓ | ✓ | Dependency scan with `pip-audit` against `requirements.txt`, plus a review of the Python version's support status |
| Code review | ✓ | ✓ | ✓ | Security-focused review of `src/`, especially scope, data handling and write paths |
| Configuration audit | ✓ | ✓ | ✓ | Token scope, file permissions (`token.json`, `decisions.db` are `600`), `.gitignore` coverage, OAuth app settings, launchd job |
| Penetration testing | | ✓ | ✓ | Adapted: attempts to make the agent act outside its pre-approved action list |
| Adversarial testing | | | ✓ | Attempts to make the agent send to, reply to or forward to third parties |
| (not in ATF) | ✓ | ✓ | ✓ | Stricter: rule-evasion tests (Intern), prompt injection (Junior+), and a live kill-switch drill at every level |

Status: **Open** for the Intern → Junior promotion; due before 2026-10-11. The kill-switch drill is done (2026-09-27).

### Gate 3: Business value

| ATF requirement | Junior | Senior | Principal | This project |
|---|---|---|---|---|
| Defined success metrics | ✓ | ✓ | ✓ | Triage accuracy (Gate 1), plus time saved per week, with the measure chosen by the owner in the Gate 3 entry |
| Baseline established | ✓ | ✓ | ✓ | Owner's estimate of weekly inbox-triage time before the agent, recorded in `decision-log.md` |
| Improvement demonstrated | | ✓ | ✓ | Change against the baseline |
| ROI calculation | | ✓ | ✓ | Time saved vs. time spent on reviews and maintenance |
| Stakeholder sign-off | ✓ | ✓ | ✓ | Owner (solo-scale roles) |

Status: **Open**; baseline due before 2026-10-11.

### Gate 4: Incident record

| ATF requirement | Junior | Senior | Principal | This project |
|---|---|---|---|---|
| Zero critical incidents | ✓ | ✓ | ✓ | Required for every promotion; see the critical definition in `incidents.md` |
| Minor incidents resolved | ✓ | ✓ | ✓ | Every minor incident logged with what changed |
| Root cause analysis | If applicable | ✓ | ✓ | Field in the `incidents.md` entry format |
| Remediation verified | If applicable | ✓ | ✓ | Field in the `incidents.md` entry format |

Status: Meets. No incidents as of 2026-09-27.

### Gate 5: Governance sign-off

| ATF requirement | Junior | Senior | Principal | This project |
|---|---|---|---|---|
| Technical owner approval | ✓ | ✓ | ✓ | Owner |
| Business owner approval | ✓ | ✓ | ✓ | Owner |
| Security team approval | | ✓ | ✓ | Owner, as security owner |
| Risk committee approval | | | ✓ | Adapted: owner, recorded as a risk acceptance in the sign-off entry |
| Executive sponsor sign-off | | | ✓ | Adapted: owner |
| Documentation updated | ✓ | ✓ | ✓ | Gate checklist, `maturity-status.md`, `docs/scope.md`, `docs/architecture.md`, `docs/atf-conformance.md`, `CHANGELOG.md` in the same commit |
| (not in ATF) | | ✓ | ✓ | Stricter: the Gmail permission changes only by the documented procedure (`docs/architecture.md`, Gmail permission ladder), with the token verified |

## Pre-promotion checklists

| ATF item | Where it's covered |
|---|---|
| **Before Junior:** all outputs reviewed, accuracy confirmed | Weekly grading with `src/review.py` (Gate 1) |
| Approval workflow configured; approver roles assigned | Built as part of the Junior promotion; approver is the owner |
| Security scan passed | Gate 2 vulnerability assessment |
| Business owner sign-off | Gate 5 |
| **Before Senior:** behavioral baseline; anomaly detection | Open: to be designed before Senior |
| Notification channels configured | macOS notification exists for failures; action notifications due at Senior |
| Transaction limits set | The Senior sign-off lists the exact pre-approved actions (junior-to-senior Gate 5) |
| **Before Principal:** full audit | Covered by the Gate 2 audit items at Principal |

## Demotion

| ATF trigger | ATF result | This project | Status |
|---|---|---|---|
| Critical incident at current level | Immediate demotion to Intern | Same; at Intern, the observation period restarts | Meets |
| Security vulnerability discovered | Demotion pending remediation | Same: drop one level until fixed and verified | Meets |
| Repeated minor incidents (3+ in evaluation period) | One-level demotion | Same; the evaluation period is the current level's observation window | Meets |
| Review-based: metrics below threshold, value not shown, scope change, **model/system change** | Review may demote | Considered at every weekly review. Triage-rule changes, style-guide updates, a new AI model, and changes to the action list, reply limits or Gmail permission all trigger that review (`governance/ongoing-validation.md`). | Meets |
| Process: document → isolate → root cause → new level → controls updated → reactivate → full re-promotion | | Plan §5 procedure | Meets |

## Known gaps for review

1. **Kill switch timing.** The ATF introduction mentions sub-second manual termination. Stopping the process is effectively immediate, but revoking the token needs a network round-trip to Google, which isn't guaranteed to be sub-second.
2. **Circuit breaker.** ATF lists one (automatic halt on repeated failures). At Intern, with no actions to halt, failures surface as notifications and in availability. An automatic halt is due before Senior.
3. **Senior's Gmail permission is broader than its role.** `gmail.modify` also allows sending and trashing; Google has no narrower permission for applying labels or archiving. The confinement is in code, and it's tested at the Senior gate.
4. **OAuth Testing mode.** Google expires sign-ins every 7 days in Testing mode, which would cause missed runs and fail availability. Keep up the Sunday re-sign-in, or move the OAuth app to production.
