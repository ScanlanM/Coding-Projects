"""Obtain and refresh a Twitch OAuth user access token.

The very first run needs a one-time authorization `code` (see
get_twitch_user_consent_index.html for how to get one). After that,
this module stores the resulting access/refresh tokens in a local
cache file and refreshes them automatically, so the one-time code is
never needed again and a token never gets silently reused past its
expiry.
"""

import json
import logging
import os
import time
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
CACHE_PATH = Path(__file__).with_name(".twitch_token_cache.json")
# Refresh a little before the real expiry so a request never straddles it.
EXPIRY_BUFFER_SECONDS = 60

# In-memory copy of the cache so repeated calls in the same process don't
# need to hit disk every time.
_memory_cache = {}


def _load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            logger.warning("Token cache file was unreadable, ignoring it.")
    return {}


def _save_cache(data):
    CACHE_PATH.write_text(json.dumps(data))


def _is_valid(token_data):
    if not token_data or "access_token" not in token_data:
        return False
    expires_at = token_data.get("obtained_at", 0) + token_data.get("expires_in", 0)
    return time.time() < expires_at - EXPIRY_BUFFER_SECONDS


def _request_token(payload):
    body = urllib.parse.urlencode(payload)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, headers=headers, data=body)

    if not response.ok:
        # Twitch error responses look like {"status": 400, "message": "..."}.
        # Never log the raw body here, it can contain token material.
        try:
            detail = response.json().get("message", "no message")
        except ValueError:
            detail = "no message"
        raise RuntimeError(f"Twitch token request failed ({response.status_code}): {detail}")

    data = response.json()
    data["obtained_at"] = time.time()
    return data


def get_auth_token():
    """Return a valid Twitch user access token, refreshing/exchanging as needed."""
    load_dotenv()

    if _is_valid(_memory_cache):
        return _memory_cache["access_token"]

    cached = _load_cache()
    if _is_valid(cached):
        _memory_cache.clear()
        _memory_cache.update(cached)
        return cached["access_token"]

    client_id = os.environ.get("TWITCH_CLIENT_ID")
    client_secret = os.environ.get("TWITCH_CLIENT_SECRET")

    if cached.get("refresh_token"):
        logger.info("Refreshing Twitch access token.")
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": cached["refresh_token"],
        }
    else:
        logger.info("Exchanging Twitch authorization code for an access token.")
        auth_code = os.environ.get("MY_AUTH_TWITCH_CODE")
        if not auth_code:
            raise RuntimeError(
                "No cached refresh token and MY_AUTH_TWITCH_CODE is not set. "
                "Use get_twitch_user_consent_index.html to get a fresh code."
            )
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost",
        }

    token_data = _request_token(payload)
    _memory_cache.clear()
    _memory_cache.update(token_data)
    _save_cache(token_data)

    return token_data["access_token"]
