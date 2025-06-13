from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def text_to_speech(text: str) -> str:
    """
    Convert text response to audio 
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found")
        client=OpenAI(api_key=api_key)
        # speech from text
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",  # alloy, echo, nova, shimmer
            input=text,
            speed=1.0  
        )
        audio_path = "response_audio.mp3"
        response.stream_to_file(audio_path)
        
        return audio_path
        
    except Exception as e:
        print(f"Voice synthesis failed: {str(e)}")
        return ""
