import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Misja: Chicago 2026",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MINIMALISTYCZNY STYL ---
# Delikatna korekta kolorów bez psucia natywnego wyglądu Streamlita
st.markdown("""
    <style>
    /* Czyste nagłówki */
    h1, h2, h3 {
        color: #0B2447 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Estetyczny główny tytuł */
    .main-title {
        background-color: #0B2447;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-title h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
    }
    /* Przyciski */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: bold;
        border: 1px solid #C62828 !important;
        color: #C62828 !important;
    }
    .stButton>button:hover {
        background-color: #C62828 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- KONFIGURACJA POŁĄCZENIA ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    return conn.read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl=0)

# --- NAGŁÓWEK ---
st.markdown("""
    <div class="main-title">
        <h1>🇺🇸 MISSION: CHICAGO 2026</h1>
        <p style="font-size: 1.2rem; margin-top: 10px;">Rodzinne Centrum Dowodzenia | Poznań ➡️ USA</p>
    </div>
""", unsafe_allow_html=True)

# --- SEKCJA GŁÓWNA: ODLICZANIE I ZDJĘCIE ---
col_info, col_image = st.columns([1, 1])

with col_info:
    data_wyjazdu = datetime.datetime(2026, 6, 30, 8, 0)
    teraz = datetime.datetime.now()
    roznica = data_wyjazdu - teraz

    st.subheader("Czas do startu ⏱️")
    m1, m2, m3 = st.columns(3)
    m1.metric("Dni", roznica.days)
    m2.metric("Godziny", roznica.seconds // 3600)
    m3.metric("Cel", "CHICAGO")
    
    st.info("💡 **Cel misji:** Bezpieczny, zorganizowany i bezstresowy wylot z dwójką dzieci.")

with col_image:
    # Używamy działającego, pięknego zdjęcia Chicago w wysokiej rozdzielczości
    st.image("https://images.unsplash.com/photo-1494522855154-9297ac14b55f?auto=format&fit=crop&w=800&q=80", 
             caption="The Bean, Chicago IL", 
             use_container_width=True)

st.markdown("---")

# --- MENU GŁÓWNE (ZAKŁADKI) ---
tab_plan, tab_zadania, tab_bagaz, tab_dzieci = st.tabs([
    "🗺️ Harmonogram", 
    "✅ Checklisty", 
    "🧳 Bagaże", 
    "👧 Strefa Dzieci"
])

# --- ZAKŁADKA 1: PLAN PODRÓŻY ---
with tab_plan:
    st.subheader("Trasa i loty")
    try:
        df_plan = load_data("Plan")
        edited_plan = st.data_editor(df_plan, use_container_width=True, hide_index=True, num_rows="dynamic")
        if st.button("💾 Zapisz Plan", key="save_plan"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Plan", data=edited_plan)
            st.success("Harmonogram zaktualizowany!")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# --- ZAKŁADKA 2: ZADANIA ---
with tab_zadania:
    st.subheader("Logistyka i dokumenty")
    try:
        df_zadania = load_data("Zadania")
        df_zadania["Status"] = df_zadania["Status"].astype(str).str.upper() == "TRUE"
        edited_tasks = st.data_editor(
            df_zadania, 
            column_config={"Status": st.column_config.CheckboxColumn("Zrobione?", default=False)},
            use_container_width=True, hide_index=True, num_rows="dynamic"
        )
        if st.button("💾 Zapisz Zadania", key="save_tasks"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Zadania", data=edited_tasks)
            st.success("Zadania zaktualizowane!")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# --- ZAKŁADKA 3: PAKOWANIE ---
with tab_bagaz:
    st.subheader("Lista Bagażowa")
    try:
        df_bagaz = load_data("Bagaz")
        df_bagaz["Spakowane"] = df_bagaz["Spakowane"].astype(str).str.upper() == "TRUE"
        
        kategorie = st.multiselect("Filtruj osobę:", options=df_bagaz["Wlasciciel"].unique(), default=df_bagaz["Wlasciciel"].unique())
        filtered_bagaz = df_bagaz[df_bagaz["Wlasciciel"].isin(kategorie)]
        
        edited_bagaz = st.data_editor(
            filtered_bagaz,
            column_config={"Spakowane": st.column_config.CheckboxColumn("W torbie?", default=False)},
            use_container_width=True, hide_index=True, num_rows="dynamic"
        )
        if st.button("💾 Zapisz Bagaże", key="save_bag"):
            df_bagaz.update(edited_bagaz)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Bagaz", data=df_bagaz)
            st.success("Bagaż zapisany!")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# --- ZAKŁADKA 4: STREFA DZIECI ---
with tab_dzieci:
    st.subheader("Wyzwania dla Dziewczynek")
    try:
        df_gry = load_data("Grywalizacja")
        df_gry["Zaliczone"] = df_gry["Zaliczone"].astype(str).str.upper() == "TRUE"
        
        for index, row in df_gry.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{row['Etap']}**")
            c2.write(f"💎 {row['Punkty_do_zdobycia']} pkt")
            
            if row['Zaliczone']:
                c3.success("ZALICZONE! 🎉")
            else:
                if c3.button("ZROBIONE!", key=f"btn_{index}"):
                    st.balloons()
                    df_gry.at[index, 'Zaliczone'] = True
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=df_gry)
                    st.rerun()

        suma_punktow = df_gry[df_gry['Zaliczone'] == True]['Punkty_do_zdobycia'].sum()
        max_punktow = df_gry['Punkty_do_zdobycia'].sum()
        
        st.divider()
        st.markdown(f"### 🏆 Zdobyte punkty: **{suma_punktow} / {max_punktow}**")
        if max_punktow > 0:
            st.progress(int((suma_punktow / max_punktow) * 100))
            
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# --- SIDEBAR (Pasek Boczny) ---
st.sidebar.markdown("### 👨‍👩‍👧‍👧 Załoga Misji:")
st.sidebar.write("🎒 **Tata** (Kierownik)")
st.sidebar.write("📋 **Mama** (Logistyka)")
st.sidebar.write("👧 **Córka** (7 lat)")
st.sidebar.write("👧 **Córka** (4 lata)")
st.sidebar.divider()
st.sidebar.success("Połączenie z bazą: Aktywne 🟢")
