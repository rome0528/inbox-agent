# Inbox Agent

An AI inbox assistant that **earns its autonomy**. It starts read-only and gets more permissions only when evidence shows it has earned them, following the [Agentic Trust Framework (ATF)](https://github.com/massivescale-ai/agentic-trust-framework) from the [Cloud Security Alliance](https://cloudsecurityalliance.org/blog/2026/02/02/the-agentic-trust-framework-zero-trust-governance-for-ai-agents).

The idea is **agentic maturation**. The system isn't an agent on day one; it's supervised automation. It becomes agentic only as it earns autonomy (permission to act without asking first), one level at a time. Accuracy is the evidence, and autonomy is what gets granted.

**Status:** running at **Intern** since 2026-09-27. Once a day it reads inbox metadata, sorts each message into `needs_response`, `junk` or `fyi`, and logs its reasoning locally. It can't change anything in Gmail.

## The promotion ladder

| Level | What it may do | Gmail permission | Minimum time |
|---|---|---|---|
| **Intern** (now) | Observe and flag: triage every message, change nothing | `gmail.readonly` | 2 weeks |
| **Junior** | Recommend: draft replies and propose actions; a human approves every item | `gmail.readonly` | 4 weeks |
| **Senior** | Act within guardrails: a pre-approved list of actions (label, archive), with a notification after each | `gmail.modify` | 8 weeks |
| **Principal** (optional) | Reply on its own within set limits, and escalate edge cases | `gmail.modify` + `gmail.send` | n/a |

Each promotion requires **five gates**: performance, security validation, business value, incident record and governance sign-off. Each gate has written evidence and none can be skipped.

## Key controls

- **Least privilege by design.** Capabilities for a higher level don't exist in the code until that promotion is signed off. They aren't just switched off.
- **The Gmail permission is the control.** It grows only at a signed-off promotion and shrinks on demotion. The code refuses any token that doesn't exactly match the current level.
- **No email content stored.** Bodies are never fetched at Intern, and no body text is ever written to logs or the database; only subject lines are kept.
- **Permanent limit:** money, contracts and commitments are never handled automatically, at any level.
- **Kill switch:** one command halts the agent, blocks restarts and revokes Google access. It's drilled live at every level.
- **Demotion is automatic:** a critical incident sends the agent straight back to Intern.
- **No silent learning:** every behavior change (rules, model, limits) is versioned, approved and triggers a review.
- **Measured, not assumed:** calls are graded by hand weekly, with per-bucket accuracy thresholds, availability and a run-time limit.

## How it runs

A small Python program on a Mac, scheduled daily. It reads Gmail through Google's API with OAuth, triages with fixed rules, and logs every decision to a local SQLite database. There's no AI model at Intern and nothing leaves the machine except calls to Google. A weekly review grades the agent's calls and feeds the gate metrics.

## What's in the repo

| Path | What it is |
|---|---|
| [`governance/agentic-promotion-plan.md`](governance/agentic-promotion-plan.md) | The framework: levels, gates, measurement, incidents and demotion, review cadence |
| [`governance/gates/`](governance/gates/) | A checklist for each promotion |
| [`governance/ongoing-validation.md`](governance/ongoing-validation.md) | Random audits and re-validation after promotion |
| [`governance/`](governance/) | Evidence: maturity status, metrics, incidents, decision log |
| [`docs/scope.md`](docs/scope.md) | What the agent may and may not do at each level |
| [`docs/architecture.md`](docs/architecture.md) | Components, the Gmail permission ladder, data storage, planned architecture |
| [`docs/atf-conformance.md`](docs/atf-conformance.md) | Every ATF requirement mapped to this project, including known gaps |
| [`CLAUDE.md`](CLAUDE.md) | Guardrails for the AI coding assistant working on this repo |
| [`src/`](src/) | The agent, Gmail client, decision log, weekly review and kill switch |

Built with [Claude Code](https://claude.com/claude-code).

## License

[Apache License 2.0](LICENSE).
