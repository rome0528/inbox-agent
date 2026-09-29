"""Decision log backed by decisions.db (SQLite), per governance/agentic-promotion-plan.md §4.

Hard rule: no email body content is ever written here. `target` is the subject
line only (whitespace-collapsed and truncated), and the free-text fields are
length-capped so a message body can't end up in them. Oversized input is
rejected rather than silently stored.

`seen_messages` sits alongside the plan's `decisions` table so a message is
logged once no matter how often the agent runs. It stores a SHA-256 of the
Gmail message id, never the id itself.

`reviews` holds your grading of the agent's triage calls (Gate 1 evidence),
kept separate so `decisions` stays exactly as the agent wrote it.
"""

import hashlib
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "decisions.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action_type TEXT NOT NULL,       -- 'read', 'flag', 'propose_reply', 'archive', etc.
    target TEXT,                     -- subject line only — NEVER full email body
    reasoning TEXT,                  -- agent's stated reasoning
    outcome TEXT,                    -- what happened
    accepted INTEGER                 -- NULL at Intern; 1/0 once Junior+ (you approve/reject)
);

CREATE TABLE IF NOT EXISTS seen_messages (
    message_hash TEXT PRIMARY KEY,   -- sha256 of the Gmail message id
    first_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    decision_id INTEGER PRIMARY KEY REFERENCES decisions(id),
    predicted TEXT NOT NULL,         -- the agent's triage bucket
    actual TEXT NOT NULL,            -- your call
    reviewed_at TEXT NOT NULL
);
"""

MAX_SUBJECT_CHARS = 200
MAX_ACTION_TYPE_CHARS = 32
MAX_TEXT_CHARS = 500


def _clean_subject(subject):
    if subject is None:
        return None
    subject = " ".join(str(subject).split())
    if len(subject) > MAX_SUBJECT_CHARS:
        subject = subject[: MAX_SUBJECT_CHARS - 1] + "…"
    return subject


def _check_text(name, value, limit):
    if value is None:
        return None
    value = str(value)
    if len(value) > limit:
        raise ValueError(
            f"{name} is {len(value)} chars (limit {limit}); refusing to log in case it contains body content"
        )
    return value


def init_db(db_path=DB_PATH):
    with closing(sqlite3.connect(db_path)) as conn:
        conn.executescript(SCHEMA)
    # Subject lines are personal data: owner-only access.
    os.chmod(db_path, 0o600)


def _hash_id(message_id):
    return hashlib.sha256(message_id.encode()).hexdigest()


def unseen(message_ids, db_path=DB_PATH):
    """Filter `message_ids` down to those not yet logged, preserving order."""
    init_db(db_path)
    with closing(sqlite3.connect(db_path)) as conn:
        seen = {row[0] for row in conn.execute("SELECT message_hash FROM seen_messages")}
    return [m for m in message_ids if _hash_id(m) not in seen]


def last_timestamp(action_type, db_path=DB_PATH):
    """Most recent timestamp logged for `action_type` as a datetime, or None."""
    if not Path(db_path).exists():
        return None
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute(
            "SELECT MAX(timestamp) FROM decisions WHERE action_type = ?", (action_type,)
        ).fetchone()
    return datetime.fromisoformat(row[0]) if row and row[0] else None


def log_decision(
    action_type, *, subject=None, reasoning=None, outcome=None, accepted=None, message_id=None, db_path=DB_PATH
):
    """Append one row. `subject` must be the email's subject line — never its body.

    With `message_id`, the message is marked seen in the same transaction.
    """
    action_type = _check_text("action_type", action_type, MAX_ACTION_TYPE_CHARS)
    if not action_type:
        raise ValueError("action_type is required")
    if accepted not in (None, 0, 1):
        raise ValueError("accepted must be None, 0, or 1")

    row = (
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
        action_type,
        _clean_subject(subject),
        _check_text("reasoning", reasoning, MAX_TEXT_CHARS),
        _check_text("outcome", outcome, MAX_TEXT_CHARS),
        accepted,
    )
    init_db(db_path)
    with closing(sqlite3.connect(db_path)) as conn, conn:
        cur = conn.execute(
            "INSERT INTO decisions (timestamp, action_type, target, reasoning, outcome, accepted) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            row,
        )
        if message_id is not None:
            conn.execute(
                "INSERT OR IGNORE INTO seen_messages (message_hash, first_seen) VALUES (?, ?)",
                (_hash_id(message_id), row[0]),
            )
        return cur.lastrowid


def record_review(decision_id, predicted, actual, db_path=DB_PATH):
    init_db(db_path)
    with closing(sqlite3.connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT OR REPLACE INTO reviews (decision_id, predicted, actual, reviewed_at) VALUES (?, ?, ?, ?)",
            (decision_id, predicted, actual, datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
