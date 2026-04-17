import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Mission: Chicago 2026 🇺🇸",
    page_icon="🗽",
    layout="wide"
)

# --- AMERYKAŃSKI STYL CSS (CHICAGO / USA VIBE) ---
st.markdown("""
    <style>
    /* Importujemy amerykańskie czcionki z Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Open+Sans:wght@400;600&display=swap');

    /* Tło i główna czcionka */
    .stApp {
        background-color: #f8f9fa;
        background-image: radial-gradient(#d3dce6 1px, transparent 1px);
        background-size: 20px 20px;
        font-family: 'Open Sans', sans-serif;
    }

    /* Wielkie, amerykańskie nagłówki */
    h1, h2, h3 {
        font-family: 'Bebas Neue', sans-serif !important;
        color: #0B2447; /* Głęboki granat (Navy Blue) */
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* Czerwone, wyraziste przyciski */
    .stButton>button {
        background-color: #C62828 !important; /* Czerwień flagi USA */
        color: white !important;
        border-radius: 6px !important;
        border: 2px solid #9b1c1c !important;
        font-family: 'Open Sans', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Efekt po najechaniu na przycisk */
    .stButton>button:hover {
        background-color: #1565C0 !important; /* Zamienia się na niebieski */
        border: 2px solid #0d47a1 !important;
        transform: translateY(-2px);
    }

    /* Liczniki (Metryki) - np. czas do wyjazdu */
    div[data-testid="stMetricValue"] {
        font-family: 'Bebas Neue', sans-serif;
        color: #C62828;
        font-size: 3rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #0B2447;
    }
    </style>
""", unsafe_allow_html=True)

# --- KONFIGURACJA POŁĄCZENIA ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    return conn.read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl=0)

# --- NAGŁÓWEK I ODLICZANIE ---
st.title("🗽 MISSION: CHICAGO 2026")
st.subheader("🇺🇸 Rodzinne Centrum Dowodzenia | Poznań ➡️ Iowa & Illinois")

data_wyjazdu = datetime.datetime(2026, 6, 30, 8, 0)
teraz = datetime.datetime.now()
roznica = data_wyjazdu - teraz

