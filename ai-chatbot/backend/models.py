import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    modality = Column(String(30), default="text")  # 'text', 'image', 'audio', 'multimodal'
    media_url = Column(String(255), nullable=True)  # path or URL for image/audio input or output
    emotional_tone = Column(String(50), nullable=True)  # detected or calibrated emotional tone
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class GuardrailIncident(Base):
    __tablename__ = "guardrail_incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), nullable=True, index=True)
    incident_type = Column(String(60), nullable=False)  # 'crisis_self_harm', 'clinical_boundary', 'prompt_injection'
    severity = Column(String(20), default="MEDIUM")  # 'CRITICAL', 'HIGH', 'MEDIUM'
    user_prompt_snippet = Column(Text, nullable=True)
    action_taken = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
