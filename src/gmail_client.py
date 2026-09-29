"""Read-only Gmail access for the Intern-level agent.

Scope is gmail.readonly and nothing else (Intern). This module deliberately exposes no
send, delete, modify, or label operations, and it never fetches message bodies:
messages are requested with format="metadata" and only whitelisted headers are
returned. Gmail's `snippet` field (a preview of the body) is dropped too.
"""

import json
import os
import sys
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = ROOT / "credentials.json"
TOKEN_PATH = ROOT / "token.json"

# The Gmail permission for the current maturity level. It changes only at a signed-off promotion or
# demotion; see docs/architecture.md → Gmail permission ladder. Tokens with any other scopes are refused.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# The only message fields the agent is allowed to see.
METADATA_HEADERS = [
    "From", "To", "Cc", "Subject", "Date", "List-Unsubscribe", "Precedence", "Auto-Submitted",
]


class AuthRequired(RuntimeError):
    """Raised when a new interactive sign-in is needed."""


def _assert_scopes(scopes):
    if set(scopes or []) != set(SCOPES):
        raise PermissionError(
            f"Refusing to use token with scopes {scopes!r}; the current level allows only {SCOPES!r}. "
            f"Delete {TOKEN_PATH.name} and re-authorize."
        )


def _save_token(creds):
    TOKEN_PATH.write_text(creds.to_json())
    os.chmod(TOKEN_PATH, 0o600)


def get_credentials():
    """Load the cached token, refreshing or running the OAuth flow as needed."""
    creds = None
    if TOKEN_PATH.exists():
        _assert_scopes(json.loads(TOKEN_PATH.read_text()).get("scopes"))
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
            return creds
        except RefreshError:
            # Refresh tokens for OAuth apps in "Testing" mode expire after 7 days; re-authorize.
            TOKEN_PATH.unlink(missing_ok=True)

    if not sys.stdin.isatty():
        # Scheduled runs have no one to click through Google's sign-in page; fail instead of hanging.
        raise AuthRequired("Gmail sign-in needed. Run `.venv/bin/python src/agent.py` in a terminal once.")
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(f"OAuth client file not found: {CREDENTIALS_PATH}")
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)
    _assert_scopes(getattr(creds, "granted_scopes", None) or creds.scopes)
    _save_token(creds)
    return creds


def _to_metadata(msg):
    """Whitelist the fields we keep; everything else (snippet, payload body) is discarded."""
    # Header names arrive in whatever case the sender used; normalise to METADATA_HEADERS spelling.
    canonical = {h.lower(): h for h in METADATA_HEADERS}
    headers = {
        canonical[h["name"].lower()]: h["value"]
        for h in msg.get("payload", {}).get("headers", [])
        if h["name"].lower() in canonical
    }
    return {
        "id": msg["id"],
        "label_ids": list(msg.get("labelIds", [])),
        "headers": headers,
    }


_service_instance = None


def _service():
    """One Gmail connection per process; release it with close()."""
    global _service_instance
    if _service_instance is None:
        _service_instance = build("gmail", "v1", credentials=get_credentials(), cache_discovery=False)
    return _service_instance


def close():
    global _service_instance
    if _service_instance is not None:
        _service_instance.close()
        _service_instance = None


def get_my_address():
    """The signed-in account's email address (read-only profile call)."""
    return _service().users().getProfile(userId="me").execute()["emailAddress"].lower()


def list_inbox_ids(after_epoch=None, limit=None):
    """Return inbox message ids (newest first), optionally only those received after `after_epoch`.

    With `limit`, stops once more than `limit` ids are found, so callers can detect overflow.
    """
    messages = _service().users().messages()
    query = f"after:{int(after_epoch)}" if after_epoch is not None else None
    ids, page_token = [], None
    while True:
        resp = messages.list(
            userId="me", labelIds=["INBOX"], q=query, maxResults=500, pageToken=page_token
        ).execute()
        ids.extend(ref["id"] for ref in resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token or (limit is not None and len(ids) > limit):
            return ids


def get_metadata(message_ids):
    """Yield metadata dicts for the given message ids. Read-only; never fetches bodies."""
    messages = _service().users().messages()
    for message_id in message_ids:
        msg = messages.get(
            userId="me",
            id=message_id,
            format="metadata",
            metadataHeaders=METADATA_HEADERS,
        ).execute()
        yield _to_metadata(msg)
