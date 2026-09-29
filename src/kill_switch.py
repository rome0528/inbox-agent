"""Emergency stop: halt any running agent and revoke its Gmail OAuth token.

Steps, in order:
  1. Write the .killed sentinel so the agent refuses to start again.
  2. SIGTERM the running agent (SIGKILL if it hasn't exited after 5s).
  3. Revoke the token with Google and delete token.json.
  4. Record the event in decisions.db (evidence for incidents.md / Gate 4).

Stdlib only, so it works even if the project's dependencies are broken.
Usage: python src/kill_switch.py
"""

import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import decision_log

ROOT = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT / "token.json"
PID_PATH = ROOT / "agent.pid"
KILLED_PATH = ROOT / ".killed"

REVOKE_URL = "https://oauth2.googleapis.com/revoke"
MANUAL_REVOKE_URL = "https://myaccount.google.com/permissions"


def _is_agent_process(pid):
    """Guard against a stale pid file pointing at an unrelated process."""
    result = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True)
    return "agent.py" in result.stdout


def _alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def halt_agent():
    if not PID_PATH.exists():
        return "no running agent (no agent.pid)"
    pid = int(PID_PATH.read_text().strip())
    if not _alive(pid) or not _is_agent_process(pid):
        PID_PATH.unlink(missing_ok=True)
        return f"stale agent.pid ({pid}) removed; agent was not running"

    os.kill(pid, signal.SIGTERM)
    for _ in range(50):
        if not _alive(pid):
            break
        time.sleep(0.1)
    else:
        os.kill(pid, signal.SIGKILL)
    PID_PATH.unlink(missing_ok=True)
    return f"agent process {pid} halted"


def revoke_token():
    """Return (ok, message)."""
    if not TOKEN_PATH.exists():
        return True, f"no token.json; nothing to revoke locally (verify at {MANUAL_REVOKE_URL} if unsure)"

    data = json.loads(TOKEN_PATH.read_text())
    # Revoking the refresh token also invalidates its access tokens.
    token = data.get("refresh_token") or data.get("token")
    ok, message = False, "token.json had no token to revoke"
    if token:
        req = urllib.request.Request(
            REVOKE_URL,
            data=urllib.parse.urlencode({"token": token}).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            urllib.request.urlopen(req, timeout=10)
            ok, message = True, "token revoked with Google"
        except urllib.error.HTTPError as e:
            # 400 means Google no longer recognises the token (already revoked or expired).
            ok = e.code == 400
            message = f"Google returned HTTP {e.code}" + (" (token already invalid)" if ok else "")
        except urllib.error.URLError as e:
            message = f"could not reach Google: {e.reason}"

    if not ok and token:
        # Keep the token so the revoke can be retried; .killed still blocks the agent.
        return ok, message + "; token.json kept so you can re-run the kill switch"
    TOKEN_PATH.unlink()
    return ok, message + "; token.json deleted"


def main():
    KILLED_PATH.write_text(time.strftime("%Y-%m-%dT%H:%M:%S%z") + "\n")
    print(f"[1/3] kill switch engaged ({KILLED_PATH.name} written)")
    halted = halt_agent()
    print(f"[2/3] {halted}")
    ok, message = revoke_token()
    print(f"[3/3] {message}")
    decision_log.log_decision(
        "kill_switch",
        reasoning="manual kill switch invoked",
        outcome=f"{halted}; {message}" + ("" if ok else "; REVOKE NOT CONFIRMED"),
    )
    if not ok:
        print(f"REVOKE NOT CONFIRMED. Remove access manually: {MANUAL_REVOKE_URL}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
