#voice implementation
import speech_recognition as sr
import os 
from pydub import AudioSegment
from config.logging import voice_input_logger

def transcibe_audio(audio_file:str) -> str:
    """
    Transcribes audio from a file to text using the Google web speech API
    Args:
        audio_file (str): Path to the audio file to be transcribed.
    """
    try:
        #initialize the recognizer 
        recognizer = sr.Recognizer()
    except Exception as e:
        voice_input_logger.error(f"Error initializing recognizer: {e}")
        raise e
