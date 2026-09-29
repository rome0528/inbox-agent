"""Grade the agent's triage calls. This is the Gate 1 (Performance) evidence.

Interactive: walks through ungraded triage calls, oldest first, and records your
verdict in the `reviews` table. `--summary` prints the numbers for the weekly
row in governance/metrics.md.

Usage:
  python src/review.py [--days N]            grade calls from the last N days (default: all)
  python src/review.py --summary [--days 7]  accuracy report
"""

import argparse
import re
import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timedelta, timezone

import decision_log

BUCKETS = ("needs_response", "junk", "fyi")
KEYS = {"r": "needs_response", "j": "junk", "f": "fyi"}

# Plan §4: a bucket with fewer graded items than this in a week is judged on the pooled window total.
MIN_WEEKLY_SAMPLE = 5

# Daily launchd slot (scripts/com.inboxagent.daily.plist) and the run-time SLA for Gate 1 (plan §4).
SCHEDULED_HOUR = 7
RUN_TIME_SLA = timedelta(minutes=15)
TRIAGE_PATTERN = re.compile(r"triage=(\w+)")


def _cutoff(days):
    if days is None:
        return ""
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")


def _rows(sql, params):
    decision_log.init_db()
    with closing(sqlite3.connect(decision_log.DB_PATH)) as conn:
        return conn.execute(sql, params).fetchall()


def ungraded(days):
    rows = _rows(
        "SELECT d.id, d.target, d.reasoning, d.outcome FROM decisions d "
        "LEFT JOIN reviews r ON r.decision_id = d.id "
        "WHERE r.decision_id IS NULL AND d.outcome LIKE 'triage=%' AND d.timestamp >= ? ORDER BY d.id",
        (_cutoff(days),),
    )
    return [(i, subject, reasoning, TRIAGE_PATTERN.search(outcome).group(1)) for i, subject, reasoning, outcome in rows]


def grade(days):
    todo = ungraded(days)
    if not todo:
        print("Nothing to grade.")
        return
    prompt = "Correct?  [y]es  [r]espond  [j]unk  [f]yi  [s]kip  [q]uit > "
    graded = 0
    for n, (decision_id, subject, reasoning, predicted) in enumerate(todo, 1):
        print(f"\n[{n}/{len(todo)}]  Subject: {subject}")
        print(f"        Agent said: {predicted}   ({reasoning})")
        while True:
            answer = input(prompt).strip().lower()[:1]
            if answer in ("y", "s", "q") or answer in KEYS:
                break
        if answer == "q":
            break
        if answer == "s":
            continue
        decision_log.record_review(decision_id, predicted, predicted if answer == "y" else KEYS[answer])
        graded += 1
    print(f"\nGraded {graded}. Run with --summary for the numbers.")


def _pct(num, den):
    return f"{num / den:.0%}" if den else "n/a"


def summary(days):
    rows = _rows(
        "SELECT r.predicted, r.actual FROM reviews r JOIN decisions d ON d.id = r.decision_id "
        "WHERE d.timestamp >= ?",
        (_cutoff(days),),
    )
    window = f"Last {days} days" if days is not None else "All time"
    correct = sum(p == a for p, a in rows)
    print(f"{window}: {len(rows)} reviewed, {correct} correct ({_pct(correct, len(rows))})")

    actual_resp = [p for p, a in rows if a == "needs_response"]
    caught = sum(p == "needs_response" for p in actual_resp)
    print(f"  needs_response: caught {caught} of {len(actual_resp)} that really needed a reply ({_pct(caught, len(actual_resp))})")

    called_junk = [a for p, a in rows if p == "junk"]
    right = sum(a == "junk" for a in called_junk)
    print(f"  junk:           {right} of {len(called_junk)} junk calls were right ({_pct(right, len(called_junk))})")

    small = [name for name, n in (("needs_response", len(actual_resp)), ("junk", len(called_junk))) if n < MIN_WEEKLY_SAMPLE]
    if small and days is not None:
        print(f"  small sample (< {MIN_WEEKLY_SAMPLE}) for {', '.join(small)}: judge on the pooled total for the whole")
        print("  observation window (re-run with --days covering it), per plan §4")

    ungraded_count = len(ungraded(days))
    if ungraded_count:
        print(f"  ({ungraded_count} calls in this window not yet graded)")

    availability(days)


def availability(days):
    """Gate 1 availability (ATF): completed scheduled daily runs / scheduled daily runs, plus run-time SLA."""
    runs = _rows(
        "SELECT action_type, timestamp, outcome FROM decisions "
        "WHERE action_type IN ('run_start', 'run_end') ORDER BY id",
        (),
    )
    if not runs:
        print("  availability:   no runs yet")
        return
    now = datetime.now().astimezone()
    start = datetime.fromisoformat(runs[0][1]).astimezone()
    if days is not None:
        start = max(start, now - timedelta(days=days))

    # One scheduled slot per day at SCHEDULED_HOUR local time, after the window start.
    slots, day = [], start.replace(hour=SCHEDULED_HOUR, minute=0, second=0, microsecond=0)
    while day <= now:
        if day > start:
            slots.append(day)
        day += timedelta(days=1)

    completed = [
        datetime.fromisoformat(ts).astimezone()
        for kind, ts, outcome in runs
        if kind == "run_end" and outcome.startswith("completed")
    ]
    met = sum(any(c >= slot and c.date() == slot.date() for c in completed) for slot in slots)
    failed = sum(
        1 for kind, ts, outcome in runs
        if kind == "run_end" and not outcome.startswith("completed") and datetime.fromisoformat(ts).astimezone() >= start
    )
    print(f"  availability:   {met} of {len(slots)} scheduled daily runs completed ({_pct(met, len(slots))}); {failed} failed runs")
    print("  (runs that failed before starting, e.g. sign-in needed, are only in logs/agent.log)")

    durations, started = [], None
    for kind, ts, _ in runs:
        t = datetime.fromisoformat(ts)
        if kind == "run_start":
            started = t
        elif started is not None:
            if t.astimezone() >= start:
                durations.append(t - started)
            started = None
    if durations:
        longest = max(durations)
        verdict = "met" if longest <= RUN_TIME_SLA else "MISSED"
        print(f"  run time:       longest {int(longest.total_seconds())}s (SLA {int(RUN_TIME_SLA.total_seconds() // 60)} min: {verdict})")

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--summary", action="store_true", help="print accuracy instead of grading")
    parser.add_argument("--days", type=int, help="only calls logged in the last N days")
    args = parser.parse_args()
    if args.summary:
        summary(args.days)
    else:
        try:
            grade(args.days)
        except (KeyboardInterrupt, EOFError):
            sys.exit("\nStopped; grades so far are saved.")


if __name__ == "__main__":
    main()
