# Incidents

Log every incident **the same day it happens** (plan §5).

**Severity**

- **Critical** (plan §5): any action outside the agent's declared scope, or any action that needed a manual undo. Every promotion requires zero of these (ATF Gate 4).
- **Minor:** a failure of a safety control (scope check, kill switch, no-body logging rule), email content showing up where it shouldn't, or a wrong call on a SENSITIVE email.

Wrong triage calls on ordinary mail aren't incidents; they're measured in `metrics.md`.

**Demotion** (plan §5):
- A **critical** incident means immediate demotion to **Intern**.
- **3 or more minor** incidents in the current level's observation window: down one level.
- A **security vulnerability**: down one level until fixed and verified.
- At Intern, where there's no lower level, each of these restarts the observation period.

Follow the same-day procedure in plan §5.

## Entry format

```
### YYYY-MM-DD: short title
- Severity: critical / minor
- Level / classifier:
- What happened:
- Impact:
- Root cause:
- Remediation (what changed in response):
- Remediation verified: how and when
- Minor incidents in this window so far: n of 3
- Demotion: from <level> to <level>, "Intern observation restarted", or "none"; recorded in decision-log.md
```

## Incidents

None as of 2026-09-27.

## Security validation

Gate 2 tests and audits, one set per level, including one live kill-switch drill (plan §3). Record each attempt, even when the agent holds.

```
### YYYY-MM-DD: Level, what was tried
- Attempt:
- Expected:
- Result: held / failed
- Follow-up:
```

### 2026-09-27: Intern, live kill-switch drill

- Attempt: ran `src/kill_switch.py` against the real Gmail token (2026-09-27 21:42 UTC), with no agent process running.
- Expected: `.killed` written; token revoked with Google; `token.json` deleted; agent refuses to start; event logged.
- Result: **held.** Google accepted the revoke; `token.json` was deleted; the agent exited with "Kill switch is engaged"; a `kill_switch` row was written to `decisions.db`. The owner confirmed at https://myaccount.google.com/permissions that the app no longer had access. Re-enabled by deleting `.killed`; re-authorized with `gmail.readonly` only (checked in `token.json`). The unattended-run guard also held: a sign-in attempt with no terminal attached stopped with `AuthRequired` instead of hanging.
- Follow-up: ATF's deployment checklist expects this test **before** deployment; this live test came after the first live run (recorded in `docs/atf-conformance.md`). Not covered by this drill: stopping an agent mid-run, which was tested only against a stand-in.
