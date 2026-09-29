"""Intern-level inbox agent: read, triage, log. Takes no action on the inbox.

Each inbox message gets one triage bucket (Gate 1 measures these):
  needs_response  a person wrote to you directly and likely expects a reply
  junk            promotional/bulk mail: candidate to unsubscribe or mark as junk
  fyi             everything else: notifications, receipts, cc's, updates

Triage is rule-based over metadata only (labels, sender, recipients, subject,
bulk-mail headers), so no email content leaves this machine. Each run triages
inbox messages it hasn't logged before; grade the results with src/review.py.

Usage: python src/agent.py [--max N] [--baseline]
"""

import argparse
import os
import re
import signal
import sys
from email.utils import getaddresses
from datetime import timedelta
from pathlib import Path

import decision_log
import gmail_client

ROOT = Path(__file__).resolve().parent.parent
PID_PATH = ROOT / "agent.pid"
KILLED_PATH = ROOT / ".killed"

LEVEL = "Intern"

# Bump whenever triage rules change, so review metrics can be split by version.
CLASSIFIER_VERSION = 2

# Re-list this far behind the previous run to catch late-delivered mail; already-seen messages are skipped.
OVERLAP = timedelta(days=1)

# Triage bucket -> decisions.action_type
ACTION_TYPES = {"needs_response": "flag", "junk": "flag_junk", "fyi": "read"}

GMAIL_CATEGORIES = {
    "CATEGORY_PROMOTIONS": "promotions",
    "CATEGORY_SOCIAL": "social",
    "CATEGORY_UPDATES": "updates",
    "CATEGORY_FORUMS": "forums",
}

# Money, commitments, contracts, third-party obligations: permanently excluded
# from auto-action at every level (plan §1). Tagged from day one and
# never suggested as junk.
SENSITIVE_PATTERN = re.compile(
    r"\b(invoice|payment|paid|contract|agreement|purchase order|wire transfer|"
    r"overdue|past due|billing|refund|docusign|e-?sign(ature)?|signature)\b",
    re.IGNORECASE,
)
AUTOMATED_SENDER_PATTERN = re.compile(r"\b(no-?reply|do-?not-?reply|notifications?)@", re.IGNORECASE)


def _addresses(header_value):
    return {addr.lower() for _, addr in getaddresses([header_value or ""]) if addr}


def classify(meta, my_address):
    """Return (triage, reasons) for one message's metadata."""
    labels = set(meta["label_ids"])
    headers = meta["headers"]
    subject = headers.get("Subject", "")
    reasons = []

    category = next((name for label, name in GMAIL_CATEGORIES.items() if label in labels), None)
    precedence = headers.get("Precedence", "").strip().lower()
    auto_submitted = headers.get("Auto-Submitted", "").strip().lower()

    bulk_signals = []
    if category:
        bulk_signals.append(f"Gmail label {category}")
    if "List-Unsubscribe" in headers:
        bulk_signals.append("has unsubscribe header")
    if precedence in ("bulk", "list", "junk"):
        bulk_signals.append(f"Precedence: {precedence}")
    if auto_submitted and auto_submitted != "no":
        bulk_signals.append("auto-submitted")
    if AUTOMATED_SENDER_PATTERN.search(headers.get("From", "")):
        bulk_signals.append("automated sender address")

    sensitive = SENSITIVE_PATTERN.search(subject)

    if not bulk_signals:
        if my_address in _addresses(headers.get("To")):
            triage = "needs_response"
            reasons.append("from a person; you're in To:")
        elif "IMPORTANT" in labels:
            triage = "needs_response"
            reasons.append("from a person; Gmail marked IMPORTANT")
        else:
            triage = "fyi"
            reasons.append("from a person, but you're only cc'd or on a list")
    elif (category == "promotions" or precedence == "junk") and not sensitive:
        triage = "junk"
        reasons.extend(bulk_signals)
        reasons.append("unsubscribe available" if "List-Unsubscribe" in headers else "no unsubscribe header: mark as junk")
        if "UNREAD" in labels:
            reasons.append("unread")
    else:
        triage = "fyi"
        reasons.extend(bulk_signals)

    if sensitive:
        reasons.append(f"SENSITIVE: subject mentions '{sensitive.group(0).lower()}' (human-only at every level)")
    return triage, reasons


def run(max_results, baseline=False):
    previous_start = decision_log.last_timestamp("run_start")
    if previous_start is None or baseline:
        # Baseline: the newest messages, re-triaged even if already logged (e.g. after a rules change).
        ids = gmail_client.list_inbox_ids(limit=max_results)[:max_results]
        new_ids = ids
        window = f"baseline, newest {max_results} inbox messages"
    else:
        since = previous_start - OVERLAP
        ids = gmail_client.list_inbox_ids(after_epoch=since.timestamp())
        new_ids = decision_log.unseen(ids)
        window = f"inbox messages received after {since.isoformat()}"

    if len(new_ids) > max_results:
        # Abort before logging run_start so the next run still covers these messages.
        sys.exit(f"{len(new_ids)} new messages exceeds --max {max_results}; nothing logged. Re-run with --max {len(new_ids)}.")

    my_address = gmail_client.get_my_address()
    decision_log.log_decision(
        "run_start",
        reasoning=f"{LEVEL} level, gmail.readonly, classifier v{CLASSIFIER_VERSION}; {window}",
        outcome=f"{len(new_ids)} to triage of {len(ids)} listed",
    )
    counts = {}
    try:
        for meta in gmail_client.get_metadata(new_ids):
            triage, reasons = classify(meta, my_address)
            decision_log.log_decision(
                ACTION_TYPES[triage],
                subject=meta["headers"].get("Subject"),
                reasoning="; ".join(reasons),
                outcome=f"triage={triage}; no inbox action taken ({LEVEL}: read-only; classifier v{CLASSIFIER_VERSION})",
                message_id=meta["id"],
            )
            counts[triage] = counts.get(triage, 0) + 1
    except BaseException as e:
        # Exception type only: messages from API errors aren't guaranteed free of email content.
        decision_log.log_decision("run_end", outcome=f"failed ({type(e).__name__}) after {counts}")
        raise
    decision_log.log_decision("run_end", outcome=f"completed {counts}")
    return counts


def _handle_sigterm(signum, frame):
    raise SystemExit(f"agent halted by signal {signum}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--max", type=int, default=100, help="most messages to triage in one run (first run / --baseline: newest N)")
    parser.add_argument(
        "--baseline", action="store_true", help="re-triage the newest --max messages even if already logged"
    )
    args = parser.parse_args()

    if KILLED_PATH.exists():
        sys.exit(f"Kill switch is engaged ({KILLED_PATH.name} exists). Review, then delete it to re-enable.")

    signal.signal(signal.SIGTERM, _handle_sigterm)
    PID_PATH.write_text(str(os.getpid()))
    try:
        counts = run(args.max, baseline=args.baseline)
    finally:
        gmail_client.close()
        PID_PATH.unlink(missing_ok=True)

    total = sum(counts.values())
    print(f"{LEVEL} run complete: {total} messages logged to {decision_log.DB_PATH.name} {counts}")


if __name__ == "__main__":
    main()
