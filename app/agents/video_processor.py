import os
import yt_dlp
import whisper
import ffmpeg
from typing import Dict, Any
from app.core.config import settings

# Initialize Whisper Model
# Using "base" model for speed/accuracy trade-off. Can be "tiny", "small", "medium", "large".
WHISPER_MODEL_SIZE = "base"
print(f"Loading Whisper model: {WHISPER_MODEL_SIZE}...")
try:
    whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
except Exception as e:
    print(f"Failed to load Whisper model: {e}")
    whisper_model = None

def download_audio(video_url: str, output_path: str = "temp_audio") -> str:
    """Downloads audio from a video URL using yt-dlp."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return f"{output_path}.mp3"
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def transcribe_audio(audio_path: str) -> str:
    """Transcribes audio file using Whisper."""
    if not whisper_model:
        return "Error: Whisper model not loaded."
        
    try:
        result = whisper_model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return f"Error transcribing: {e}"

def video_processor_node(state: Dict[str, Any]):
    print("---VIDEO PROCESSOR NODE---")
    text = state.get("text", "")
    
    # Check if text is a URL and looks like a video link
    # Simple check for now. Ideally, we'd have a separate input field or content_type
    if text.startswith("http") and ("youtube.com" in text or "youtu.be" in text):
        video_url = text.strip()
        print(f"Processing video URL: {video_url}")
        
        # Download
        audio_file = download_audio(video_url, output_path=f"temp_{state.get('article_id', 'manual')}")
        
        if audio_file and os.path.exists(audio_file):
            print(f"Audio downloaded to {audio_file}. Transcribing...")
            
            # Transcribe
            transcript = transcribe_audio(audio_file)
            print("Transcription complete.")
            
            # Cleanup
            try:
                os.remove(audio_file)
            except:
                pass
            
            # Update state with transcript
            # We append it to existing text or replace it?
            # Let's replace it as the "content" to be analyzed
            return {"text": f"Video Transcript from {video_url}:\n\n{transcript}"}
        else:
            return {"text": f"Failed to process video: {video_url}"}
            
    return {"text": text} # Pass through if not a video
