import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"

@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def is_truthy(val):
    """Konwertuje wartości z Excela (tekst TRUE/FALSE lub puste) na czysty typ Boolean."""
    if isinstance(val, bool): return val
    return str(val).strip().upper() in ["TRUE", "1", "YES", "TAK", "T"]

def load_data(sheet_name):
    """Pobiera dane bezpośrednio z Google Sheets omijając pamięć podręczną chmury (ttl=0)."""
    return get_connection().read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl=0)

def init_state(sheet_name):
    """Inicjalizuje dane w pamięci telefonu podczas pierwszego uruchomienia."""
    state_key = f"df_{sheet_name}"
    if state_key not in st.session_state:
        try:
            df = load_data(sheet_name)
            # Konwersja kolumn statusowych
            for col in ["Status", "Spakowane", "Zaliczone"]:
                if col in df.columns:
                    df[col] = df[col].apply(is_truthy)
            st.session_state[state_key] = df
        except Exception as e:
            st.error(f"Błąd ładowania danych {sheet_name}: {e}")

def save_and_sync(sheet_name):
    """Pancerny zapis do chmury: usuwa puste wiersze i formatuje Prawdę/Fałsz."""
    try:
        df_to_save = st.session_state[f"df_{sheet_name}"].copy()
        
        # TO JEST BARDZO WAŻNE: Czyszczenie danych przed wysyłką do Google!
        # Usuwa puste wiersze, które mogłyby zablokować zapis w arkuszu.
        df_to_save = df_to_save.dropna(how='all').fillna("")
        
        for col in ["Status", "Spakowane", "Zaliczone"]:
            if col in df_to_save.columns:
                df_to_save[col] = df_to_save[col].map({True: "TRUE", False: "FALSE"})
        
        # Wysłanie do arkusza Google
        get_connection().update(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, data=df_to_save)
        
        # Wyczyszczenie pamięci podręcznej, aby F5 pobrało zaktualizowane dane z chmury
        st.cache_data.clear() 
        return True
        
    except Exception as e:
        st.error(f"KRYTYCZNY BŁĄD ZAPISU DO CHMURY: {e}")
        st.stop()

def toggle_status_callback(sheet_name, index, col_name):
    """Magiczny przycisk! Zmienia status w ułamku sekundy i natychmiast wyzwala zapis."""
    current_val = st.session_state[f"df_{sheet_name}"].at[index, col_name]
    st.session_state[f"df_{sheet_name}"].at[index, col_name] = not current_val
    
    # Jeśli dziecko właśnie wykonało misję w Kids Hub, przygotuj balony
    if sheet_name == "Grywalizacja" and not current_val: 
        st.session_state["show_balloons"] = True
        
    save_and_sync(sheet_name)

@st.cache_data(ttl=900)
def get_weather(lat, lon):
    """Pobiera i odświeża pogodę (max co 15 minut, żeby oszczędzać zasoby)"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=3).json()
        temp = round(res['current_weather']['temperature'])
        return f"{temp}°C"
    except:
        return "--°C"
