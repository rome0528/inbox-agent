# Scope

What the inbox agent may and may not do, by level, following the Agentic Trust Framework (ATF) v0.9.1 levels (`docs/atf-conformance.md`). Governing documents: `governance/agentic-promotion-plan.md` and the checklists in `governance/gates/`.

## Purpose

Help manage one personal Gmail inbox, in this order:
1. **Sort:** tell which mail needs a reply, which is junk or worth unsubscribing from, and which is just FYI.
2. **Draft** replies for the owner's approval (Junior).
3. **Act and send** within narrow, approved limits (Senior, and optionally Principal).

## Agentic maturation

This project is about **agentic maturation**: the system doesn't start as an agent. It starts as supervised automation and *becomes* agentic as it earns autonomy, meaning permission to choose and take actions without asking first. Accuracy doesn't make it agentic by itself; accuracy is the evidence that earns each step of autonomy at a gate.

| Level | Who decides | Who acts | Agentic? |
|---|---|---|---|
| Intern | Fixed rules label mail | Nobody; nothing changes in Gmail | **No.** Automation that observes and labels |
| Junior | The agent proposes (likely with an AI model drafting) | The owner approves every item | **Not yet.** Assistive: judgment without autonomy |
| Senior | The agent, within a pre-approved action set | The agent, and it notifies the owner after | **Yes, bounded.** Acts on its own within narrow limits |
| Principal | The agent, within its domain | The agent, including sending replies | **Yes.** Fully agentic in domain, still within the permanent limits |

Each step up widens what the agent may do on its own. Each is granted only when the gates in `governance/gates/` show it has earned it.

## Scope by level: summary

| | Intern (now) | Junior | Senior | Principal (optional) |
|---|---|---|---|---|
| Gmail permission | `gmail.readonly` | `gmail.readonly` | `gmail.modify` | `gmail.modify` + `gmail.send` |
| Reads | Inbox metadata only | Inbox metadata; bodies of `needs_response` mail; the owner's sent replies from the last 90 days (to learn their style) | Same as Junior | Inbox metadata and bodies; sent replies as at Junior |
| Triage and flag | ✓ | ✓ | ✓ | ✓ |
| Draft replies | | Into a local queue, for the owner's approval | ✓ | ✓ |
| Unsubscribe/junk | | Proposes; the owner approves and does it | Does it on its own, if on the approved list | ✓ |
| Label / archive on its own | | | Pre-approved list, notifies after | ✓ |
| Send replies | | | | On its own, within sign-off limits; escalates edge cases |
| Owner's role | Grade calls weekly | Approve every item | Weekly random audit and quarterly re-validation | Weekly random audit, quarterly re-validation, handle escalations |
| Minimum time at level | 2 weeks | 4 weeks | 8 weeks | |

**The Gmail permission is updated as the agent matures**, only at a signed-off promotion (and reduced on demotion), using the procedure in `docs/architecture.md` (Gmail permission ladder). Moving right requires passing all five gates in `governance/gates/`. **Nothing in a later column exists in the code until that promotion is signed off** in `governance/decision-log.md`. The sections below define each level; items marked *decide at sign-off* must be settled in that promotion's Gate 5 entry.

## Intern: observe and flag (current)

- **Gmail permission:** `gmail.readonly`.
- **Reads:** one Gmail account, **inbox only** (the `INBOX` label, which covers all inbox tabs), and **metadata only**: sender, recipients, subject, date, bulk-mail headers and Gmail labels. Not Sent, Spam, Trash, archived mail, other labels, bodies or attachments.
- **May do on its own:** triage each message as `needs_response`, `junk` or `fyi`; tag SENSITIVE subjects; log decisions locally.
- **Needs the owner's approval:** nothing; it takes no actions.
- **Must not do, with no capability in the code:** send, reply, draft, forward, delete, trash, archive, label, mark read/unread or unsubscribe; read bodies or attachments; use any other Gmail permission; send email data to any third party, including AI services; touch other Google services (Calendar, Drive, Contacts).
- **Data flows:** Google → this Mac only.

## Junior: recommend, the owner approves

- **Gmail permission:** `gmail.readonly`, unchanged. The agent still can't change anything in Gmail. The owner carries out every approved action. It also can't create Gmail drafts, because that needs a compose permission, so drafts live in a local queue.
- **Reads:** metadata for all inbox mail, plus the **body of `needs_response` messages** in order to draft replies. Bodies are held in memory only, never logged (plan §8).
- **Reads the owner's sent mail, to learn their style** (plan §8):
  - **What:** the owner's sent replies from the **last 90 days**, excluding any about SENSITIVE topics. This is the only mail outside the inbox the agent reads, and it's within `gmail.readonly`.
  - **What's kept:** a **style guide** (tone, length, greetings, sign-offs, common phrasings in general terms) that the owner reviews and approves before it's used. It contains **no quoted text** from real emails, and no copies of sent mail are stored.
  - **How it changes:** the guide is versioned. Refreshing it is a system change that triggers a review (`governance/ongoing-validation.md`, Changes that force a review); it's never updated silently.
  - **Measuring drafts:** each draft is compared with the reply the owner actually sent, as a measure of draft quality alongside approve/reject.
