from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")

client = ElevenLabs(
    api_key=api_key
)

textToRead = "Place holder text, to be updated beyond MVP"

# response = client.voices.search()
# print(response.voices)

voice_choice = "JBFqnCBsd6RMkjVDRZzb"

audio = client.text_to_speech.convert(

    text=textToRead,  # pull in text
    voice_id=voice_choice,
    model_id="eleven_multilingual_v2",
    output_format="mp3_22050_32"

)

play(audio)
