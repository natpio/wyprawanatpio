import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"

@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def is_truthy(val):
    if isinstance(val, bool): return val
    return str(val).strip().upper() in ["TRUE", "1", "YES", "TAK", "T"]

def load_data(sheet_name):
    # ttl=0 jest kluczowe, aby zawsze pytać Google o najnowsze dane
    return get_connection().read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl=0)

def init_state(sheet_name):
    state_key = f"df_{sheet_name}"
    if state_key not in st.session_state:
        try:
            df = load_data(sheet_name)
            # Konwersja kolumn statusowych na boolean dla poprawnej filtracji archiwum
            for col in ["Status", "Spakowane", "Zaliczone"]:
                if col in df.columns:
                    df[col] = df[col].apply(is_truthy)
            st.session_state[state_key] = df
        except Exception as e:
            st.error(f"Błąd ładowania danych: {e}")

def save_and_sync(sheet_name):
    """Zapisuje zmiany w Google Sheets i czyści cache"""
    try:
        df_to_save = st.session_state[f"df_{sheet_name}"].copy()
        # Konwersja na format tekstowy TRUE/FALSE widoczny na Twoim zrzucie ekranu
        for col in ["Status", "Spakowane", "Zaliczone"]:
            if col in df_to_save.columns:
                df_to_save[col] = df_to_save[col].map({True: "TRUE", False: "FALSE"})
        
        get_connection().update(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, data=df_to_save)
        # Czyścimy cache, aby następny odczyt po odświeżeniu był aktualny
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"KRYTYCZNY BŁĄD ZAPISU: {e}")
        return False

@st.cache_data(ttl=900)
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=3).json()
        temp = round(res['current_weather']['temperature'])
        return f"{temp}°C"
    except:
        return "--°C"
