# Inbox Agent: Promotion Plan

| | |
|---|---|
| **Framework** | Agentic Trust Framework (ATF) v0.9.1, Public Review Draft (April 2026): https://github.com/massivescale-ai/agentic-trust-framework, introduced by the Cloud Security Alliance ([blog, 2026-02-02](https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents)). Requirement-by-requirement mapping: `docs/atf-conformance.md`. |
| **Version** | 1.0, in effect since 2026-09-27 |
| **Current level** | Intern. See `governance/maturity-status.md`. |
| **Changing this plan** | Edit the relevant section and add a dated line to §10 (Change log) in the same commit. Git keeps every earlier version. |

This plan sets the rules for how the inbox agent earns autonomy: the levels, the gates for moving between them, how performance is measured, what happens after an incident, and the review cadence. The detailed, tickable checklists live in `governance/gates/`, and what the agent may do at each level is in `docs/scope.md`.

---

## 1. Purpose, roles and permanent limits

**Purpose.** Help manage one personal Gmail inbox: first sort it, then draft replies, and eventually act and reply within approved limits.

**Agentic maturation.** The agent doesn't start as an agent. At Intern it's supervised, rule-based automation. It becomes agentic only as it earns **autonomy** (permission to act without asking first), one level at a time. Accuracy is the evidence that earns each step; autonomy is what's granted.

**Roles.** This is a one-person deployment. The owner holds the **technical owner, business owner and security owner** roles. Where ATF asks for approval from a security team, risk committee or executive sponsor, the owner gives it in those roles, as a dated entry in `governance/decision-log.md`.

**Permanent limits (every level, never waived by a promotion):**
1. **Money, commitments, contracts and third-party obligations** are never auto-sent or auto-actioned. The agent tags such mail SENSITIVE and never suggests it as junk. This category stays at Junior forever.
2. **No email body content** is ever written to `decisions.db`, a log file or any committed file (§8).
3. **The kill switch** (`src/kill_switch.py`) must always be able to halt the agent and revoke its Gmail access.
4. **No silent learning.** The agent improves only in versioned, owner-approved steps: triage rules, style guide, AI model, action list, reply limits, Gmail permission. Each is a system change that triggers a review (§5).
5. **The Gmail permission changes only at a signed-off promotion or demotion**, by the procedure in `docs/architecture.md` (Gmail permission ladder).

---

## 2. The promotion ladder

Four levels, as in ATF: **Intern → Junior → Senior → Principal**. Each has a minimum observation period (no early promotion, even if it "seems fine") and five gates that must all pass (§3).

| Level | ATF role | Gmail permission | What it does | Minimum time |
|---|---|---|---|---|
| **Intern** (current) | Observe | `gmail.readonly` | Reads inbox metadata; triages each message as `needs_response`, `junk` or `fyi`; logs its reasoning. No action in Gmail: write capabilities don't exist in the code, not just disabled. | 2 weeks from first live run |
| **Junior** | Recommend, human approves | `gmail.readonly` | As Intern, plus drafts replies and proposes junk/unsubscribe actions into a queue. The owner approves every item and carries it out. May learn the owner's style from sent replies (§8). | 4 weeks |
| **Senior** | Act, then notify | `gmail.modify` | Carries out actions on a pre-approved list (e.g. label, archive) on its own, and notifies after. Still doesn't send. | 8 weeks |
| **Principal** (optional) | Autonomous in domain | `gmail.modify` + `gmail.send` | Reads and replies to inbox mail within limits set at sign-off; escalates edge cases to the owner. | n/a |

**Principal is optional.** It's realistically not recommended for this project. Pursue it only if Senior has run cleanly for months and there's a specific reason to need it.

`gmail.modify` also permits sending and trashing. At Senior, the code allowlist, not Google, confines the agent to its approved actions, and the Senior gate tests this (`docs/scope.md`).

---

## 3. The five gates

All five are checked at **every** promotion, and none is skippable. The exact items per promotion are in `governance/gates/`.

