#voice implementation
import speech_recognition as sr
import os 
from pydub import AudioSegment
from config.logging import voice_handler_logger

def transcibe_audio(audio_file:str) -> str:
    """
    Transcribes audio from a file to text using the Google web speech API
    Args:
        audio_file (str): Path to the audio file to be transcribed.
    """
    try:
        #initialize the recognizer 
        recognizer = sr.Recognizer()

        #load the audio file 
        audio = AudioSegment.from_file(audio_file)

        #convert the audio file to a .wav format 
        wav_file = audio_file.replace(".mp3", ".wav")

        #save the audio file in .wav format
        audio.export(wav_file, format = "wav")

        with sr.AudioFile(wav_file) as source:
            #adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            #record the audio
            audio_data = recognizer.record(source)
            try:
                #transcribe the audio using Google web speech API
                text = recognizer.recognize_google(audio_data)
                voice_handler_logger.info(f"Transcription successful: {text}")
                return text
            except sr.UnknownValueError:
                voice_handler_logger.error("Google Web Speech API could not understand the audio.")
                return "Could not understand the audio."
    except Exception as e:
        voice_handler_logger.error(f"Error initializing recognizer: {e}")
        raise e
