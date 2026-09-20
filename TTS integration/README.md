# TTS integration

Listens to a Twitch channel's chat via Twitch's EventSub WebSocket API
and reads each incoming chat message aloud using ElevenLabs
text-to-speech.

## How it works

1. `tw_ws_conn.py` opens a WebSocket connection to Twitch EventSub.
2. On `session_welcome`, `subscribe_to_twitch_events.py` subscribes
   that session to `channel.chat.message` events for the configured
   broadcaster.
3. Each incoming chat message notification is passed to
   `tts_handle.speak()`, which converts it to audio with ElevenLabs
   and plays it back.
4. `get_twitch_auth_token.py` manages the Twitch OAuth token. It's
   exchanged once from a one-time authorization code, then refreshed
   automatically after that, and cached in `.twitch_token_cache.json`
   (git-ignored, don't commit it).

## Setup

1. Create a Twitch application at
   https://dev.twitch.tv/console/apps and note its client ID and secret.
2. Copy `.env.example` to `.env` and fill in `TWITCH_CLIENT_ID`,
   `TWITCH_CLIENT_SECRET`, `TWITCH_USER_ID` (the account granting
   consent), `TARGET_BROADCASTER` (the channel to listen to), and
   `ELEVENLABS_API_KEY`.
3. Open `get_twitch_user_consent_index.html` in a browser, click
   through the consent flow, and copy the `code` value from the
   redirect URL into `MY_AUTH_TWITCH_CODE` in `.env`. This is only
   needed once.
4. Install dependencies: `pip install -r requirements.txt`
5. Run the client: `python tw_ws_conn.py`

## Known limitations

- Reconnects use a fixed 5 second delay rather than exponential
  backoff.
- `session_keepalive` messages are logged but there's no watchdog that
  detects a silently dropped connection between keepalives.
- No automated tests yet.
