import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Misja: Chicago 2026 🇺🇸",
    page_icon="✈️",
    layout="wide"
)

# --- KONFIGURACJA POŁĄCZENIA ---
# Wklej tutaj swój link do Google Sheets
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"

conn = st.connection("gsheets", type=GSheetsConnection)

# Funkcja pomocnicza do pobierania danych
def load_data(sheet_name):
    return conn.read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name)

# --- NAGŁÓWEK I ODLICZANIE ---
st.title("🗽 Misja: Chicago 2026")
st.subheader("Centrum Dowodzenia Rodzinną Wyprawą")

data_wyjazdu = datetime.datetime(2026, 6, 30, 8, 0) # Przykładowa godzina wyjazdu z Poznania
teraz = datetime.datetime.now()
roznica = data_wyjazdu - teraz

col1, col2, col3, col4 = st.columns(4)
col1.metric("Dni", roznica.days)
col2.metric("Godziny", roznica.seconds // 3600)
col3.metric("Minuty", (roznica.seconds // 60) % 60)
col4.metric("Status", "W przygotowaniu 🛠️")

# --- MENU GŁÓWNE (ZAKŁADKI) ---
tab_plan, tab_zadania, tab_bagaz, tab_dzieci = st.tabs([
    "🗺️ Plan Podróży", 
    "✅ Lista Zadań", 
    "🧳 Pakowanie", 
    "🌟 Strefa Dzieci"
])

# --- ZAKŁADKA 1: PLAN PODRÓŻY ---
with tab_plan:
    st.header("Harmonogram Wyprawy")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        ### 🚌 Etap 1: Polska
        * **30.06.2026:** Wyjazd Flixbusem z Poznania.
        * **30.06.2026:** Przyjazd do Warszawy, zameldowanie w hotelu.
        * **Noc 30.06/01.07:** Odpoczynek i transfer na Okęcie (WAW).
        """)
    
    with col_b:
        st.markdown("""
        ### ✈️ Etap 2: Loty
        * **01.07.2026:** Lot Warszawa (WAW) -> Monachium (MUC).
        * **01.07.2026:** Przesiadka w Monachium (pamiętać o Gate!).
        * **01.07.2026:** Lot Monachium (MUC) -> Chicago (ORD).
        * **Welcome to USA! 🇺🇸**
        """)

# --- ZAKŁADKA 2: ZADANIA ---
with tab_zadania:
    st.header("Formalności i Logistyka")
    df_zadania = load_data("Zadania")
    
    # Edytor tabeli
    edited_tasks = st.data_editor(
        df_zadania, 
        column_config={"Status": st.column_config.CheckboxColumn("Zrobione?")},
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("Zapisz status zadań", key="save_tasks"):
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Zadania", data=edited_tasks)
        st.success("Zapisano zmiany w Google Sheets!")

# --- ZAKŁADKA 3: PAKOWANIE ---
with tab_bagaz:
    st.header("Listy Bagażowe")
    df_bagaz = load_data("Bagaz")
    
    # Filtry
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        kat_filter = st.multiselect("Filtruj kategorię:", options=df_bagaz["Kategoria"].unique(), default=df_bagaz["Kategoria"].unique())
    with col_f2:
        osoba_filter = st.multiselect("Czyj to bagaż?:", options=df_bagaz["Wlasciciel"].unique(), default=df_bagaz["Wlasciciel"].unique())
    
    # Filtrowanie danych
    mask = df_bagaz["Kategoria"].isin(kat_filter) & df_bagaz["Wlasciciel"].isin(osoba_filter)
    filtered_bagaz = df_bagaz[mask]
    
    # Edytor bagażu
    edited_bagaz = st.data_editor(
        filtered_bagaz,
        column_config={"Spakowane": st.column_config.CheckboxColumn("W torbie?")},
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("Zapisz postęp pakowania", key="save_bag"):
        # Uwaga: Aktualizujemy cały arkusz, łącząc zmiany z przefiltrowanego widoku
        df_bagaz.update(edited_bagaz)
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Bagaz", data=df_bagaz)
        st.success("Lista bagażowa zaktualizowana!")

# --- ZAKŁADKA 4: STREFA DZIECI ---
with tab_dzieci:
    st.header("🌟 Wyzwania dla Małych Podróżniczek")
    st.write("Zbierajcie punkty za każdy dzielny krok w podróży!")
    
    df_gry = load_data("Grywalizacja")
    
    for index, row in df_gry.iterrows():
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{row['Etap']}**")
        c2.write(f"💎 {row['Punkty_do_zdobycia']} pkt")
        
        if row['Zaliczone']:
            c3.success("ZALICZONE!")
        else:
            if c3.button("ZROBIONE!", key=f"btn_{index}"):
                # Animacja sukcesu
                st.balloons()
                # Aktualizacja danych
                df_gry.at[index, 'Zaliczone'] = True
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=df_gry)
                st.rerun()

    # Podsumowanie punktów
    suma_punktow = df_gry[df_gry['Zaliczone'] == True]['Punkty_do_zdobycia'].sum()
    st.divider()
    st.markdown(f"### 🏆 Razem zdobyliście: **{suma_punktow} punktów!**")
    if suma_punktow > 50:
        st.info("🎁 Nagroda w Chicago jest coraz bliżej!")

# --- STOPKA ---
st.sidebar.image("https://img.icons8.com/color/96/usa.png")
st.sidebar.markdown("---")
st.sidebar.write("👨‍👩‍👧‍👧 **Uczestnicy:**")
st.sidebar.write("* Tata (Kierownik wyprawy)")
st.sidebar.write("* Mama (Logistyka)")
st.sidebar.write("* Córka (7 lat)")
st.sidebar.write("* Córka (4 lata)")
