import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def is_truthy(val):
    # Ultra-odporne sprawdzanie: wszystko, co nie jest jawnym fałszem/pustką, staje się Prawdą.
    if pd.isna(val) or val is None: return False
    if isinstance(val, bool): return val
    
    s = str(val).strip().upper().replace("'", "").replace('"', "")
    if s in ["", "FALSE", "0", "NO", "NIE", "F", "FAŁSZ", "NAN", "NONE", "NULL"]:
        return False
        
    # Każda inna wartość (TRUE, PRAWDA, YES, 1, a nawet dziwne znaczki) to True
    return True

def load_data(sheet_name):
    # 1. Twarde wyczyszczenie pamięci podręcznej Streamlita przed pobraniem
    st.cache_data.clear()
    
    # 2. KRYTYCZNA ZMIANA: Usunięto argument spreadsheet=URL. 
    # Teraz biblioteka MUSI użyć konta usługi (z secrets.toml) i połączy się 
    # przez natywne API Google'a w czasie rzeczywistym, omijając opóźniony cache CSV!
    return get_connection().read(worksheet=sheet_name, ttl="0s")

def init_state(sheet_name):
    state_key = f"df_{sheet_name}"
    if state_key not in st.session_state:
        try:
            df = load_data(sheet_name)
            df = df.reset_index(drop=True)
            df = df.fillna("")
            
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
                # Konwersja na czyste booleany przed wysłaniem do chmury
                df_to_save[col] = df_to_save[col].apply(lambda x: bool(is_truthy(x)))
        
        df_to_save = df_to_save.fillna("")
        
        # Zapisujemy zmiany (również bierze główny adres URL z secrets)
        get_connection().update(worksheet=sheet_name, data=df_to_save)
        
        # Czyszczenie i toast
        st.cache_data.clear()
        st.toast(f"☁️ Zapisano {sheet_name} w chmurze!", icon="✅")
        
    except Exception as e:
        st.error(f"Błąd zapisu do chmury: {e}")

def toggle_status(sheet_name, index, col_name):
    """Odwraca status, wymusza przerysowanie listy i wysyła do Google Sheets"""
    df = st.session_state[f"df_{sheet_name}"]
    current_val = df.at[index, col_name]
    new_val = not is_truthy(current_val)
    
    df.at[index, col_name] = new_val
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
