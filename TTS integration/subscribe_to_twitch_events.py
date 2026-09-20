"""Create a Twitch EventSub subscription for channel chat messages."""

import json
import logging
import os

import requests
from dotenv import load_dotenv

from get_twitch_auth_token import get_auth_token

logger = logging.getLogger(__name__)

EVENT_SUB_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"
CHAT_MESSAGE_EVENT_TYPE = "channel.chat.message"
CHAT_MESSAGE_EVENT_VERSION = "1"


def create_twitch_chat_event_sub(session_id):
    """Subscribe the given EventSub websocket session to chat messages."""
    load_dotenv()

    broadcaster_id = os.environ.get("TARGET_BROADCASTER")
    user_id = os.environ.get("TWITCH_USER_ID")
    if not broadcaster_id or not user_id:
        raise RuntimeError(
            "TARGET_BROADCASTER and TWITCH_USER_ID must be set in the environment."
        )

    headers = {
        "Authorization": f"Bearer {get_auth_token()}",
        "Client-Id": os.environ.get("TWITCH_CLIENT_ID"),
        "Content-Type": "application/json",
    }

    payload = {
        "type": CHAT_MESSAGE_EVENT_TYPE,
        "version": CHAT_MESSAGE_EVENT_VERSION,
        "condition": {
            "broadcaster_user_id": broadcaster_id,
            "user_id": user_id,
        },
        "transport": {
            "method": "websocket",
            "session_id": session_id,
        },
    }

    response = requests.post(EVENT_SUB_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()

    subscription = response.json()["data"][0]
    logger.info(
        "Subscribed to %s (subscription id: %s)",
        CHAT_MESSAGE_EVENT_TYPE,
        subscription["id"],
    )
    return subscription