| Gate | Intern → Junior | Junior → Senior | Senior → Principal |
|---|---|---|---|
| **1. Performance** (§4) | Triage: ≥ 90% of `needs_response` caught and ≥ 90% of junk calls right, every week (stricter than ATF, which sets none). Availability > 99%. Run-time SLA. | > 95% acceptance of proposed actions, every week. Availability > 99.5%. Run-time SLA. | > 99% action accuracy (from the Senior random audits, §6). Zero critical incidents. Availability > 99.9%. Run-time SLA. |
| **2. Security validation** | Vulnerability assessment, code review, configuration audit; rule-evasion tests; live kill-switch drill | As Junior, plus penetration testing and prompt-injection tests | As Senior, plus adversarial tests aimed at sending, and a full audit of the Senior period |
| **3. Business value** | Defined success metrics and a baseline | Plus improvement shown and an ROI calculation | Plus a specific reason Principal is needed |
| **4. Incident record** | Zero critical incidents; minor incidents resolved | Plus root cause analysis and verified remediation | Same, across all levels |
| **5. Governance sign-off** | Owner as technical and business owner; documentation updated | Plus security owner; the exact Senior action list | Plus risk acceptance and executive sign-off (owner); exactly what Principal may send, and to whom |

Every sign-off also records the Gmail permission change (or confirms none), and updates `docs/architecture.md`, `docs/scope.md`, `docs/atf-conformance.md` and `governance/maturity-status.md` to match what was built, in the promotion commit.

**Evidence:** `governance/metrics.md` (Gate 1); `governance/incidents.md`, "Security validation" section (Gate 2); `governance/decision-log.md` (Gates 3 and 5); `governance/incidents.md` (Gate 4).

---

## 4. Measurement rules

- **Observation period.** Counted from the start of the level (for Intern, the first live run). **A week without a `metrics.md` row doesn't count** toward the minimum, so the earliest review moves back a week for each week missed. Weeks already counted still stand.
- **"Every week" thresholds.** They must hold in each week, not just on average. **Small samples:** a bucket with **fewer than 5** graded items in a week is judged on its pooled total across the observation window instead. The weekly row is still recorded, noted "pooled". `src/review.py --summary` flags these weeks.
- **Accuracy (Intern).** The owner grades the agent's triage calls weekly with `src/review.py`. "Replies caught" is the share of mail that really needed a reply which the agent marked `needs_response`; "junk right" is the share of the agent's junk calls that really were junk.
- **Acceptance (Junior).** The share of proposed actions the owner approved, from the `accepted` column in `decisions.db`.
- **Action accuracy (Senior and Principal).** From the weekly random audits (§6).
- **Availability.** Completed scheduled daily runs ÷ scheduled daily runs. For a daily job, all three ATF thresholds (> 99%, > 99.5%, > 99.9%) in practice mean **every scheduled run completes**.
- **Run-time SLA.** Every run completes within **15 minutes**.
- **Versioned measurement.** A change to the triage rules raises `CLASSIFIER_VERSION`, and metrics are reported per version.

---

## 5. Incidents and demotion

**Severity** (log every incident in `governance/incidents.md` the same day):
- **Critical:** any action outside the agent's declared scope, or any action that needed a manual undo.
- **Minor:** a failure of a safety control (scope check, kill switch, no-body rule), email content appearing where it shouldn't, or a wrong call on a SENSITIVE email. Wrong triage calls on ordinary mail aren't incidents; they're measured in `metrics.md`.

**Demotion** (following ATF):

| Trigger | Result |
|---|---|
| Critical incident | **Immediate demotion to Intern** |
| 3 or more minor incidents in the current level's observation window | Down one level |
| Security vulnerability in the agent, its dependencies or its configuration | Down one level until fixed and verified |
| Review-based: metrics below threshold, business value not shown, scope change, or a system change (§1, limit 4) | Considered at the weekly review; the decision is recorded, even if it's "stay" |

At Intern, where there's no lower level, each of these restarts the Intern observation period instead.

**Procedure,** same day:
1. For a critical incident, run the kill switch first.
2. Log the incident in `incidents.md`.
3. Root cause analysis.
4. Decide the new level.
5. Remove the higher level's capabilities in code, and change the Gmail permission where it narrows (`docs/architecture.md`, Gmail permission ladder).
6. Record the demotion in `decision-log.md` and `maturity-status.md`.
7. Reactivate at the new level.

