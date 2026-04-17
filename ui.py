import streamlit as st
import base64
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

def apply_custom_css():
    css = """
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #f8f9fa; font-family: 'Open Sans', sans-serif; }
    .route-card { background: white; border-radius: 12px; padding: 15px; margin-bottom: 10px; border-left: 5px solid #C62828; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .route-tag { background: #FFC72C; color: #0B2447; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; }
    .clock-container { background: white; border-radius: 10px; padding: 10px; text-align: center; border-top: 4px solid #0B2447; }
    .clock-time { font-size: 1.8rem; font-weight: bold; color: #0B2447; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def display_safe_image(path, caption=""):
    try:
        img = Image.open(path)
        # Używamy width="stretch" dla zgodności z nowym Streamlitem
        st.image(img, caption=caption, width=None)
    except:
        st.info(f"Brak pliku: {path}")

def jetlag_clock(city, timezone, label):
    """Naprawiony zegar wykorzystujący standardowy HTML/JS"""
    import datetime
    import pytz
    now = datetime.datetime.now(pytz.timezone(timezone))
    st.markdown(f"""
        <div class="clock-container">
            <div style="font-size: 0.8rem; color: gray;">{city}</div>
            <div class="clock-time">{now.strftime('%H:%M')}</div>
            <div style="font-size: 0.6rem;">{label}</div>
        </div>
    """, unsafe_allow_html=True)

def render_boarding_pass(days):
    st.markdown(f"### ✈️ IOWA 2026 | Pozostało: {days} dni", unsafe_allow_html=True)

def render_customs_card(d):
    st.write("--- FORMULARZ CELNY (PODGLĄD) ---")
    st.json(d)
