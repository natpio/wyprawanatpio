import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os

# --- 1. KONFIGURACJA STRONY (USA-MAX NATIVE FEEL) ---
st.set_page_config(
    page_title="CHICAGO '26 | OPERATION HUB 🇺🇸",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- 2. ZAAWANSOWANY CSS "USA-MAX" (Diner / Marquee Style) ---
# Całkowite ukrycie UI Streamlita i odważna stylizacja komercyjna
st.markdown("""
    <style>
    /* Całkowite ukrycie UI Streamlita (Top Bar i Footer) */
    header[data-testid="stHeader"] { visibility: hidden; }
    div[data-testid="stHeader"] { visibility: hidden; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    /* Import komercyjnych czcionek USA - Open Sans dla czytelności i blocky Anton dla nagłówków */
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Open+Sans:wght@400;600;800&display=swap');

    /* Tło aplikacji - dynamiczny komercyjny gradient z teksturą placemat */
    .stApp {
        background-color: #f8f9fa;
        background-image: linear-gradient(135deg, rgba(244, 0, 0, 0.05) 0%, rgba(255, 199, 44, 0.05) 100%),
                          radial-gradient(#d3dce6 1px, transparent 1px);
        background-size: 100% 100%, 20px 20px;
        background-attachment: fixed;
        font-family: 'Open Sans', sans-serif !important;
    }

    /* --- PREMIUM HERO SECTION (MISSION STATUS JUMBOTRON) --- */
    .hero-marquee {
        background-color: #0B2447; /* Navy Blue */
        border-radius: 20px;
        padding: 30px 40px;
        color: #FFC72C; /* McD Yellow */
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-top: -30px;
        margin-bottom: 30px;
        border: 4px solid #C62828; /* McD Red/Maroon border */
        position: relative;
        overflow: hidden;
    }
    
    .hero-marquee::after {
        content: "🇺🇸";
        font-size: 120px;
        position: absolute;
        right: -10px;
        top: -20px;
        opacity: 0.1;
        transform: rotate(30deg);
    }

    .marquee-title {
        font-family: 'Anton', sans-serif !important;
        font-weight: 400;
        font-size: 3rem !important;
        letter-spacing: -1px;
        margin: 0;
        text-transform: uppercase;
    }
    
    .marquee-subtitle {
        font-weight: 800;
        font-size: 1.1rem;
        color: #f1f1f1;
        opacity: 0.9;
        margin-top: -5px;
        margin-bottom: 20px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Komercyjne, boldowe kafelki z metrykami */
    div[data-testid="stMetricValue"] {
        font-family: 'Anton', sans-serif;
        color: #F40000; /* Coke Red */
        font-size: 4rem !important;
        font-weight: 400;
        letter-spacing: -2px;
        margin-top: -10px;
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Open Sans', sans-serif;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        color: #0B2447;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* --- STYLIZACJA ELEMENTÓW STREAMLIT "Diner Menu Style" --- */
    /* Boldowe, komercyjne zakładki (Tabs) z pastylkami */
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

    /* Przyciski USA-PRO */
    .stButton>button {
        background-color: #C62828 !important; /* Diner Maroon */
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(198, 40, 40, 0.3) !important;
        transition: transform 0.1s ease, box-shadow 0.1s ease !important;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 18px rgba(198, 40, 40, 0.2) !important;
    }
    
    /* Stylizacja tabel jak "Diner Placemat Menu" */
    div[data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 2px solid #e2e8f0 !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. POŁĄCZENIE Z BAZĄ DANYCH (Google Sheets) ---
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
godziny = roznica.seconds // 3600

# --- 5. PREMIUM HERO SECTION (MISSION STATUS JUMBOTRON) ---
# Tytuł stylizowany na komercyjny marquee
st.markdown(f"""
    <div class="hero-marquee">
        <p class="marquee-subtitle">MISSION STATUS | OPERATION HUB | DEPARTURE: Poznań ➡️ Iowa ➡️ Chicago</p>
        <h1 class="marquee-title">OPERATION: CHICAGO</h1>
    </div>
""", unsafe_allow_html=True)

# Główne metryki USA-MAX w dynamicznym układzie
col_info, col_img_header = st.columns([2, 1])

with col_info:
    # Ogromne, Coke Red metryki w Diner Style
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Countdown (Days)", f"{dni}")
    m_col2.metric("Hours Left", f"{godziny}")
    m_col3.metric("Status", "DEPART")
    
    # Komercyjne powiadomienie o celu misji
    st.markdown("<p style='background-color: rgba(255,199,44,0.1); border-radius: 10px; padding: 15px; border: 2px solid #FFC72C; color: #0B2447;'>💡 <strong>MISSION PROFILE:</strong> Bezpieczny, zorganizowany i bezstresowy wylot z dwójką dzieci do USA.</p>", unsafe_allow_html=True)

with col_img_header:
    # Wstawiamy Twój rysunek chicago.png w stylu "Diner Placemat Sketch"
    if os.path.exists("chicago.png"):
        st.image("chicago.png", caption="CHICAGO ROAD Sketch (Diner Placemat local feature)", use_container_width=True)
    else:
        st.warning("⚠️ Brak pliku chicago.png w głównym folderze repozytorium na GitHub.")

st.markdown("---")

# --- 6. GŁÓWNY INTERFEJS (ZAKŁADKI) "Diner Menu Style" ---
tab_plan, tab_zadania, tab_bagaz, tab_dzieci = st.tabs([
    "📍 Roadmap", 
    "✅ Checklist (Menu)", 
    "🧳 Cargo (Manifest)", 
    "🎮 Kids Hub (Mission Log)"
])

# --- ZAKŁADKA 1: PLAN PODRÓŻY (Roadmap) ---
with tab_plan:
    st.markdown("<h3 style='color: #0f2027;'>📍 Road Trip & Flights Harmonogram</h3>", unsafe_allow_html=True)
    try:
        df_plan = load_data("Plan")
        edited_plan = st.data_editor(
            df_plan, 
            use_container_width=True, 
            hide_index=True, 
            num_rows="dynamic",
            height=400
        )
        if st.button("Zapisz Harmonogram (Sync to base)", key="save_plan"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Plan", data=edited_plan)
            st.toast("Zapisano Harmonogram!", icon="✅")
    except Exception as e:
        st.error(f"Błąd: {e}")
    
    st.divider()
    
    # Nowa sekcja "Route Feature: Des Moines" z rysunkiem
    st.markdown("<h3 style='color: #0f2027;'>✨ Przystanek na trasie: Des Moines, IOWA</h3>", unsafe_allow_html=True)
    # Wstawiamy Twój rysunek desmoines.png jako postcard feature
    if os.path.exists("desmoines.png"):
        st.image("desmoines.png", caption="IOWA Local Feature Sketch", use_container_width=True)
    else:
        st.warning("⚠️ Brak pliku desmoines.png w głównym folderze repozytorium na GitHub.")

# --- ZAKŁADKA 2: ZADANIA (Checklist / Pre-Departure Menu) ---
with tab_zadania:
    st.markdown("<h3 style='color: #0f2027;'>Pre-Departure Pre-Departure Checklist (Menu)</h3>", unsafe_allow_html=True)
    try:
        df_zadania = load_data("Zadania")
        df_zadania["Status"] = df_zadania["Status"].astype(str).str.upper() == "TRUE"
        
        # Pasek postępu USA-MAX
        zrobione = df_zadania['Status'].sum()
        wszystkie = len(df_zadania)
        progres = zrobione / wszystkie if wszystkie > 0 else 0
        
        # Stylizacja paska progresu jak stadion Jumbotron
        st.write("") # Odstęp
        col_prog, col_metrics = st.columns([3, 1])
        with col_prog:
            st.progress(progres, text=f"LOGISTYKA UKOŃCZONA: {zrobione}/{wszystkie} zadań")
        
        st.write("") # Odstęp
        
        edited_tasks = st.data_editor(
            df_zadania, 
            column_config={"Status": st.column_config.CheckboxColumn("Wykonane?", default=False)},
            use_container_width=True, hide_index=True, num_rows="dynamic"
        )
        if st.button("Aktualizuj Menu Zadań", key="save_tasks"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Zadania", data=edited_tasks)
            st.toast("Zadania zaktualizowane!", icon="✈️")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# --- ZAKŁADKA 3: PAKOWANIE (Cargo) ---
with tab_bagaz:
    st.markdown("<h3 style='color: #0f2027;'>Bagaż Family Cargo Manifest (Packing List)</h3>", unsafe_allow_html=True)
    try:
        df_bagaz = load_data("Bagaz")
        df_bagaz["Spakowane"] = df_bagaz["Spakowane"].astype(str).str.upper() == "TRUE"
        
        # Nowoczesne, dynamiczne filtry nad tabelą
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            kategorie = st.multiselect("Bagaż kogo pakujemy?", options=df_bagaz["Wlasciciel"].unique(), default=df_bagaz["Wlasciciel"].unique())
        
        filtered_bagaz = df_bagaz[df_bagaz["Wlasciciel"].isin(kategorie)]
        
        edited_bagaz = st.data_editor(
            filtered_bagaz,
            column_config={"Spakowane": st.column_config.CheckboxColumn("W walizce?", default=False)},
            use_container_width=True, hide_index=True, num_rows="dynamic", height=500
        )
        if st.button("Zapisz Cargo Manifest", key="save_bag"):
            df_bagaz.update(edited_bagaz)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Bagaz", data=df_bagaz)
            st.toast("Zapisano stan walizek!", icon="🎒")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# --- ZAKŁADKA 4: STREFA DZIECI (Kids Hub / Mission Log) ---
with tab_dzieci:
    st.markdown("<h3 style='color: #0f2027;'>🎮 Kids Hub (Mission Log / Wyzwania)</h3>", unsafe_allow_html=True)
    try:
        df_gry = load_data("Grywalizacja")
        df_gry["Zaliczone"] = df_gry["Zaliczone"].astype(str).str.upper() == "TRUE"
        
        suma_punktow = df_gry[df_gry['Zaliczone'] == True]['Punkty_do_zdobycia'].sum()
        max_punktow = df_gry['Punkty_do_zdobycia'].sum()
        
        # Wielki, ładny stadium-style wskaźnik postępu
        st.metric("Zebrane Punkty / Cel", f"{suma_punktow} / {max_punktow} 💎")
        if max_punktow > 0:
            st.progress(int((suma_punktow / max_punktow) * 100))
        
        st.divider()
        
        # Renderowanie misji jako komercyjne pastylki
        for index, row in df_gry.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"<p style='background-color: rgba(100,116,139,0.05); border-radius: 8px; padding: 10px;'>⭐️ <strong>{row['Etap']}</strong></p>", unsafe_allow_html=True)
            c2.markdown(f"Trophy: `+{row['Punkty_do_zdobycia']} pkt`")
            
            if row['Zaliczone']:
                c3.markdown("✅ **Zaliczone**")
            else:
                if c3.button("ZROBIONE!", key=f"btn_{index}", help="Kliknij, jeśli zadanie wykonane!"):
                    st.balloons()
                    df_gry.at[index, 'Zaliczone'] = True
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=df_gry)
                    st.rerun()

        # Panel Administratora USA na dole
        st.divider()
        with st.expander("⚙️ Tryb Rodzica (Edycja i dodawanie nowych misji)"):
            st.caption("Zarządzaj listą misji i punktacją")
            edited_gry = st.data_editor(
                df_gry,
                column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)},
                use_container_width=True, hide_index=True, num_rows="dynamic"
            )
            if st.button("Zapisz zasady gry (Sync)", key="save_gry"):
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=edited_gry)
                st.toast("Reguły gry zaktualizowane!")
                st.rerun()
            
    except Exception as e:
        st.error(f"Błąd: {e}")

# --- SIDEBAR (Pasek Boczny - Załoga Misji) "Stadium Scoreboard Style" ---
# Używamy nowych, american icons
st.sidebar.markdown("### 👨‍👩‍👧‍👧 ZAŁOGA MISJI (THE CREW):")
st.sidebar.write("🎒 🏈 **Tata** (The Big Boss)")
st.sidebar.write("📋 ⚾ **Mama** (Logistics Manager)")
st.sidebar.write("👧 ✈️ **Córka** (Future Explorer, 7 lat)")
st.sidebar.write("👧 🚌 **Córka** (Country Kid, 4 lata)")
st.sidebar.divider()
st.sidebar.success("Połączenie z bazą IOWA/IL: Aktywne 🔴🟢")
