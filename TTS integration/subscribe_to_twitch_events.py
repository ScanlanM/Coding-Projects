from dotenv import load_dotenv

import os
import requests
import json
import logging

from get_twitch_auth_token import get_auth_token


def create_twitch_chat_event_sub(session_id):
    load_dotenv()
    # TODO access token and cache handling
    access_token = os.environ.get("TWITCH_ACCESS_TOKEN")
    # access_token = get_auth_token()

    event_sub_url = "https://api.twitch.tv/helix/eventsub/subscriptions"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': os.environ.get("TWITCH_CLIENT_ID"),
        'Content-Type': 'application/json'
    }
    event_type = "channel.chat.message"

    user_id = os.environ.get("TWITCH_USER_ID")
    broadcaster_id = os.environ.get("TARGET_BROADCASTER")

    payload = {
        "type": event_type,
        "version": "1",
        "condition": {
            "broadcaster_user_id": broadcaster_id,
            "user_id": user_id
        },
        "transport": {
            "method": "websocket",
            "session_id": session_id
        }
    }
    payload = json.dumps(payload)

    r = requests.post(event_sub_url, headers=headers, data=payload)
    print(r.raise_for_status())
