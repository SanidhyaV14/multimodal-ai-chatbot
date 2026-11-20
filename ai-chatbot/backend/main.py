import shutil
import uuid
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db, init_db, engine
from backend.models import ChatSession, ChatMessage, GuardrailIncident
from backend.schemas import ChatResponse, CrisisAlert, HealthStatus, MessageHistoryItem
from backend.guardrails import GuardrailEngine
from backend.gemini_service import gemini_service
from backend.tts_service import TTSService

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multimodal Emotional Support Chatbot API with Active Guardrails and Voice Synthesis"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount audio & uploads static directories
app.mount("/audio", StaticFiles(directory=str(settings.AUDIO_OUTPUT_DIR)), name="audio")
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")


@app.on_event("startup")
def on_startup():
    """Initializes database tables on application start."""
    init_db()


@app.get("/", tags=["Health"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online"
    }


@app.get("/api/health", response_model=HealthStatus, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    db_name = engine.dialect.name
    gemini_ready = gemini_service.is_configured()
    return HealthStatus(
        status="healthy",
        database_backend=db_name,
        gemini_configured=gemini_ready,
        version=settings.VERSION
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(
    session_id: str = Form(...),
    message: Optional[str] = Form(None),
    enable_audio_output: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Main multimodal conversational endpoint.
    Processes text, image, and voice notes with safety guardrails and audio response.
    """
    user_text = (message or "").strip()

    # 1. Ensure ChatSession exists
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        session = ChatSession(session_id=session_id)
        db.add(session)
        db.commit()

    # 2. Save incoming media files if present
    saved_image_path = None
    saved_audio_path = None
    input_modality = "text"

    if image and image.filename:
        input_modality = "multimodal"
        ext = Path(image.filename).suffix or ".png"
        img_filename = f"img_{uuid.uuid4().hex[:8]}{ext}"
        saved_image_path = settings.UPLOAD_DIR / img_filename
        with open(saved_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    if audio and audio.filename:
        input_modality = "multimodal"
        ext = Path(audio.filename).suffix or ".wav"
        aud_filename = f"aud_{uuid.uuid4().hex[:8]}{ext}"
        saved_audio_path = settings.UPLOAD_DIR / aud_filename
        with open(saved_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

    # 3. Guardrail Evaluation
    guardrail_result = GuardrailEngine.evaluate_input(user_text)

    # Log user message with PII masked
    sanitized_user_text = GuardrailEngine.sanitize_pii(user_text)
    user_media_ref = str(saved_image_path or saved_audio_path or "")
    user_msg_record = ChatMessage(
        session_id=session_id,
        role="user",
        content=sanitized_user_text or "[Multimodal Input]",
        modality=input_modality,
        media_url=user_media_ref if user_media_ref else None
    )
    db.add(user_msg_record)
    db.commit()

    # If Guardrail Flagged (Crisis, Injection, Boundary)
    if not guardrail_result["passed"]:
        incident = GuardrailIncident(
            session_id=session_id,
            incident_type=guardrail_result["incident_type"],
            severity=guardrail_result["severity"],
            user_prompt_snippet=sanitized_user_text[:300],
            action_taken="Intercepted and replaced with safety protocol"
        )
        db.add(incident)

        bot_response_text = guardrail_result["message"]
        
        audio_url = None
        if enable_audio_output:
            audio_url = TTSService.generate_speech(bot_response_text, filename_prefix="guardrail_voice")

        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=bot_response_text,
            modality="text",
            media_url=audio_url
        )
        db.add(assistant_msg)
        db.commit()

        crisis_alert = CrisisAlert(
            is_crisis=guardrail_result["is_crisis"],
            crisis_type=guardrail_result["incident_type"],
            helpline_info=settings.CRISIS_HOTLINE if guardrail_result["is_crisis"] else None,
            recommended_action="Immediate connection to crisis services" if guardrail_result["is_crisis"] else None
        )

        return ChatResponse(
            session_id=session_id,
            response_text=bot_response_text,
            response_audio_url=audio_url,
            emotional_tone="supportive_deescalation",
            crisis_alert=crisis_alert,
            guardrail_status=guardrail_result["incident_type"].upper()
        )

    # 4. Fetch recent chat history
    history_records = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(6)
        .all()
    )
    history = [{"role": msg.role, "content": msg.content} for msg in reversed(history_records)]

    # 5. Direct Multimodal Gemini Generation
    bot_response_text = gemini_service.generate_multimodal_response(
        user_text=user_text,
        history=history,
        image_path=saved_image_path,
        audio_path=saved_audio_path
    )

    # 6. Speech Audio Synthesis (Multimodal Output)
    audio_url = None
    if enable_audio_output:
        audio_url = TTSService.generate_speech(bot_response_text, filename_prefix="aura_voice")

    # 7. Persist Assistant Response in DB
    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=bot_response_text,
        modality="multimodal" if audio_url else "text",
        media_url=audio_url,
        emotional_tone="empathetic"
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        session_id=session_id,
        response_text=bot_response_text,
        response_audio_url=audio_url,
        emotional_tone="empathetic",
        crisis_alert=CrisisAlert(is_crisis=False),
        guardrail_status="PASSED"
    )


@app.get("/api/history/{session_id}", response_model=List[MessageHistoryItem], tags=["History"])
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """Retrieves chronological chat history for a session."""
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        MessageHistoryItem(
            id=m.id,
            role=m.role,
            content=m.content,
            modality=m.modality,
            media_url=m.media_url,
            created_at=m.created_at.isoformat()
        )
        for m in messages
    ]
