# Ongoing Validation

**Status: Not active.** Applies from the promotion to **Senior**, and stays in force at **Principal** (plan §6).

Passing a gate earns a level; ongoing validation is how the agent **keeps** it. ATF: *"Principal agents require continuous validation. Any significant incident triggers automatic demotion."* The same applies here to Senior, because it's the first level that acts on its own.

## Weekly random audit (part of the Sunday review)

- **Sample:** each week, `src/review.py` draws a **random** sample of the agent's autonomous work: actions at Senior, and actions plus sent replies at Principal. The sample is **10 items or 10% of the week's total, whichever is larger** (everything, if there are fewer than 10). It's random so the agent can't be tuned to pass a predictable check.
- **Always reviewed, on top of the sample:**
  - every escalation
  - every reply to a type of thread it hasn't answered before
  - every action or reply involving a message near the SENSITIVE line (tagged, or edited to remove the tag)
  - anything the anomaly detection flagged
- **Grade each item:** correct, wrong but harmless, or wrong and needed undoing. An item that needed undoing is a **critical incident** (plan §5): log it in `incidents.md` the same day, and demote to Intern (plan §5).
- **Record:** the audit accuracy goes in the week's `metrics.md` row (Audit accuracy column).

## Ongoing thresholds

A level's entry bar has to keep holding after promotion.

| Level | Audit accuracy | Availability | Run-time SLA |
|---|---|---|---|
| Senior | > 95% of audited actions correct | > 99.5% | Every run within 15 minutes |
| Principal | > 99% of audited actions and replies correct | > 99.9% | Every run within 15 minutes |

The plan §4 small-sample rule applies: a week with fewer than 5 audited items is judged on the pooled total since promotion. Falling below any threshold triggers a **review-based demotion** decision (ATF), recorded in `decision-log.md` with the outcome, even if the outcome is "stay".

## Quarterly re-validation

Every 13 weeks at Senior or Principal, record each item in `incidents.md` under "Security validation":
- [ ] Re-run that level's Gate 2 tests: penetration tests at Senior; adversarial send tests at Principal.
- [ ] Live kill-switch drill.
- [ ] `token.json` scopes match the permission ladder for the level (`docs/architecture.md`).
- [ ] Vulnerability assessment (`pip-audit`) and Python still supported.
- [ ] Style guide (if used) reviewed: still accurate, contains no quoted email text.

## Changes that force a review

Any of these counts as an "underlying model or system change" (ATF review-based demotion). Log it in `decision-log.md` and consider the level at the next weekly review:
- new triage rules (`CLASSIFIER_VERSION`)
- a new or updated style guide
- a new AI model or provider
- a change to the approved action list or the reply limits
- a change to the Gmail permission
