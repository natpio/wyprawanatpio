import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
import requests
from PIL import Image, ImageFile

# Zabezpieczenie przed "uciętymi" plikami graficznymi
ImageFile.LOAD_TRUNCATED_IMAGES = True

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

def display_safe_image(filename_base, caption=""):
    """Bezpieczne ładowanie grafik z dysku/GitHuba"""
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    for ext in extensions:
        file_path = f"{filename_base}{ext}"
        if os.path.exists(file_path):
            try:
                img = Image.open(file_path)
                img.load()
                st.image(img, caption=caption, use_container_width=True)
                return
            except Exception:
                st.error(f"⚠️ Plik {file_path} jest uszkodzony.")
                return
    st.info(f"💡 Wgraj plik '{filename_base}.png' na GitHub.")

@st.cache_data(ttl=900)
def get_weather(lat, lon):
    """Pobiera aktualną pogodę z darmowego API"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=3).json()
        temp = round(res['current_weather']['temperature'])
        code = res['current_weather']['weathercode']
        
        if code == 0: emoji = "☀️"
        elif code in [1, 2, 3]: emoji = "⛅"
        elif code in [45, 48]: emoji = "🌫️"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: emoji = "🌧️"
        elif code in [71, 73, 75, 77, 85, 86]: emoji = "❄️"
        elif code in [95, 96, 99]: emoji = "⛈️"
        else: emoji = "🌡️"
        return f"{temp}°C {emoji}"
    except Exception:
        return "Brak danych 🌡️"

@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    return get_connection().read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl=0)

def init_state(sheet_name, bool_cols=[]):
    """Inicjalizuje lokalną pamięć aplikacji, aby działała błyskawicznie"""
    state_key = f"df_{sheet_name}"
    if state_key not in st.session_state:
        try:
            df = load_data(sheet_name)
            for col in bool_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip().str.upper().isin(["TRUE", "1", "YES", "T", "TAK"])
            st.session_state[state_key] = df
        except Exception as e:
            st.error(f"Błąd ładowania {sheet_name}: {e}")
            st.session_state[state_key] = pd.DataFrame()

def save_and_sync(sheet_name):
    """Wysyła zmienione dane do Google Sheets"""
    try:
        df = st.session_state[f"df_{sheet_name}"].copy()
        for col in df.select_dtypes(include=['bool']).columns:
            df[col] = df[col].map({True: "TRUE", False: "FALSE"})
        get_connection().update(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, data=df)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Błąd zapisu do GSheets: {e}")
