import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os
from PIL import Image, ImageFile

# Zabezpieczenie przed "uciętymi" plikami graficznymi (częsty problem przy uploadzie na GitHub)
ImageFile.LOAD_TRUNCATED_IMAGES = True

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="IOWA '26 | OPERATION HUB 🇺🇸",
    page_icon="✈️",
    layout="wide"
    # Usunięto boczny pasek całkowicie
)

# --- FUNKCJA POMOCNICZA: BEZPIECZNE ŁADOWANIE OBRAZÓW ---
def display_safe_image(filename_base, caption=""):
    """
    Funkcja szuka pliku graficznego (png/jpg), bezpiecznie go ładuje
    i zapobiega wywaleniu aplikacji, jeśli plik jest uszkodzony.
    """
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    for ext in extensions:
        file_path = f"{filename_base}{ext}"
        if os.path.exists(file_path):
            try:
                img = Image.open(file_path)
                img.load() # Wymusza wczytanie danych, by sprawdzić błędy struktury
                st.image(img, caption=caption, use_container_width=True)
                return
            except Exception as e:
                st.error(f"⚠️ Plik {file_path} jest uszkodzony. Wgraj go ponownie na GitHuba.")
                return
    
    # Jeśli pętla się zakończy i nie znajdzie pliku:
    st.info(f"💡 [Brak grafiki] Wgraj plik '{filename_base}.png' lub '.jpg' do repozytorium, aby go tutaj wyświetlić.")

