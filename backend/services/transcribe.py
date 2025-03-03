from deepgram import DeepgramClient
import os
import logging
import mimetypes
from typing import Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Deepgram with your API key
API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not API_KEY:
    raise ValueError("DEEPGRAM_API_KEY environment variable is not set")

# Supported audio file extensions
ALLOWED_EXTENSIONS = {
    '.mp3', '.mp4', '.wav', '.ogg', '.m4a', 
    '.flac', '.aac', '.wma', '.amr', '.aiff', 
    '.opus', '.webm'
}

def is_valid_audio_file(filename: str) -> bool:
    """
    Check if the file is a valid audio file based on extension
    """
    try:
        # Check file extension
        ext = os.path.splitext(filename)[1].lower()
        logger.debug(f"Validating file extension: {ext}")
        if ext not in ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file extension: {ext}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        return False

def transcribe_audio_file(file_path: str) -> Optional[str]:
    """
    Helper function that takes a file path and returns the transcription as string.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        String containing the transcription text or None if transcription failed
    """
    try:
        # Validate file extension
        if not is_valid_audio_file(file_path):
            logger.error(f"Invalid audio file format: {file_path}")
            return None
            
        # Get content type based on file extension
        content_type = mimetypes.guess_type(file_path)[0]
        if not content_type:
            # Default to audio/mpeg if we can't determine mime type
            content_type = 'audio/mpeg'
            
        logger.info(f"Processing audio file: {file_path}")
        
        # Process the audio file
        result = deepgram_speech_to_text(file_path, content_type)
        
        if result.get("transcript") == "failed":
            logger.error("Failed to transcribe audio")
            return None
            
        return result["transcript"]

    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        return None

def deepgram_speech_to_text(file_path: str, content_type: str) -> Dict[str, str]:
    """
    Process audio file using Deepgram
    """
    try:
        logger.debug(f"Initializing Deepgram client for file: {file_path}")
        # Initialize the Deepgram client
        deepgram = DeepgramClient(API_KEY)

        # Read the audio file
        logger.debug("Reading audio file")
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        logger.debug(f"Successfully read {len(audio_data)} bytes")

        # Prepare the request payload
        source = {
            'buffer': audio_data,
            'mimetype': content_type
        }

        # Set the options for the Whisper model
        options = {
            'model': 'whisper',
            'punctuate': True,
            'language': 'en',
            'summarize': 'v2'
        }

        logger.debug("Sending request to Deepgram")
        # Call the transcribe_file method
        response = deepgram.listen.prerecorded.v("1").transcribe_file(source, options, timeout=300)
        logger.debug("Received response from Deepgram")

        # Extract transcript, summary, and detected language
        results_dict = response.to_dict()
        transcript = results_dict.get('results', {}).get('channels', [{}])[0]\
            .get('alternatives', [{}])[0].get('transcript', '')
        
        summary = results_dict.get('results', {}).get('summary', {}).get('short', '')
        
        # Extract detected language
        detected_language = results_dict.get('results', {}).get('channels', [{}])[0]\
            .get('detected_language', 'unknown')
        
        logger.debug(f"Detected language: {detected_language}")

        return {
            "transcript": transcript,
            "summary": summary,
            "detected_language": detected_language
        }

    except Exception as e:
        logger.error(f"Error in speech to text: {str(e)}")
        logger.debug(f"Speech to text error: {str(e)}")
        return {"transcript": "failed"}