- **May do on its own:** everything Intern does; draft replies and propose unsubscribe/junk actions into the queue, each with its reasoning.
- **Needs the owner's approval:** every item. Each approve/reject is recorded in the `accepted` column of `decisions.db`.
- **Must not do:** execute any action in Gmail; send anything; use any permission beyond `gmail.readonly`; draft replies to SENSITIVE mail beyond a flag for the owner's attention *(decide at sign-off: flag only, or draft for the owner's review)*.
- **Data flows:** Google → this Mac. If drafting uses an AI model, message bodies go to that provider (e.g. the Claude API → Anthropic), and so does sent mail if the model builds the style guide. That's a **new data flow**, decided and documented in `docs/architecture.md` before it's built.
- **Decide at sign-off (Intern → Junior):**
  - Whether the style guide is built from sent mail at all, and whether an AI provider may see the owner's sent mail to build it.
  - Whether drafting uses an AI model, and which provider.
  - Where the queue lives and how long drafts are kept. Drafts may quote the original email, so they're treated like bodies: local, git-ignored, owner-only, deleted once decided.
  - How approval works in practice.

## Senior: act within guardrails, notify after

- **Gmail permission:** `gmail.modify`. **Caution:** Google's `gmail.modify` permission is broader than Senior's job. It also allows sending, trashing and changing any message. What confines Senior to its approved actions is the code allowlist, the tests and the audit, not Google.
  - The code may call only the approved actions; any other write call is a critical incident.
  - Gate 2 penetration testing at this level must specifically check that nothing outside the list can be triggered.
- **Reads:** same as Junior.
- **May do on its own:** only the actions on the **pre-approved list** set at the Junior → Senior sign-off (ATF "transaction limits"), for example applying labels, archiving, or moving clear junk out of the inbox. It notifies the owner after each action or in a daily digest.
- **Needs the owner's approval:** anything not on the list, including all replies (drafted as at Junior), and anything SENSITIVE.
- **Ongoing validation:** weekly random audit of its autonomous actions (> 95% correct) and quarterly re-validation, per `governance/ongoing-validation.md`.
- **Must not do:** send or forward email; permanently delete; act on SENSITIVE mail; change its own permissions or allowlist; act outside the inbox.
- **Unsubscribing** needs care. It works either by emailing the sender (which is sending, so not allowed at Senior) or by a one-click web request to the sender's site (a new outbound data flow). Either needs explicit sign-off before it's on the list.
- **Required before Senior** (ATF): action notifications, a behavioral baseline, anomaly detection and a circuit breaker (automatic halt after repeated failures).
- **Decide at sign-off (Junior → Senior):** the exact action list; how the owner is notified; the circuit-breaker threshold; whether unsubscribing is included, and by which method.

## Principal: read and respond within its domain (optional)

- **Gmail permission:** `gmail.modify` + `gmail.send`: the full read-and-respond set.
- **Reads:** metadata and bodies of inbox mail.
- **May do on its own:** everything Senior does, **plus reply to email** within the sign-off limits, notifying the owner after. It **escalates** edge cases to the owner instead of deciding them (ATF): anything ambiguous, new or outside the limits.
- **Needs the owner's approval:** anything escalated; anything outside the sign-off limits; all SENSITIVE mail, which is never auto-sent (plan §1).
- **Ongoing validation:** weekly random audit of its actions and sent replies (> 99% correct), every escalation reviewed, and quarterly re-validation, per `governance/ongoing-validation.md`. ATF requires continuous validation at Principal.
- **Must not do:** send to anyone not already in the thread, start new threads, forward, send attachments, reply to SENSITIVE mail, change its own permissions or limits, or act outside the inbox *(each is a default the sign-off may narrow further, never widen past the permanent limits)*.
- **Decide at sign-off (Senior → Principal):**
  - Exactly which mail it may answer (e.g. by sender, thread type or triage category).
  - Who it may reply to.
  - A daily send cap.
  - Whether replies wait a hold period before sending, giving the owner a window to cancel.
  - What counts as an edge case to escalate.

## Permanent limits (every level)

- **Money, commitments, contracts and third-party obligations** are never auto-sent or auto-actioned (plan §1). The agent tags subjects mentioning invoices, payments, contracts, signatures and similar as SENSITIVE, and never suggests them as junk.
- **No email body content** is ever written to `decisions.db`, a log file or any committed file (plan §8).
- **The kill switch** (`src/kill_switch.py`) must always be able to halt the agent and revoke its access.
- **Demotion** (plan §5, following ATF): a critical incident means immediate demotion to Intern; 3 or more minor incidents or a security vulnerability means down one level. Demotion removes that level's permissions. At Intern, the observation period restarts.

## Data handling

- Stored locally now: subject lines, triage decisions and reasons, hashed message IDs, and the owner's grades. See `docs/architecture.md` → Data storage.
- From Junior: message bodies and sent replies are read into memory and never stored in `decisions.db` or logs. The only thing derived from sent mail that's kept is the approved, versioned style guide, with no quoted text. Drafts are kept in a local, git-ignored, owner-only queue and deleted once decided. Any AI provider used for drafting receives the bodies it drafts from.
- Nothing is committed to git except code and governance docs.
