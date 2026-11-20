"""
Database Initialization Script.
Creates all required tables in MySQL (or configured fallback DB).
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import init_db, engine
from backend.config import settings

def main():
    print("=" * 60)
    print("Initializing Database Schema...")
    print(f"Target Database Engine: {engine.dialect.name}")
    print(f"Target URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print("=" * 60)

    try:
        init_db()
        print("✅ Database tables successfully created:")
        print("  - chat_sessions")
        print("  - chat_messages")
        print("  - guardrail_incidents")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
