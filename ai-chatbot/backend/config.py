import os
from pathlib import Path

# Load .env file from project root if python-dotenv is available
ROOT_DIR = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

class Settings:
    PROJECT_NAME: str = "Multimodal Emotional Support Chatbot"
    VERSION: str = "1.0.0"
    ROOT_DIR: Path = ROOT_DIR

    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")

    # MySQL Database Configuration
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "multimodal_chatbot")
    
    # Primary MySQL connection string
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Fallback to SQLite if MySQL is unavailable
    FALLBACK_TO_SQLITE: bool = os.getenv("FALLBACK_TO_SQLITE", "True").lower() in ("true", "1", "t")
    SQLITE_URL: str = os.getenv("SQLITE_URL", f"sqlite:///{ROOT_DIR}/chatbot_fallback.db")

    # Server Configuration
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", 8000))
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")

    # Storage Paths
    UPLOAD_DIR: Path = ROOT_DIR / "uploads"
    AUDIO_OUTPUT_DIR: Path = ROOT_DIR / "generated_audio"

    # Crisis & Guardrail Emergency Contacts
    CRISIS_HOTLINE: str = os.getenv("CRISIS_HOTLINE_PRIMARY", "988 (Suicide & Crisis Lifeline - Call or Text 24/7)")
    CRISIS_TEXT_LINE: str = os.getenv("CRISIS_TEXT_LINE", "Text HOME to 741741")
    EMERGENCY_DISCLAIMER: str = (
        "I am an AI companion and cannot provide clinical diagnosis, medical advice, "
        "or emergency interventions. If you are in immediate danger or distress, please reach out to professional services."
    )

settings = Settings()

# Ensure runtime directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