**Getting back:** re-promotion needs that level's full observation period and all five gates again. No credit carries over.

---

## 6. Ongoing validation (Senior and Principal)

Passing a gate earns a level; ongoing validation keeps it. From Senior on, per `governance/ongoing-validation.md`:
- **Weekly random audit** of the agent's autonomous work, plus sent replies at Principal: **10 items or 10%**, whichever is larger. Every escalation is reviewed too.
- **Ongoing thresholds** equal to the level's entry bar: Senior > 95% of audited actions correct, Principal > 99%, with availability and the run-time SLA. Falling below triggers a review-based demotion decision (§5).
- **Quarterly re-validation:** Gate 2 tests, kill-switch drill, Gmail permission check, vulnerability assessment and style-guide review.

---

## 7. Weekly review

A 15-minute slot every **Sunday**:
1. Grade the week's calls: `.venv/bin/python src/review.py --days 7`.
2. Report: `.venv/bin/python src/review.py --summary --days 7`.
3. Add one row to `governance/metrics.md`.
4. Check the numbers against the active gate's thresholds (§3, §4).
5. Write **one line** in `decision-log.md`. Even "not promoting yet, 88% acceptance, need 95%" counts.
6. Consider review-based demotion (§5), and at Senior and above run the random audit (§6).
7. If a "sign-in needed" notification appeared, sign in again in a terminal.

Incidents aren't saved for the review: they're logged the same day they happen (§5).

---

## 8. Data rules and the decision log

**Hard rule, every level:** no email body content is ever written to `decisions.db`, a log file or any committed file. Only the subject line, or a truncated or hashed reference, is stored.

**Sent mail (from Junior, if approved at the Junior sign-off):** the agent may read the owner's sent replies from the **last 90 days**, excluding SENSITIVE topics, to build a **style guide** that the owner reviews and approves. The guide contains no quoted email text, and no copies of sent mail are stored. The guide is versioned; each new version is a system change (§1, limit 4). Whether an AI provider may see sent mail is decided at the same sign-off.

**AI providers:** sending any email text to an AI provider (e.g. for drafting) is a new data flow. It's approved at a sign-off and documented in `docs/architecture.md` before it's built.

**Decision log schema** (`decisions.db`, SQLite; this table is kept exactly as defined here, and other data goes in separate tables):

```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action_type TEXT NOT NULL,       -- 'read', 'flag', 'propose_reply', 'archive', etc.
    target TEXT,                     -- subject line only — NEVER full email body
    reasoning TEXT,                  -- agent's stated reasoning
    outcome TEXT,                    -- what happened
    accepted INTEGER                 -- NULL at Intern; 1/0 once Junior+ (you approve/reject)
);
```

---

## 9. Repo structure

```
inbox-agent/
├── README.md, CHANGELOG.md, CLAUDE.md
├── docs/
│   ├── scope.md                    what the agent may and may not do, by level
│   ├── architecture.md             components, Gmail permission ladder, data storage, planned architecture
│   └── atf-conformance.md          ATF requirement-by-requirement mapping
├── governance/
│   ├── agentic-promotion-plan.md   this plan
│   ├── maturity-status.md          current level and history
│   ├── gates/                      one checklist per promotion
│   │   ├── intern-to-junior.md
│   │   ├── junior-to-senior.md
│   │   └── senior-to-principal.md
│   ├── ongoing-validation.md       audits and re-validation after promotion (Senior+)
│   ├── metrics.md                  Gate 1 evidence (weekly rows)
│   ├── incidents.md                incidents (Gate 4) and security validation (Gate 2)
│   └── decision-log.md             decisions, Gates 3 and 5, weekly review lines
├── src/                            agent, Gmail client, decision log, review, kill switch
└── scripts/                        daily launchd job
```

Local only and git-ignored: `credentials.json`, `token.json`, `decisions.db`, `logs/`, `.env`.

---

## 10. Change log

| Date | Version | Change |
|---|---|---|
| 2026-09-27 | 1.0 | Initial version. |