# --- 2. ZAAWANSOWANY CSS (MOTYW BOARDING PASS + USA-MAX) ---
st.markdown("""
    <style>
    /* Całkowite ukrycie technicznego UI Streamlita */
    header[data-testid="stHeader"] { visibility: hidden; }
    div[data-testid="stHeader"] { visibility: hidden; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; } /* Upewniamy się, że sidebar nie istnieje */

    /* Czcionki: Anton (nagłówki), Open Sans (tekst), Libre Barcode (kod kreskowy) */
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Open+Sans:wght@400;600;800&family=Libre+Barcode+39+Text&display=swap');

    .stApp {
        background-color: #f8f9fa;
        background-image: linear-gradient(135deg, rgba(244, 0, 0, 0.05) 0%, rgba(255, 199, 44, 0.05) 100%),
                          radial-gradient(#d3dce6 1px, transparent 1px);
        background-size: 100% 100%, 20px 20px;
        background-attachment: fixed;
        font-family: 'Open Sans', sans-serif !important;
    }

    /* --- REALISTYCZNY BILET LOTNICZY (BOARDING PASS) --- */
    .boarding-pass-wrapper {
        display: flex;
        justify-content: center;
        margin-top: 10px;
        margin-bottom: 40px;
    }
    .ticket {
        display: flex;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        overflow: hidden;
        width: 100%;
        max-width: 1100px;
        position: relative;
        border: 1px solid #e2e8f0;
    }
    .ticket-left {
        flex: 3;
        display: flex;
        flex-direction: column;
        border-right: 3px dashed #cbd5e1;
        position: relative;
    }
    /* Półkola wycinające bilet na łączeniu */
    .ticket-left::after, .ticket-left::before {
        content: '';
        position: absolute;
        right: -12px;
        width: 20px;
        height: 20px;
        background-color: #f8f9fa;
        border-radius: 50%;
        border-left: 1px solid #e2e8f0;
        z-index: 10;
    }
    .ticket-left::before { top: -10px; border-bottom: 1px solid #e2e8f0; border-left: none; box-shadow: inset 0 -2px 4px rgba(0,0,0,0.05); }
    .ticket-left::after { bottom: -10px; border-top: 1px solid #e2e8f0; border-left: none; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }

    .ticket-header {
        background-color: #0B2447;
        color: #FFC72C;
        padding: 15px 25px;
        font-family: 'Anton', sans-serif;
        font-size: 1.5rem;
        letter-spacing: 2px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ticket-header span.flight-class {
        font-family: 'Open Sans', sans-serif;
        font-size: 0.9rem;
        font-weight: 800;
        background: #C62828;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
    }
    .ticket-body {
        padding: 25px;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .ticket-row {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 15px;
    }
    .ticket-field {
        display: flex;
        flex-direction: column;
    }
    .ticket-field small {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 4px;
        letter-spacing: 1px;
    }
    .ticket-field strong {
        color: #0f2027;
        font-size: 1.2rem;
        font-weight: 800;
        text-transform: uppercase;
    }
    .ticket-airport {
        font-family: 'Anton', sans-serif;
        font-size: 3rem;
        color: #C62828;
        line-height: 1;
        display: flex;
        align-items: baseline;
        gap: 10px;
    }
    .ticket-airport span {
        font-family: 'Open Sans', sans-serif;
        font-size: 1rem;
        color: #0B2447;
        font-weight: 800;
    }
    
    .ticket-right {
        flex: 1;
        background: #f8fafc;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        min-width: 200px;
    }
    .ticket-right .countdown-num {
        font-family: 'Anton', sans-serif;
        font-size: 4.5rem;
        color: #0B2447;
        line-height: 1;
        margin-bottom: -5px;
    }
    .ticket-right .countdown-lbl {
        color: #C62828;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 15px;
    }
    .ticket-barcode {
        font-family: 'Libre Barcode 39 Text', cursive;
        font-size: 3.5rem;
        color: #334155;
        line-height: 0.8;
    }

    /* --- RESZTA STYLIZACJI (Zakładki, przyciski, tabele, karty) --- */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 6px;
        gap: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 20px !important;
        border: none !important;
        font-weight: 800 !important;
        color: #64748b;
        transition: all 0.2s ease;
        text-transform: uppercase;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0B2447 !important;
        color: #FFC72C !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.08) !important;
    }
    .stButton>button {
        background-color: #C62828 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(198, 40, 40, 0.3) !important;
        text-transform: uppercase;
    }
    div[data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 2px solid #e2e8f0 !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important;
    }
    .route-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #C62828;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
    }
    .route-date {
        font-family: 'Anton', sans-serif;
        font-size: 1.5rem;
        color: #0B2447;
        min-width: 120px;
        text-align: center;
        border-right: 2px dashed #e2e8f0;
        padding-right: 20px;
        margin-right: 20px;
    }
    .route-tag {
        display: inline-block;
        background-color: #FFC72C;
        color: #0B2447;
        font-size: 0.8rem;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. POŁĄCZENIE Z BAZĄ DANYCH ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"

@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_connection()

def load_data(sheet_name):
    return conn.read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl=0)

# --- 4. OBLICZENIA CZASU MISJI ---
data_wyjazdu = datetime.datetime(2026, 6, 30, 8, 0)
teraz = datetime.datetime.now()
roznica = data_wyjazdu - teraz
dni = roznica.days

# --- 5. BOARDING PASS HERO SECTION ---
st.markdown(f"""
    <div class="boarding-pass-wrapper">
        <div class="ticket">
            <div class="ticket-left">
                <div class="ticket-header">
                    <span>🇺🇸 OPERATION: IOWA 2026</span>
                    <span class="flight-class">FAMILY CLASS</span>
                </div>
                <div class="ticket-body">
                    <div class="ticket-row">
                        <div class="ticket-field">
                            <small>Passenger</small>
                            <strong>THE CREW (4)</strong>
                        </div>
                        <div class="ticket-field">
                            <small>Date</small>
                            <strong>30 JUN 2026</strong>
                        </div>
                        <div class="ticket-field">
                            <small>Final Destination</small>
                            <strong>DES MOINES, IA 🌽</strong>
                        </div>
                    </div>
                    
                    <div class="ticket-row" style="margin-top: 10px; align-items: center;">
                        <div class="ticket-field">
                            <small>Origin</small>
                            <div class="ticket-airport">POZ <span>Poznań</span></div>
                        </div>
                        <div style="font-size: 2rem; color: #cbd5e1;">✈️</div>
                        <div class="ticket-field">
                            <small>Transfer Hub</small>
                            <div class="ticket-airport" style="color: #0B2447;">ORD <span>Chicago</span></div>
                        </div>
                        <div style="font-size: 2rem; color: #cbd5e1;">🚗</div>
                        <div class="ticket-field">
                            <small>Destination</small>
                            <div class="ticket-airport">DSM <span>Des Moines</span></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="ticket-right">
                <div class="countdown-num">{dni}</div>
                <div class="countdown-lbl">Days Left</div>
                <div class="ticket-barcode">*IOWA2026*</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 6. GŁÓWNY INTERFEJS (ZAKŁADKI) ---
tab_plan, tab_zadania, tab_bagaz, tab_dzieci = st.tabs([
    "📍 Roadmap & Map", 
    "✅ Checklist", 
    "🧳 Cargo", 
    "🎮 Kids Hub"
])

# --- ZAKŁADKA 1: PLAN PODRÓŻY & MAPA ---
with tab_plan:
    st.markdown("<h3 style='color: #0f2027;'>🗺️ Trasa: Poznań ➡️ Chicago ➡️ Des Moines</h3>", unsafe_allow_html=True)
    
    # Wyświetlanie głównej mapy
    display_safe_image("mapa", "Strategiczna Mapa Operacji")

    st.divider()

    col_timeline, col_features = st.columns([2, 1])
    
    with col_timeline:
        st.markdown("<h4 style='color: #0f2027;'>Harmonogram</h4>", unsafe_allow_html=True)
        try:
            df_plan = load_data("Plan")
            
            # Renderowanie estetycznych kart HTML
            for index, row in df_plan.iterrows():
                st.markdown(f"""
                <div class="route-card">
                    <div class="route-date">{row['Dzien']}</div>
                    <div>
                        <div class="route-tag">{row['Etap']}</div>
                        <p style="margin: 0; font-weight: 600; color: #1e293b;">{row['Opis']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Panel Edycji (ukryty dla czystości)
            with st.expander("⚙️ Tryb Edycji Harmonogramu"):
                edited_plan = st.data_editor(df_plan, use_container_width=True, hide_index=True, num_rows="dynamic")
                if st.button("Zapisz Harmonogram", key="save_plan"):
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Plan", data=edited_plan)
                    st.toast("Zapisano Harmonogram!", icon="✅")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Błąd bazy danych: {e}")

    with col_features:
        st.markdown("<h4 style='color: #0f2027;'>Punkty Orientacyjne</h4>", unsafe_allow_html=True)
        # Bezpieczne wyświetlanie dodatkowych grafik
        display_safe_image("chicago")
        st.write("") # Odstęp
        display_safe_image("desmoines")


# --- ZAKŁADKA 2: ZADANIA ---
with tab_zadania:
    st.markdown("<h3 style='color: #0f2027;'>Pre-Departure Checklist</h3>", unsafe_allow_html=True)
    try:
        df_zadania = load_data("Zadania")
        df_zadania["Status"] = df_zadania["Status"].astype(str).str.upper() == "TRUE"
        
        zrobione = df_zadania['Status'].sum()
        wszystkie = len(df_zadania)
        progres = zrobione / wszystkie if wszystkie > 0 else 0
        
        col_prog, _ = st.columns([3, 1])
        with col_prog:
            st.progress(progres, text=f"STATUS: {zrobione}/{wszystkie} ukończonych zadań")
        
        edited_tasks = st.data_editor(
            df_zadania, 
            column_config={
                "Status": st.column_config.CheckboxColumn("Wykonane?", default=False, width="small"),
                "Zadanie": st.column_config.TextColumn("Opis Zadania", width="large"),
                "Kategoria": st.column_config.SelectboxColumn("Kategoria", width="medium")
            },
            use_container_width=True, hide_index=True, num_rows="dynamic"
        )
        if st.button("Aktualizuj Menu Zadań", key="save_tasks"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Zadania", data=edited_tasks)
            st.toast("Zadania zaktualizowane!", icon="✈️")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")


# --- ZAKŁADKA 3: PAKOWANIE ---
with tab_bagaz:
    st.markdown("<h3 style='color: #0f2027;'>Bagaż Family Cargo Manifest</h3>", unsafe_allow_html=True)
    try:
        df_bagaz = load_data("Bagaz")
        df_bagaz["Spakowane"] = df_bagaz["Spakowane"].astype(str).str.upper() == "TRUE"
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            kategorie = st.multiselect("Bagaż kogo pakujemy?", options=df_bagaz["Wlasciciel"].unique(), default=df_bagaz["Wlasciciel"].unique())
        
        filtered_bagaz = df_bagaz[df_bagaz["Wlasciciel"].isin(kategorie)]
        
        edited_bagaz = st.data_editor(
            filtered_bagaz,
            column_config={
                "Spakowane": st.column_config.CheckboxColumn("W walizce?", default=False, width="small"),
                "Przedmiot": st.column_config.TextColumn("Rzecz", width="large"),
                "Wlasciciel": st.column_config.TextColumn("Osoba", width="medium")
            },
            use_container_width=True, hide_index=True, num_rows="dynamic", height=500
        )
        if st.button("Zapisz Cargo Manifest", key="save_bag"):
            df_bagaz.update(edited_bagaz)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Bagaz", data=df_bagaz)
            st.toast("Zapisano stan walizek!", icon="🎒")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")


# --- ZAKŁADKA 4: STREFA DZIECI ---
with tab_dzieci:
    st.markdown("<h3 style='color: #0f2027;'>🎮 Kids Hub (Mission Log)</h3>", unsafe_allow_html=True)
    try:
        df_gry = load_data("Grywalizacja")
        df_gry["Zaliczone"] = df_gry["Zaliczone"].astype(str).str.upper() == "TRUE"
        
        suma_punktow = df_gry[df_gry['Zaliczone'] == True]['Punkty_do_zdobycia'].sum()
        max_punktow = df_gry['Punkty_do_zdobycia'].sum()
        
        st.metric("Zebrane Punkty / Cel", f"{suma_punktow} / {max_punktow} 💎")
        if max_punktow > 0:
            st.progress(int((suma_punktow / max_punktow) * 100))
        
        st.divider()
        
        for index, row in df_gry.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"<p style='background-color: rgba(100,116,139,0.05); border-radius: 8px; padding: 10px;'>⭐️ <strong>{row['Etap']}</strong></p>", unsafe_allow_html=True)
            c2.markdown(f"Trophy: `+{row['Punkty_do_zdobycia']} pkt`")
            
            if row['Zaliczone']:
                c3.markdown("✅ **Zaliczone**")
            else:
                if c3.button("ZROBIONE!", key=f"btn_{index}"):
                    st.balloons()
                    df_gry.at[index, 'Zaliczone'] = True
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=df_gry)
                    st.rerun()

        st.divider()
        with st.expander("⚙️ Tryb Rodzica (Edycja i dodawanie misji)"):
            edited_gry = st.data_editor(
                df_gry,
                column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)},
                use_container_width=True, hide_index=True, num_rows="dynamic"
            )
            if st.button("Zapisz zasady gry", key="save_gry"):
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=edited_gry)
                st.toast("Reguły zaktualizowane!")
                st.rerun()
            
    except Exception as e:
        st.error(f"Błąd: {e}")
