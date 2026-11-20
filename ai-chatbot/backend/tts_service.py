import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from backend.config import settings

logger = logging.getLogger("chatbot.tts")

class TTSService:
    @staticmethod
    def generate_speech(text: str, filename_prefix: str = "aura_voice") -> Optional[str]:
        """
        Synthesizes empathetic speech audio from response text using gTTS.
        Returns the filename or relative URL path to the generated audio file.
        """
        if not text:
            return None
        
        # Strip markdown syntax for natural speech rendering
        clean_text = text.replace("**", "").replace("*", "").replace("#", "").replace("- ", "")
        # Limit speech synthesis to first 400 characters for conversational brevity
        if len(clean_text) > 400:
            clean_text = clean_text[:400] + "... I've shared the full details in the text below."

        audio_id = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.mp3"
        output_path = settings.AUDIO_OUTPUT_DIR / audio_id

        try:
            from gtts import gTTS
            tts = gTTS(text=clean_text, lang='en', tld='com', slow=False)
            tts.save(str(output_path))
            logger.info(f"Synthesized voice audio saved to {output_path}")
            return f"/audio/{audio_id}"
        except ImportError:
            logger.warning("gTTS package not installed. Skipping audio synthesis.")
            return None
        except Exception as e:
            logger.error(f"Error during audio synthesis: {e}")
            return None
