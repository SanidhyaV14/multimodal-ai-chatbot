import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
from PIL import Image
from dotenv import load_dotenv
from backend.config import settings

logger = logging.getLogger("chatbot.gemini")

AURA_SYSTEM_INSTRUCTION = """
You are Aura, an emotionally perceptive, warm, and grounded companion. Your purpose is to provide a calm, non-judgmental space for the user to reflect, untangle thoughts, and find emotional equilibrium.

CORE PRINCIPLES & VOICE:
1. Speak with genuine human empathy, gentle presence, and brevity. Avoid clinical jargon, robotic affirmations, or repetitive bullet-point lectures.
2. First validate what the person is feeling. Do not rush into fixing or lecturing. Often people need to be heard before they need a solution.
3. You have deep natural understanding of somatic grounding, nervous system regulation, and mindfulness (e.g., physiological sighs, box breathing, 5-4-3-2-1 sensory grounding, compassionate self-talk). Weave these organically when the user needs relief, rather than presenting them like a textbook manual.
4. When an image or voice note is shared:
   - Acknowledge its emotional essence softly (the quiet mood of a photo, the tension in a journal doodle, the exhaustion or brightness in a voice).
   - Meet them where they are in that moment.
5. Absolute Boundary: You are a caring companion, not a licensed psychiatrist or physician. Never diagnose clinical conditions or recommend pharmaceutical dosages. If asked, respond with warm honesty and guide them gently toward professional care.
"""

# Resilient model cascade: prioritized for active availability and fast conversational response
DEFAULT_MODEL_FALLBACKS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash"
]

def get_current_api_key() -> str:
    """Always re-checks environment and .env dynamically."""
    load_dotenv(settings.ROOT_DIR / ".env", override=True)
    key = os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY)
    if key:
        key = key.strip().strip("'\"")
    return key

class GeminiService:
    def __init__(self):
        pass

    def is_configured(self) -> bool:
        key = get_current_api_key()
        return bool(key and not key.startswith("your_"))

    def generate_multimodal_response(
        self,
        user_text: str,
        history: List[Dict[str, str]],
        image_path: Optional[Path] = None,
        audio_path: Optional[Path] = None
    ) -> str:
        """
        Orchestrates multimodal inputs (text, image, audio) and prompts Gemini.
        Uses the modern google.genai SDK with multi-model resiliency.
        """
        api_key = get_current_api_key()
        if not api_key or api_key.startswith("your_"):
            logger.warning("No valid GEMINI_API_KEY detected. Returning fallback response.")
            return self._fallback_empathetic_response(user_text, image_path, audio_path)

        # Build contents payload
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            contents = []

            # 1. Conversational history context
            if history:
                history_text = "Recent conversation:\n"
                for msg in history[-6:]:
                    history_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
                contents.append(history_text)

            # 2. Image attachment
            if image_path and image_path.exists():
                try:
                    img = Image.open(image_path)
                    contents.append(img)
                    contents.append("[User attached this image for reflection.]")
                except Exception as img_err:
                    logger.warning(f"Failed to process image: {img_err}")

            # 3. Audio voice note attachment
            if audio_path and audio_path.exists():
                try:
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                    mime_type = "audio/wav" if str(audio_path).endswith(".wav") else "audio/mp3"
                    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
                    contents.append(audio_part)
                    contents.append("[User provided this voice note.]")
                except Exception as aud_err:
                    logger.warning(f"Failed to process audio: {aud_err}")

            # 4. User prompt
            if user_text:
                contents.append(f"User: {user_text}")
            elif not image_path and not audio_path:
                contents.append("User: Hello Aura.")

            config = types.GenerateContentConfig(
                system_instruction=AURA_SYSTEM_INSTRUCTION,
                temperature=0.7
            )

            # Build prioritized list of models to try
            configured_model = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL).strip()
            models_to_try = [configured_model]
            for m in DEFAULT_MODEL_FALLBACKS:
                if m not in models_to_try:
                    models_to_try.append(m)

            last_error = None
            for model_name in models_to_try:
                try:
                    logger.info(f"Invoking Gemini model '{model_name}'...")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config
                    )
                    if response and response.text:
                        logger.info(f"Successfully generated response from model '{model_name}'.")
                        return response.text.strip()
                except Exception as model_err:
                    last_error = model_err
                    logger.warning(f"Model '{model_name}' failed ({type(model_err).__name__}: {str(model_err)[:120]}). Trying next candidate...")

            logger.error(f"All candidate Gemini models failed. Last error: {last_error}")
            return self._fallback_empathetic_response(user_text, image_path, audio_path)

        except Exception as e:
            logger.error(f"Error in multimodal generation pipeline: {e}", exc_info=True)
            return self._fallback_empathetic_response(user_text, image_path, audio_path)

    def _fallback_empathetic_response(
        self,
        user_text: str,
        image_path: Optional[Path],
        audio_path: Optional[Path]
    ) -> str:
        """
        Calm, natural companion response when running offline or without active Gemini quota.
        """
        media_note = ""
        if image_path:
            media_note = "I see the visual you shared—thank you for trusting me with that. "
        elif audio_path:
            media_note = "I've heard your voice note and the feeling behind it. "

        lowered = (user_text or "").lower()
        if any(w in lowered for w in ["anxious", "anxiety", "panic", "overwhelm", "stressed"]):
            return (
                f"{media_note}It sounds like your nervous system is carrying a heavy load right now. "
                "You don't have to figure everything out in this single moment.\n\n"
                "If it feels okay, try dropping your shoulders away from your ears and letting out a long, slow sigh. "
                "I'm here with you. Would you like to just talk it through, or would a gentle breathing exercise help ground you?"
            )
        elif any(w in lowered for w in ["sleep", "tired", "insomnia", "bed"]):
            return (
                f"{media_note}Late-night thoughts can feel much louder than they really are. "
                "Give yourself permission to set today down—whatever is unfinished can safely wait until tomorrow.\n\n"
                "Unclench your jaw, soften your eyelids, and let your body sink into wherever you're resting. What's on your mind right now?"
            )
        elif any(w in lowered for w in ["breath", "breathing"]):
            return (
                "Let's take a slow breath together.\n\n"
                "• Inhale gently through your nose for 4 seconds...\n"
                "• Pause softly at the top for 4 seconds...\n"
                "• Release slowly through your mouth for 6 seconds...\n\n"
                "Notice the brief stillness as you let that breath go. How does your body feel right now?"
            )
        else:
            return (
                f"{media_note}I hear you, and whatever is present for you right now is completely okay. "
                "Take all the time you need. What feels most important to talk about or release today?"
            )

gemini_service = GeminiService()
