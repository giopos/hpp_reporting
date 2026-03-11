"""
Usage tracker for Swimmer Dashboard.
Logs activity to a local JSONL file and can push logs to GitHub repo.
All tracking is silent — errors never surface to users.
"""

import datetime
import json
import os
import secrets
from pathlib import Path
from typing import Optional

import streamlit as st

LOG_FILE = Path("usage_logs.jsonl")


def get_session_id():
    """Return a stable anonymous session ID for the current browser session."""
    if "tracker_session_id" not in st.session_state:
        st.session_state.tracker_session_id = secrets.token_hex(8)
    return st.session_state.tracker_session_id


def _is_new_session():
    """True the first time the app runs in this session."""
    if "tracker_started" not in st.session_state:
        st.session_state.tracker_started = True
        return True
    return False


def log_event(event: str, details: Optional[dict] = None):
    """Append one event to the JSONL log file."""
    try:
        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "sid": get_session_id(),
            "event": event,
            "details": details or {},
        }
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass  # never break the app


def track_app_start():
    """Call once per session — logs 'app_start'."""
    if _is_new_session():
        log_event("app_start")


def track_page_view(page: str):
    """Track which page/section the user is viewing."""
    key = f"tracker_seen_{page}"
    if key not in st.session_state:
        st.session_state[key] = True
        log_event("page_view", {"page": page})


def track_template_download():
    log_event("template_download")


def track_file_upload(filename: str, num_records: int, num_swimmers: int):
    log_event("file_upload", {
        "filename": filename,
        "records": num_records,
        "swimmers": num_swimmers,
    })


def track_pdf_export(swimmer: str, stroke: str, date: str):
    log_event("pdf_export", {
        "swimmer": swimmer,
        "stroke": stroke,
        "date": date,
    })


def track_pdf_download(swimmer: str):
    log_event("pdf_download", {"swimmer": swimmer})


def track_bulk_export(count: int, date: str):
    log_event("bulk_export", {
        "count": count,
        "date": date,
    })


def track_bulk_download(count: int):
    log_event("bulk_download", {"count": count})


def track_swimmer_view(swimmer: str, stroke: str, date: str):
    log_event("swimmer_view", {
        "swimmer": swimmer,
        "stroke": stroke,
        "date": date,
    })


# ---------------------------------------------------------------------------
# GitHub auto-push (optional, uses Streamlit secrets)
# ---------------------------------------------------------------------------

def push_logs_to_github():
    """
    Push the JSONL log to the private GitHub repo.
    Requires these Streamlit secrets:
        [github]
        token = "ghp_..."
        repo  = "username/repo-name"
    Returns (success: bool, message: str).
    """
    try:
        import base64
        import requests

        token = st.secrets.get("github", {}).get("token")
        repo = st.secrets.get("github", {}).get("repo")

        if not token or not repo:
            return False, "GitHub secrets not configured."

        if not LOG_FILE.exists():
            return False, "No log file to push."

        content = LOG_FILE.read_text()
        if not content.strip():
            return False, "Log file is empty."

        url = f"https://api.github.com/repos/{repo}/contents/logs/usage_logs.jsonl"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Check if file already exists (need SHA to update)
        resp = requests.get(url, headers=headers, timeout=15)
        sha = resp.json().get("sha") if resp.status_code == 200 else None

        payload = {
            "message": f"Update usage logs — {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "content": base64.b64encode(content.encode()).decode(),
        }
        if sha:
            payload["sha"] = sha

        put_resp = requests.put(url, headers=headers, json=payload, timeout=15)
        if put_resp.status_code in (200, 201):
            return True, "Logs pushed to GitHub."
        return False, f"GitHub API error: {put_resp.status_code}"

    except ImportError:
        return False, "requests library not installed."
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Admin helpers — read & summarise logs
# ---------------------------------------------------------------------------

def read_logs():
    """Return list of log dicts, newest first."""
    if not LOG_FILE.exists():
        return []
    entries = []
    for line in LOG_FILE.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    entries.reverse()
    return entries


def summarise_logs(entries: list) -> dict:
    """Return a quick summary dict from log entries."""
    sessions = set()
    events = {}
    for e in entries:
        sessions.add(e.get("sid", ""))
        evt = e.get("event", "unknown")
        events[evt] = events.get(evt, 0) + 1
    return {
        "total_events": len(entries),
        "unique_sessions": len(sessions),
        "events_breakdown": events,
    }


def get_log_file_bytes() -> Optional[bytes]:
    """Return raw log bytes for download, or None."""
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 0:
        return LOG_FILE.read_bytes()
    return None
