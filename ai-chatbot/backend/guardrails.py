import re
import logging
from typing import Tuple, Optional, Dict, Any
from backend.config import settings

logger = logging.getLogger("chatbot.guardrails")

# 1. Critical Self-Harm & Crisis Regex Patterns
CRISIS_PATTERNS = [
    r"\b(kill|end)\s+(my\s*self|my\s*life)\b",
    r"\b(suicid(e|al|ing))\b",
    r"\bwant\s+to\s+die\b",
    r"\bdon'?t\s+want\s+to\s+live\b",
    r"\bhurt(ing)?\s+myself\b",
    r"\bcut(ting)?\s+my\s*wrists?\b",
    r"\boverdose\b",
    r"\bhang\s+myself\b",
    r"\bbetter\s+off\s+dead\b",
    r"\bno\s+reason\s+to\s+live\b"
]

# 2. Clinical Diagnosis & Prescription Patterns
CLINICAL_PATTERNS = [
    r"\b(diagnose\s+me\s+with|do\s+i\s+have)\s+(bipolar|schizophrenia|depression|adhd|ocd|autism|ptsd)\b",
    r"\bwhat\s+(?:dose|dosage|amount)\b.*?\bshould\s+i\s+take\b",
    r"\bwhat\s+medication\s+should\s+i\s+take\b",
    r"\b(prescribe|prescription)\b",
    r"\bcan\s+you\s+replace\s+my\s+therapist\b"
]

# 3. Prompt Injection & Jailbreak Patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions?",
    r"disregard\s+system\s+prompt",
    r"you\s+are\s+now\s+in\s+dan\s+mode",
    r"bypass\s+all\s+(rules|safety|guardrails)",
    r"reveal\s+(your|the)\s+system\s+prompt",
    r"output\s+your\s+instructions\s+verbatim"
]

# 4. PII Scrubbing Patterns
PII_EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PII_PHONE_PATTERN = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
PII_SSN_PATTERN = r"\b\d{3}-\d{2}-\d{4}\b"


class GuardrailEngine:
    @staticmethod
    def sanitize_pii(text: str) -> str:
        """Masks sensitive PII before persistence or logging."""
        if not text:
            return ""
        scrubbed = re.sub(PII_EMAIL_PATTERN, "[EMAIL_MASKED]", text)
        scrubbed = re.sub(PII_SSN_PATTERN, "[SSN_MASKED]", scrubbed)
        scrubbed = re.sub(PII_PHONE_PATTERN, "[PHONE_MASKED]", scrubbed)
        return scrubbed

    @staticmethod
    def check_crisis(text: str) -> Tuple[bool, Optional[str]]:
        """
        Detects acute emotional crisis or suicidal ideation.
        Returns: (is_crisis, response_message_if_triggered)
        """
        if not text:
            return False, None
        
        lowered = text.lower()
        for pattern in CRISIS_PATTERNS:
            if re.search(pattern, lowered):
                logger.warning(f"CRISIS GUARDRAIL TRIGGERED: Match pattern '{pattern}'")
                crisis_response = (
                    "I hear how much pain you are experiencing right now, and I want you to be safe. "
                    "Please know that you do not have to carry this alone.\n\n"
                    "Because I care about your safety and I am an AI companion without the ability to intervene in emergencies, "
                    "please connect immediately with compassionate people trained to help:\n\n"
                    f"- 📞 **Suicide & Crisis Lifeline**: Call or text **{settings.CRISIS_HOTLINE}** (Free, confidential, 24/7)\n"
                    f"- 💬 **Crisis Text Line**: **{settings.CRISIS_TEXT_LINE}**\n"
                    f"- 🌍 **International Emergencies**: Please contact your local emergency services (e.g., 911, 999, 112, 100) or visit the nearest emergency room.\n\n"
                    "I am holding space for you, but please reach out to one of these services right now."
                )
                return True, crisis_response

        return False, None

    @staticmethod
    def check_clinical_boundary(text: str) -> Tuple[bool, Optional[str]]:
        """
        Detects medical/clinical diagnostic requests and redirects.
        Returns: (is_clinical, response_message_if_triggered)
        """
        if not text:
            return False, None

        lowered = text.lower()
        for pattern in CLINICAL_PATTERNS:
            if re.search(pattern, lowered):
                logger.info(f"CLINICAL BOUNDARY GUARDRAIL TRIGGERED: Match pattern '{pattern}'")
                redirect_response = (
                    "I can hear that you're seeking clarity on your mental health symptoms, and it's completely understandable to want answers. "
                    "However, as an AI companion, I cannot formally diagnose conditions or recommend medical prescriptions.\n\n"
                    "I can support you by offering evidence-informed grounding exercises, emotional reflections, and healthy coping techniques. "
                    "For a proper diagnosis or medical evaluation, please speak with a licensed psychologist, psychiatrist, or primary care physician."
                )
                return True, redirect_response

        return False, None

    @staticmethod
    def check_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
        """
        Detects and neutralizes prompt injection / jailbreak attempts.
        Returns: (is_injection, sanitized_or_refusal_message)
        """
        if not text:
            return False, None

        lowered = text.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, lowered):
                logger.warning(f"PROMPT INJECTION GUARDRAIL TRIGGERED: Match pattern '{pattern}'")
                refusal = (
                    "I am committed to providing a safe, respectful, and supportive space. "
                    "I cannot modify my core safety guidelines or operational directives. "
                    "How can I support your wellbeing today?"
                )
                return True, refusal

        return False, None

    @classmethod
    def evaluate_input(cls, user_text: str) -> Dict[str, Any]:
        """
        Runs comprehensive guardrail evaluation pipeline on incoming text.
        """
        # 1. Crisis Check (Highest Priority)
        is_crisis, crisis_msg = cls.check_crisis(user_text)
        if is_crisis:
            return {
                "passed": False,
                "incident_type": "crisis_self_harm",
                "severity": "CRITICAL",
                "message": crisis_msg,
                "is_crisis": True
            }

        # 2. Injection Check
        is_injection, injection_msg = cls.check_prompt_injection(user_text)
        if is_injection:
            return {
                "passed": False,
                "incident_type": "prompt_injection",
                "severity": "HIGH",
                "message": injection_msg,
                "is_crisis": False
            }

        # 3. Clinical Boundary Check
        is_clinical, clinical_msg = cls.check_clinical_boundary(user_text)
        if is_clinical:
            return {
                "passed": False,
                "incident_type": "clinical_boundary",
                "severity": "MEDIUM",
                "message": clinical_msg,
                "is_crisis": False
            }

        return {
            "passed": True,
            "incident_type": None,
            "severity": None,
            "message": None,
            "is_crisis": False
        }
