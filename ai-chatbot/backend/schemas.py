from typing import Optional, List
from pydantic import BaseModel, Field

class CrisisAlert(BaseModel):
    is_crisis: bool = False
    crisis_type: Optional[str] = None
    helpline_info: Optional[str] = None
    recommended_action: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique guest session identifier")
    message: Optional[str] = Field(None, description="User's text input")
    enable_audio_output: bool = Field(True, description="Whether to synthesize voice audio response")

class ChatResponse(BaseModel):
    session_id: str
    response_text: str
    response_audio_url: Optional[str] = None
    emotional_tone: str = "supportive"
    crisis_alert: CrisisAlert = Field(default_factory=CrisisAlert)
    guardrail_status: str = "PASSED"

class MessageHistoryItem(BaseModel):
    id: int
    role: str
    content: str
    modality: str
    media_url: Optional[str] = None
    created_at: str

class HealthStatus(BaseModel):
    status: str
    database_backend: str
    gemini_configured: bool
    version: str
