import aiohttp

import asyncio
from contextlib import suppress
import json
import sys
import traceback

from subscribe_to_twitch_events import create_twitch_chat_event_sub


async def start_client(url: str) -> None:
    print("client started")

    async def dispatch(ws: aiohttp.ClientWebSocketResponse) -> None:
        print("session started")
        while True:
            msg = await ws.receive()
            try:
                match msg.type:
                    case aiohttp.WSMsgType.TEXT:
                        handle_tw_ws_message_type_text(msg.data)
                    case aiohttp.WSMsgType.BINARY:
                        print(msg.data)
                    case aiohttp.WSMsgType.PING:  # aiohttp automatically handles ping pong, so this can likely be removed
                        await ws.pong()
                    case aiohttp.WSMsgType.PONG:
                        print('pong')
                    case aiohttp.WSMsgType.CLOSE:
                        print('connection close received')
                        print(msg)
                        await ws.close()
                    case aiohttp.WSMsgType.ERROR:
                        print(ws.exception())
                    case aiohttp.WSMsgType.CLOSED:
                        print("connection Closed")
                        pass
            except Exception:
                traceback.print_exc()
                await ws.close()
                break

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url=url, autoclose=False, autoping=True) as ws:
            dispatch_task = asyncio.create_task(dispatch(ws))

            while line := await asyncio.to_thread(sys.stdin.readline):
                await ws.send_str(line)

                dispatch_task.cancel()
                with suppress(asyncio.CancelledError):
                    await dispatch_task


def handle_tw_ws_message_type_text(msg):
    data = json.loads(msg)
    metadata = data['metadata']
    payload = data['payload']
    # TODO check for duplicate message
    match metadata['message_type']:
        case 'session_welcome':
            session_id = payload['session']['id']
            create_twitch_chat_event_sub(session_id)
        case 'session_keepalive':
            print(payload)
            # TODO add handling to extend the healthy session if needed, otherwise pass
            print('session_keepalive')
            pass
        case 'notification':
            print(payload)
            # TODO add handling for notification sub type. for now print type return payload
            print('notification')
        case 'session_reconnect':
            print(payload)
            # TODO reconnect handler
            print('session_reconnect')
            pass


asyncio.run(start_client(
    url='wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30'))
