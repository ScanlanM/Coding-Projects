"""Text-to-speech helper built on the ElevenLabs API.

Importing this module does nothing by itself; call speak() to actually
convert text to audio and play it. This keeps it safe to import from
other modules (e.g. the Twitch chat listener) without triggering an
API call and audio playback as a side effect of the import.
"""

import logging
import os

from dotenv import load_dotenv
from elevenlabs import play
from elevenlabs.client import ElevenLabs

logger = logging.getLogger(__name__)

load_dotenv()

DEFAULT_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
DEFAULT_MODEL_ID = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set in the environment.")
        _client = ElevenLabs(api_key=api_key)
    return _client


def speak(text, voice_id=DEFAULT_VOICE_ID, model_id=DEFAULT_MODEL_ID):
    """Convert `text` to speech with ElevenLabs and play it back."""
    if not text:
        return

    audio = _get_client().text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format="mp3_22050_32",
    )
    play(audio)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    speak("Place holder text, to be updated beyond MVP")
