"""
Voice Module
Handles Text-to-Speech (TTS) for AI questions and Speech-to-Text (STT)
for candidate responses using OpenAI Whisper API + gTTS fallback.

For full local STT: pip install openai-whisper pyaudio sounddevice
For TTS: pip install gtts pygame
"""

import os
import io
import json
import tempfile
import base64
from typing import Optional, Tuple
from openai import OpenAI


class VoiceModule:
    """
    Manages audio I/O for the voice interview feature.

    TTS  → OpenAI TTS API (tts-1 model, alloy voice)
    STT  → OpenAI Whisper API (transcription endpoint)
    """

    TTS_VOICE    = "alloy"       # Options: alloy, echo, fable, onyx, nova, shimmer
    TTS_MODEL    = "tts-1"
    WHISPER_MODEL = "whisper-1"

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history: list[dict] = []

    # ─── Text-to-Speech ───────────────────────────────────────────

    def text_to_speech(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using OpenAI TTS API.

        Args:
            text: Text to synthesise

        Returns:
            MP3 audio bytes, or None on failure
        """
        try:
            response = self.client.audio.speech.create(
                model=self.TTS_MODEL,
                voice=self.TTS_VOICE,
                input=text[:4096],          # API limit
            )
            return response.content
        except Exception as e:
            print(f"TTS error: {e}")
            return None

    def text_to_speech_b64(self, text: str) -> Optional[str]:
        """Return TTS audio as a base-64 string (for embedding in HTML)."""
        audio_bytes = self.text_to_speech(text)
        if audio_bytes:
            return base64.b64encode(audio_bytes).decode("utf-8")
        return None

    # ─── Speech-to-Text ───────────────────────────────────────────

    def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """
        Transcribe audio bytes using OpenAI Whisper API.

        Args:
            audio_bytes: Raw audio bytes (wav/mp3/m4a/webm…)
            filename:    Hint for format detection

        Returns:
            Transcribed text string
        """
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = filename
            transcript = self.client.audio.transcriptions.create(
                model=self.WHISPER_MODEL,
                file=audio_file,
                response_format="text",
            )
            return transcript.strip() if isinstance(transcript, str) else transcript
        except Exception as e:
            return f"[Transcription failed: {e}]"

    def transcribe_audio_file(self, filepath: str) -> str:
        """Transcribe an audio file on disk."""
        try:
            with open(filepath, "rb") as f:
                return self.transcribe_audio_bytes(f.read(), os.path.basename(filepath))
        except Exception as e:
            return f"[File transcription failed: {e}]"

    # ─── Conversation history ──────────────────────────────────────

    def add_to_history(self, role: str, content: str, audio_bytes: Optional[bytes] = None):
        """Append an entry to the voice-interview conversation log."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "has_audio": audio_bytes is not None,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        })

    def get_history(self) -> list[dict]:
        return self.conversation_history

    def reset(self):
        self.conversation_history = []

    # ─── HTML audio player helper ──────────────────────────────────

    @staticmethod
    def audio_autoplay_html(audio_b64: str) -> str:
        """Return an HTML snippet that auto-plays base-64 MP3 audio."""
        return (
            f'<audio autoplay controls style="width:100%;margin-top:0.5rem;">'
            f'<source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg">'
            f"</audio>"
        )
