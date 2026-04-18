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
    # Agresywne usuwanie śmieci z Google Sheets (np. ukryty apostrof 'TRUE)
    s = str(val).strip().upper().replace("'", "").replace('"', "")
    return s in ["TRUE", "1", "YES", "TAK", "T"]

def load_data(sheet_name):
    # ttl="0s" to najbezpieczniejszy zapis w nowym Streamlit zmuszający do pobrania świeżych danych
    return get_connection().read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl="0s")

def init_state(sheet_name):
    state_key = f"df_{sheet_name}"
    if state_key not in st.session_state:
        try:
            df = load_data(sheet_name)
            # Resetujemy index, by upewnić się, że po dodaniu zadania numery rzędów się nie rozjadą
            df = df.reset_index(drop=True)
            for col in ["Status", "Spakowane", "Zaliczone"]:
                if col in df.columns:
                    df[col] = df[col].apply(is_truthy)
            st.session_state[state_key] = df
        except Exception as e:
            st.error(f"Błąd bazy: {e}")

def save_and_sync(sheet_name):
    try:
        df_to_save = st.session_state[f"df_{sheet_name}"].copy()
        
        for col in ["Status", "Spakowane", "Zaliczone"]:
            if col in df_to_save.columns:
                # Zapisujemy twarde booleany lub idealnie puste stringi (żeby uniknąć NaN w chmurze)
                df_to_save[col] = df_to_save[col].apply(
                    lambda x: bool(is_truthy(x)) if str(x).strip() != "" and pd.notna(x) else ""
                )
        
        df_to_save = df_to_save.fillna("")
        
        # Wysłanie do Google Sheets
        get_connection().update(worksheet=sheet_name, data=df_to_save)
        
        # Twarde wyczyszczenie pamięci podręcznej i potwierdzenie
        st.cache_data.clear()
        st.toast(f"☁️ Zapisano {sheet_name} w chmurze!", icon="✅")
        
    except Exception as e:
        st.error(f"Błąd zapisu do chmury: {e}")

def toggle_status(sheet_name, index, col_name):
    """Odwraca status zadania, wymusza reaktywność UI i natychmiast zapisuje do bazy"""
    df = st.session_state[f"df_{sheet_name}"]
    current_val = df.at[index, col_name]
    new_val = not is_truthy(current_val)
    
    # Krok 1: Zmiana w komórce
    df.at[index, col_name] = new_val
    
    # Krok 2: WYMUSZENIE REAKTYWNOŚCI
    # Przypisujemy df.copy(), aby Streamlit zauważył nowy obiekt i od razu przebudował widok zadań!
    st.session_state[f"df_{sheet_name}"] = df.copy()
    
    if sheet_name == "Grywalizacja" and new_val:
        st.session_state["show_balloons"] = True
        
    save_and_sync(sheet_name)

@st.cache_data(ttl=900)
def get_weather(lat, lon):
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
    except:
        return "--°C"