col1, col2, col3, col4 = st.columns(4)
col1.metric("Dni do startu", roznica.days)
col2.metric("Godziny", roznica.seconds // 3600)
col3.metric("Minuty", (roznica.seconds // 60) % 60)
col4.metric("Cel", "CHICAGO, IL 🌭")

st.markdown("---")

# --- MENU GŁÓWNE (ZAKŁADKI) ---
tab_plan, tab_zadania, tab_bagaz, tab_dzieci = st.tabs([
    "🗺️ ROUTE (Plan Podróży)", 
    "✅ CHECKLIST (Zadania)", 
    "🧳 CARGO (Bagaż)", 
    "👧 KIDS ZONE (Wyzwania)"
])

# --- ZAKŁADKA 1: PLAN PODRÓŻY ---
with tab_plan:
    st.header("ROADMAP: Harmonogram Wyprawy")
    st.write("Twój plan lotu jest teraz w pełni interaktywny. Dodawaj nowe przystanki lub zmieniaj godziny bezpośrednio w tabeli poniżej.")
    
    try:
        df_plan = load_data("Plan")
        
        # Edytor planu podróży
        edited_plan = st.data_editor(
            df_plan,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic" # Pozwala na dodawanie i usuwanie etapów podróży
        )
        
        if st.button("🗺️ ZAPISZ PLAN (SYNC)", key="save_plan"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Plan", data=edited_plan)
            st.success("Harmonogram zaktualizowany! Trasa wyznaczona. 🚍✈️")
            
    except Exception as e:
        st.error(f"System Error: {e}. Upewnij się, że stworzyłeś zakładkę 'Plan' w Google Sheets!")

# --- ZAKŁADKA 2: ZADANIA ---
with tab_zadania:
    st.header("Formalności, Logistyka, Biurokracja")
    st.write("Wszystkie wiersze są w 100% edytowalne. Puste wiersze na dole pozwalają dodać nowe zadania.")
    
    try:
        df_zadania = load_data("Zadania")
        df_zadania["Status"] = df_zadania["Status"].astype(str).str.upper() == "TRUE"
        
        edited_tasks = st.data_editor(
            df_zadania, 
            column_config={"Status": st.column_config.CheckboxColumn("Zrobione?", default=False)},
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic" # Zapewnia łatwe dodawanie/usuwanie
        )
        
        if st.button("🇺🇸 ZAPISZ ZADANIA (SYNC)", key="save_tasks"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Zadania", data=edited_tasks)
            st.success("Zapisano w bazie! Świetna robota! ✅")
            
    except Exception as e:
        st.error(f"System Error: {e}")

# --- ZAKŁADKA 3: PAKOWANIE ---
with tab_bagaz:
    st.header("Listy Bagażowe (Pamiętajcie o przejściówkach!)")
    
    try:
        df_bagaz = load_data("Bagaz")
        df_bagaz["Spakowane"] = df_bagaz["Spakowane"].astype(str).str.upper() == "TRUE"
        
        # Szybki filtr na górze
        kategorie = st.multiselect("Pokaż tylko:", options=df_bagaz["Wlasciciel"].unique(), default=df_bagaz["Wlasciciel"].unique())
        mask = df_bagaz["Wlasciciel"].isin(kategorie)
        filtered_bagaz = df_bagaz[mask]
        
        st.markdown("💡 *Zmień nazwę, zaznacz checkbox, lub dodaj nowy wiersz na samym dole tabeli.*")
        edited_bagaz = st.data_editor(
            filtered_bagaz,
            column_config={"Spakowane": st.column_config.CheckboxColumn("W torbie?", default=False)},
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic" # Pełna edycja z poziomu interfejsu
        )
        
        if st.button("🦅 ZAPISZ BAGAŻE (SYNC)", key="save_bag"):
            df_bagaz.update(edited_bagaz)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Bagaz", data=df_bagaz)
            st.success("Bagaż zaktualizowany! Gotowi do drogi! 🎒")
            
    except Exception as e:
        st.error(f"System Error: {e}")

# --- ZAKŁADKA 4: STREFA DZIECI ---
with tab_dzieci:
    st.header("🌟 Wyzwania dla Małych Podróżniczek")
    st.write("Zbierajcie punkty za każdy dzielny krok w podróży!")
    
    try:
        df_gry = load_data("Grywalizacja")
        df_gry["Zaliczone"] = df_gry["Zaliczone"].astype(str).str.upper() == "TRUE"
        
        # Właściwa gra dla dzieci
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

        # Pasek postępu
        suma_punktow = df_gry[df_gry['Zaliczone'] == True]['Punkty_do_zdobycia'].sum()
        max_punktow = df_gry['Punkty_do_zdobycia'].sum()
        
        st.divider()
        st.markdown(f"### 🏆 Razem zdobyliście: **{suma_punktow} / {max_punktow} pkt!**")
        if max_punktow > 0:
            st.progress(int((suma_punktow / max_punktow) * 100))
        
        # PANEL DLA RODZICÓW (Edycja misji)
        st.markdown("---")
        with st.expander("⚙️ Tryb Rodzica (Edycja i dodawanie nowych misji)"):
            st.write("Tutaj możesz zmienić punktację, poprawić tekst lub dodać całkiem nowe wyzwanie dla dziewczynek (np. 'Zjedzenie warzyw w samolocie').")
            edited_gry = st.data_editor(
                df_gry,
                column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)},
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic"
            )
            if st.button("💾 Zapisz zmiany w misjach", key="save_gry"):
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=edited_gry)
                st.success("Misje zaktualizowane!")
                st.rerun()
            
    except Exception as e:
        st.error(f"System Error: {e}")

# --- STOPKA ---
st.sidebar.image("https://img.icons8.com/color/96/usa.png")
st.sidebar.markdown("---")
st.sidebar.write("👨‍👩‍👧‍👧 **CREW:**")
st.sidebar.write("* Tata (Kierownik wyprawy)")
st.sidebar.write("* Mama (Logistyka)")
st.sidebar.write("* Córka (7 lat)")
st.sidebar.write("* Córka (4 lata)")
