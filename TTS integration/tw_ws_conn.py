"""Twitch EventSub WebSocket client.

Connects to Twitch's EventSub WebSocket, subscribes to chat messages for
the configured broadcaster, and reads each chat message aloud via
tts_handle.speak().
"""

import asyncio
import json
import logging

import aiohttp

from subscribe_to_twitch_events import create_twitch_chat_event_sub
from tts_handle import speak

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

EVENTSUB_URL = "wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30"
# Bound how many recent message ids we remember, so this can't grow forever.
_MAX_SEEN_MESSAGE_IDS = 500
_seen_message_ids = []


def _already_seen(message_id):
    """Track message ids so a redelivered notification is only spoken once."""
    if message_id in _seen_message_ids:
        return True
    _seen_message_ids.append(message_id)
    if len(_seen_message_ids) > _MAX_SEEN_MESSAGE_IDS:
        del _seen_message_ids[: len(_seen_message_ids) - _MAX_SEEN_MESSAGE_IDS]
    return False


async def handle_notification(payload):
    subscription_type = payload["subscription"]["type"]

    if subscription_type != "channel.chat.message":
        logger.info("Ignoring notification for %s", subscription_type)
        return

    message_id = payload["event"].get("message_id") or payload["subscription"]["id"]
    if _already_seen(message_id):
        logger.debug("Skipping duplicate chat message notification.")
        return

    chat_text = payload["event"]["message"]["text"]
    logger.info("Chat message: %s", chat_text)
    try:
        await asyncio.to_thread(speak, chat_text)
    except Exception:
        logger.exception("Failed to speak chat message.")


async def handle_text_message(raw_message, on_reconnect):
    data = json.loads(raw_message)
    metadata = data["metadata"]
    payload = data["payload"]

    match metadata["message_type"]:
        case "session_welcome":
            session_id = payload["session"]["id"]
            try:
                await asyncio.to_thread(create_twitch_chat_event_sub, session_id)
            except Exception:
                logger.exception("Failed to create the chat message subscription.")
        case "session_keepalive":
            logger.debug("Keepalive received.")
        case "notification":
            await handle_notification(payload)
        case "session_reconnect":
            reconnect_url = payload["session"]["reconnect_url"]
            logger.info("Twitch requested a reconnect.")
            on_reconnect(reconnect_url)
        case _:
            logger.debug("Unhandled message_type: %s", metadata["message_type"])


async def run_session(url):
    """Run a single EventSub session. Returns a URL to reconnect to next,
    or None if the caller should back off and start over from EVENTSUB_URL.
    """
    reconnect_url = None

    def on_reconnect(new_url):
        nonlocal reconnect_url
        reconnect_url = new_url

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url=url, autoclose=False, autoping=True) as ws:
            logger.info("Session connected.")
            # aiohttp answers PING/PONG frames itself (autoping=True), so we
            # only need to handle the message types Twitch actually sends us.
            async for msg in ws:
                match msg.type:
                    case aiohttp.WSMsgType.TEXT:
                        await handle_text_message(msg.data, on_reconnect)
                        if reconnect_url:
                            return reconnect_url
                    case aiohttp.WSMsgType.ERROR:
                        logger.error("Websocket error: %s", ws.exception())
                        return None
                    case aiohttp.WSMsgType.CLOSE | aiohttp.WSMsgType.CLOSED:
                        logger.info("Connection closed.")
                        return None
    return None


async def main():
    url = EVENTSUB_URL
    while True:
        next_url = await run_session(url)
        if next_url:
            url = next_url
            continue
        logger.info("Reconnecting in 5 seconds...")
        await asyncio.sleep(5)
        url = EVENTSUB_URL


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down.")
