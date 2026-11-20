# ✦ Aura: Bespoke Multimodal Emotional Support Companion

An ethical, multimodal AI companion engineered for compassionate active listening, emotional grounding, and crisis-aware de-escalation. Built with a modern dark-mode interface powered by **Streamlit**, an asynchronous **FastAPI** gateway, persistent **MySQL** state storage, and **Google Gemini**.

---

## 🌟 Key Features

1. **Multimodal Inputs & Outputs**:
   - **Inputs**: Conversational text, expressive images/artwork/journal uploads (PNG/JPG), and spoken voice notes (WAV/MP3).
   - **Outputs**: Attuned emotional reflections, somatic grounding cues, and synthesized audio playback (TTS) for auditory grounding.
2. **Defined Safety & Guardrails Engine**:
   - **Acute Crisis Interception**: Instant detection of self-harm or suicidal intent with immediate de-escalation and verified helpline referrals (**988 Suicide & Crisis Lifeline**).
   - **Clinical Boundary Enforcement**: Empathetic refusal and redirection when users ask for formal psychiatric diagnoses or prescription dosages.
   - **Prompt Injection Defense**: Detection and neutralization of jailbreaks and instruction overrides.
   - **PII Scrubbing**: Automatic masking of sensitive personal details (emails, phone numbers, SSNs) prior to database persistence.
3. **Bespoke Obsidian Dark Mode Interface**:
   - Clean, modern dark palette (`#080B11` / `#0E131F`).
   - Eliminates standard generic AI elements; hidden deployment/toolbar chrome.
   - Quick grounding prompt chips (*Calming Breath*, *Overwhelm Relief*, *Bedtime Wind-Down*).
   - Inline audio player and custom media attachments tray.
4. **Data Persistence via MySQL**:
   - Tracks session lifecycle, multimodal message exchanges, and guardrail incident logs.
   - Includes automatic SQLite fallback if local MySQL is temporarily offline.

---

## 🏗️ Architecture & Tech Stack

```
Frontend (Streamlit Dark Mode)  <──HTTP/Multipart──>  FastAPI Gateway
                                                              │
                                            ┌─────────────────┴────────────────┐
                                            ▼                                  ▼
                                     Guardrail Engine                    Gemini Service
                                            │                                  │
                                     Safety Intercept                   Multimodal LLM
                                            │                                  │
                                            └─────────────────┬────────────────┘
                                                              ▼
                                                    MySQL DB & Audio TTS
```

- **Frontend**: Streamlit (Bespoke Dark Theme configured via `.streamlit/config.toml`)
- **Backend API**: FastAPI + Uvicorn
- **Database**: MySQL (SQLAlchemy ORM + PyMySQL)
- **LLM**: Google Gemini 1.5 / 2.0 (via `google-generativeai`)
- **Speech Synthesis (TTS)**: gTTS / Google Audio

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Credentials (`.env`)
```bash
copy .env.example .env
```
Ensure your Gemini API key and MySQL connection details are filled in:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/multimodal_chatbot
FALLBACK_TO_SQLITE=True
```

### 3. Initialize Database Schema
```bash
python scripts/init_db.py
```

### 4. Launch Application

You can launch both the FastAPI backend and Streamlit frontend together with a single command:
```bash
python run.py
```
- **Frontend UI**: `http://localhost:8501`
- **Backend API**: `http://localhost:8000`
- **Interactive API Docs (Swagger)**: `http://localhost:8000/docs`

*(Press `Ctrl+C` to gracefully terminate both services at once).*

#### Running Services Individually (Optional)
If you prefer running them in separate terminals:
```bash
# Terminal 1: Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
streamlit run frontend/app.py
```

---

## 🧪 Testing Guardrails
Run the guardrail unit test suite:
```bash
python -m unittest tests/test_guardrails.py
```
