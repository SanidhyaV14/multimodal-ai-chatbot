import uuid
import requests
import streamlit as st

# ------------------------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Aura — Emotional Companion",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000"

# ------------------------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "enable_audio" not in st.session_state:
    st.session_state["enable_audio"] = True
if "pending_prompt" not in st.session_state:
    st.session_state["pending_prompt"] = None

# ------------------------------------------------------------------------------
# Bespoke Dark Mode CSS (Removes Deploy button, slop styling & elevates aesthetics)
# ------------------------------------------------------------------------------
st.markdown("""
<style>
    /* 1. HIDE STREAMLIT DEPLOY BUTTON & TOOLBAR */
    [data-testid="stDeployButton"], 
    .stDeployButton, 
    [data-testid="stToolbarActions"], 
    header[data-testid="stHeader"] .stDeployButton,
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. ROOT THEME & SMOOTH SCROLLING */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #080B11 !important;
        color: #E2E8F0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    }

    /* 3. SIDEBAR ELEVATION */
    [data-testid="stSidebar"] {
        background-color: #0E131F !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 1.2rem 0;
    }

    /* 4. CHAT CONTAINER & BUBBLES */
    .stChatMessage {
        background-color: transparent !important;
        padding: 0.8rem 0rem !important;
    }
    
    /* User Message Styling */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #1E1B4B 0%, #2E285F 100%) !important;
        border: 1px solid rgba(129, 140, 248, 0.25) !important;
        border-radius: 16px 16px 4px 16px !important;
        padding: 1rem 1.25rem !important;
        margin: 0.6rem 0 0.6rem auto !important;
        max-width: 82% !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }
    
    /* Assistant Message Styling */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #111827 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px 16px 16px 4px !important;
        padding: 1rem 1.25rem !important;
        margin: 0.6rem 0 !important;
        max-width: 90% !important;
        box-shadow: 0 4px 24px -2px rgba(0, 0, 0, 0.35);
    }

    /* 5. HERO HEADER & BADGES */
    .aura-hero {
        padding: 1.5rem 0 1.2rem 0;
        margin-bottom: 0.8rem;
    }
    .aura-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 30%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .aura-subtitle {
        color: #94A3B8;
        font-size: 0.98rem;
        font-weight: 400;
        line-height: 1.5;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #34D399;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-bottom: 0.8rem;
    }
    .status-pulse {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
    }

    /* 6. SAFETY BANNER */
    .safety-disclaimer {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 3px solid #6366F1;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.82rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }

    /* 7. CRISIS EMERGENCY CARD */
    .crisis-card-dark {
        background: linear-gradient(135deg, #2A1215 0%, #1A0C0E 100%);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-left: 4px solid #EF4444;
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(239, 68, 68, 0.15);
    }
    .crisis-card-dark h4 {
        color: #FCA5A5;
        font-size: 1.05rem;
        margin-bottom: 0.4rem;
    }
    .crisis-card-dark p {
        color: #E2E8F0;
        font-size: 0.92rem;
        line-height: 1.6;
        margin-bottom: 0.6rem;
    }
    .crisis-pill-hotline {
        display: inline-block;
        background: rgba(239, 68, 68, 0.2);
        color: #FECACA;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* 8. BUTTONS & CONTROLS */
    div.stButton > button {
        background: #1E293B !important;
        color: #F1F5F9 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.stButton > button:hover {
        background: #2D3748 !important;
        border-color: #818CF8 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }

    /* 9. INPUT & CHATBAR POLISH */
    [data-testid="stChatInput"] {
        background-color: #0E131F !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* 10. AUDIO PLAYER POLISH */
    audio {
        width: 100% !important;
        height: 38px !important;
        border-radius: 8px !important;
        margin-top: 8px !important;
        filter: invert(0.9) hue-rotate(180deg);
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Sidebar Navigation & Settings
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="padding-top: 0.5rem; margin-bottom: 0.8rem;">
            <span style="font-size: 1.4rem; font-weight: 700; color: #FFFFFF;">✦ Aura</span>
            <div style="color: #64748B; font-size: 0.82rem; margin-top: 2px;">Emotional Support Companion</div>
        </div>
    """, unsafe_allow_html=True)

    # Health Check Indicator
    try:
        health_resp = requests.get(f"{API_BASE_URL}/api/health", timeout=1.5)
        if health_resp.status_code == 200:
            h_data = health_resp.json()
            db_label = h_data.get("database_backend", "DB").upper()
            gemini_online = h_data.get("gemini_configured", False)
            if gemini_online:
                st.markdown(f"""
                    <div class="status-pill">
                        <div class="status-pulse"></div>
                        Gemini & {db_label} Active
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background: rgba(234, 179, 8, 0.12); border: 1px solid rgba(234, 179, 8, 0.3); color: #FACC15; padding: 4px 10px; border-radius: 9999px; font-size: 0.76rem; font-weight: 500; display: inline-flex; align-items: center; gap: 5px; margin-bottom: 0.8rem;">
                        <span style="color:#EAB308;">●</span> Offline Fallback (Key Not Found)
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("⚠️ System initializing...")
    except Exception:
        st.markdown("""
            <div style="color: #F87171; font-size: 0.8rem; margin-bottom: 0.8rem;">
                ● Backend offline (Run: <code>python run.py</code>)
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("<p style='font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B;'>Session Controls</p>", unsafe_allow_html=True)
    
    col_reset, col_space = st.columns([1, 0.01])
    with col_reset:
        if st.button("✦ Start Fresh Conversation", use_container_width=True):
            st.session_state["session_id"] = str(uuid.uuid4())
            st.session_state["messages"] = []
            st.session_state["pending_prompt"] = None
            st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.session_state["enable_audio"] = st.toggle("Voice Audio Playback", value=st.session_state["enable_audio"])

    st.divider()

    # Emergency Support Card in Sidebar
    st.markdown("""
        <p style='font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B;'>Crisis Support Resources</p>
        <div style='background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 12px; font-size: 0.82rem; color: #CBD5E1;'>
            <div style='margin-bottom: 8px;'><strong>📞 Lifeline (US/CA):</strong> <span style='color: #FCA5A5;'>Call or text 988</span></div>
            <div style='margin-bottom: 8px;'><strong>💬 Crisis Text Line:</strong> Text <code>HOME</code> to 741741</div>
            <div><strong>🌍 UK / EU / IN:</strong> 999 / 112 / 100</div>
        </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Main Stage: Header & Aesthetic Disclaimer
# ------------------------------------------------------------------------------
st.markdown("""
<div class="aura-hero">
    <div class="aura-title">Aura</div>
    <div class="aura-subtitle">A calm, compassionate space to reflect, decompress, and untangle your feelings.</div>
</div>
<div class="safety-disclaimer">
    ✦ <strong>Gentle Reminder:</strong> Aura is a conversational support companion, not a licensed therapist or physician. 
    It cannot provide medical diagnosis or psychiatric treatment. If you are experiencing an emergency, please connect with <strong>988</strong> or your local emergency team.
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Quick Grounding Starter Prompts (Fluid UX)
# ------------------------------------------------------------------------------
if len(st.session_state["messages"]) == 0:
    st.markdown("<p style='font-size: 0.85rem; color: #64748B; margin-bottom: 0.6rem;'>Take a breath. You can start with one of these or speak freely below:</p>", unsafe_allow_html=True)
    chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
    with chip_col1:
        if st.button("🌿 Calming Breath", use_container_width=True):
            st.session_state["pending_prompt"] = "Could you guide me through a slow, calming breathing exercise?"
            st.rerun()
    with chip_col2:
        if st.button("🌊 Feeling Overwhelmed", use_container_width=True):
            st.session_state["pending_prompt"] = "I am feeling really overwhelmed with everything right now."
            st.rerun()
    with chip_col3:
        if st.button("💭 Untangle Thoughts", use_container_width=True):
            st.session_state["pending_prompt"] = "My mind is racing and I need help sorting through my thoughts."
            st.rerun()
    with chip_col4:
        if st.button("🌙 Bedtime Wind-Down", use_container_width=True):
            st.session_state["pending_prompt"] = "I can't seem to unwind tonight. Can you help me relax for sleep?"
            st.rerun()
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Render Conversation History
# ------------------------------------------------------------------------------
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        if msg.get("image_preview"):
            st.image(msg["image_preview"], width=260)
        
        st.markdown(msg["content"])

        # High-clarity crisis emergency card if triggered
        if msg.get("crisis_alert") and msg["crisis_alert"].get("is_crisis"):
            helpline = msg["crisis_alert"].get("helpline_info", "988")
            st.markdown(f"""
            <div class="crisis-card-dark">
                <h4>Compassionate Help is Available Right Now</h4>
                <p>I care deeply about your wellbeing, and you don't have to carry this alone. Please reach out to counselors trained to support you through this exact moment:</p>
                <div class="crisis-pill-hotline">📞 Call or Text {helpline} (Free & Confidential 24/7)</div>
            </div>
            """, unsafe_allow_html=True)

        # Embedded voice audio playback
        if msg.get("audio_url"):
            full_audio_url = f"{API_BASE_URL}{msg['audio_url']}"
            st.audio(full_audio_url)


# ------------------------------------------------------------------------------
# Multimodal Attachment Tray (Clean Drawer)
# ------------------------------------------------------------------------------
with st.expander("📎 Share an Image or Voice Note", expanded=False):
    col_img, col_aud = st.columns(2)
    with col_img:
        attached_image = st.file_uploader(
            "Share an expressive photo, artwork, or journal page",
            type=["png", "jpg", "jpeg"],
            key="drawer_image_uploader"
        )
        if attached_image:
            st.image(attached_image, width=160, caption="Attached image")
    with col_aud:
        attached_audio = st.file_uploader(
            "Upload a spoken voice note",
            type=["wav", "mp3", "m4a"],
            key="drawer_audio_uploader"
        )
        if attached_audio:
            st.audio(attached_audio)


# ------------------------------------------------------------------------------
# Chat Input & Reactive Execution
# ------------------------------------------------------------------------------
prompt_input = st.chat_input("What is on your mind? Take your time...")

# Check if prompt came from quick starter chip or chat input
active_prompt = None
if st.session_state["pending_prompt"]:
    active_prompt = st.session_state["pending_prompt"]
    st.session_state["pending_prompt"] = None
elif prompt_input:
    active_prompt = prompt_input

if active_prompt or attached_image or attached_audio:
    user_display_text = active_prompt or "Shared an attachment for reflection."

    # Record user message locally
    user_entry = {
        "role": "user",
        "content": user_display_text,
        "image_preview": attached_image if attached_image else None
    }
    st.session_state["messages"].append(user_entry)

    with st.chat_message("user"):
        if attached_image:
            st.image(attached_image, width=260)
        st.markdown(user_display_text)

    # Invoke FastAPI Backend
    with st.chat_message("assistant"):
        with st.spinner("Aura is listening..."):
            try:
                form_data = {
                    "session_id": st.session_state["session_id"],
                    "message": active_prompt or "",
                    "enable_audio_output": str(st.session_state["enable_audio"]).lower()
                }
                files_payload = {}
                if attached_image:
                    files_payload["image"] = (attached_image.name, attached_image.getvalue(), attached_image.type)
                if attached_audio:
                    files_payload["audio"] = (attached_audio.name, attached_audio.getvalue(), attached_audio.type)

                resp = requests.post(
                    f"{API_BASE_URL}/api/chat",
                    data=form_data,
                    files=files_payload if files_payload else None,
                    timeout=90
                )

                if resp.status_code == 200:
                    data = resp.json()
                    bot_text = data.get("response_text", "")
                    audio_url = data.get("response_audio_url")
                    crisis_alert = data.get("crisis_alert", {})

                    st.markdown(bot_text)

                    if crisis_alert.get("is_crisis"):
                        helpline = crisis_alert.get("helpline_info", "988")
                        st.markdown(f"""
                        <div class="crisis-card-dark">
                            <h4>Compassionate Help is Available Right Now</h4>
                            <p>I care deeply about your wellbeing, and you don't have to carry this alone. Please reach out to counselors trained to support you through this exact moment:</p>
                            <div class="crisis-pill-hotline">📞 Call or Text {helpline} (Free & Confidential 24/7)</div>
                        </div>
                        """, unsafe_allow_html=True)

                    if audio_url:
                        st.audio(f"{API_BASE_URL}{audio_url}")

                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": bot_text,
                        "audio_url": audio_url,
                        "crisis_alert": crisis_alert
                    })
                else:
                    st.error(f"Response error ({resp.status_code}): {resp.text}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend server. Please ensure FastAPI is running via `uvicorn backend.main:app`.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
