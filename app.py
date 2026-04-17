import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Mission: Chicago 2026 🗽",
    page_icon="🗽",
    layout="wide"
)

# --- AMERYKAŃSKI STYL CSS (VINTAGE ROAD TRIP VIBE) ---
st.markdown("""
    <style>
    /* Importujemy amerykańskie czcionki z Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Special+Elite&family=Open+Sans:wght@400;600&display=swap');

    /* Tło z klasyczną amerykańską mapą drogową */
    .stApp {
        background-color: #e4dccf;
        background-image: url('https://www.transparenttextures.com/patterns/road-map.png');
        background-attachment: fixed;
        font-family: 'Open Sans', sans-serif;
    }

    /* Stylizowane nagłówki - efekt retro szyldu */
    h1 {
        font-family: 'Bebas Neue', sans-serif !important;
        color: #f1f1f1 !important;
        background-color: #C62828; /* Czerwień USA */
        padding: 15px 25px !important;
        border-radius: 10px !important;
        border: 4px solid #f1f1f1 !important;
        text-shadow: 3px 3px 0px #8e1c1c !important;
        letter-spacing: 2px !important;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 20px !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    h2, h3 {
        font-family: 'Bebas Neue', sans-serif !important;
        color: #0B2447; /* Navy Blue */
        letter-spacing: 1.5px;
        text-transform: uppercase;
        border-bottom: 2px solid #C62828;
        padding-bottom: 5px;
    }

    /* Przezroczyste karty z efektem rozmycia (Glassmorphism) */
    div.stExpander, div[data-testid="stDataFrame"], .stTabs, div[data-testid="stBlock"] {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 10px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Poprawa widoczności tekstu w przezroczystych kontenerach */
    .stMarkdown, p, li {
        color: #0B2447 !important;
    }

    /* Amerykańskie przyciski z efektem vintage */
    .stButton>button {
        background-color: #0B2447 !important; /* Navy Blue */
        color: white !important;
        border-radius: 30px !important;
        border: 2px solid #0B2447 !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 1.2rem !important;
        letter-spacing: 1px;
        padding: 10px 25px !important;
        transition: all 0.3s ease;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #C62828 !important; /* Zamienia się na czerwień */
        border: 2px solid #C62828 !important;
        transform: scale(1.05);
    }

    /* Stylizacja liczników (Metryki) */
    div[data-testid="stMetricValue"] {
        font-family: 'Special Elite', cursive; /* Czcionka maszyny do pisania */
        color: #C62828;
        font-size: 3.5rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.2rem !important;
        color: #0B2447;
    }
    
    /* Stylizacja zakładek */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 1.3rem !important;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 5px 5px 0 0;
        color: #0B2447;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
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

# --- NAGŁÓWEK I ODLICZANIE ---
# Główny tytuł w stylu szyldu
st.markdown("<h1>🗽 MISSION: CHICAGO 2026</h1>", unsafe_allow_html=True)

# Wstawiamy kolumny, aby wkomponować metryki i rysunek kredkami
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🇺🇸 Rodzinne Centrum Dowodzenia | Poznań ➡️ Iowa & Illinois")

    data_wyjazdu = datetime.datetime(2026, 6, 30, 8, 0)
    teraz = datetime.datetime.now()
    roznica = data_wyjazdu - teraz

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Dni do startu", roznica.days)
    m_col2.metric("Godziny", roznica.seconds // 3600)
    m_col3.metric("Cel", "CHICAGO, IL 🌭")

with col_right:
    # Wstawiamy unikalny rysunek Chicago kredkami, wygenerowany w tej sesji
    st.image("https://i.imgur.com/8Q4S8D4.png", caption="CHICAGO ROAD TRIP (Kredki)", use_container_width=True)

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
        
        edited_plan = st.data_editor(
            df_plan,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic" 
        )
        
        if st.button("🗺️ ZAPISZ PLAN (SYNC)", key="save_plan"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Plan", data=edited_plan)
            st.success("Harmonogram zaktualizowany! Trasa wyznaczona. 🚍✈️")
            
    except Exception as e:
        st.error(f"System Error: {e}. Upewnij się, że stworzyłeś zakładkę 'Plan' w Google Sheets!")

# --- ZAKŁADKA 2: ZADANIA ---
with tab_zadania:
    st.header("Formalności, Logistyka, Biurokracja")
    st.write("Wszystkie wiersze are w 100% edytowalne. Puste wiersze na dole pozwalają dodać nowe zadania.")
    
    try:
        df_zadania = load_data("Zadania")
        df_zadania["Status"] = df_zadania["Status"].astype(str).str.upper() == "TRUE"
        
        edited_tasks = st.data_editor(
            df_zadania, 
            column_config={"Status": st.column_config.CheckboxColumn("Zrobione?", default=False)},
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic" 
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
        
        kategorie = st.multiselect("Pokaż tylko:", options=df_bagaz["Wlasciciel"].unique(), default=df_bagaz["Wlasciciel"].unique())
        mask = df_bagaz["Wlasciciel"].isin(kategorie)
        filtered_bagaz = df_bagaz[mask]
        
        st.markdown("💡 *Zmień nazwę, zaznacz checkbox, lub dodaj nowy wiersz na samym dole tabeli.*")
        edited_bagaz = st.data_editor(
            filtered_bagaz,
            column_config={"Spakowane": st.column_config.CheckboxColumn("W torbie?", default=False)},
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic" 
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
        st.markdown(f"### 🏆 Razem zdobyliście: **{suma_punktow} / {max_punktow} pkt!**")
        if max_punktow > 0:
            st.progress(int((suma_punktow / max_punktow) * 100))
        
        st.markdown("---")
        with st.expander("⚙️ Tryb Rodzica (Edycja i dodawanie nowych misji)"):
            st.write("Tutaj możesz zmienić punktację, poprawić tekst lub dodać całkiem nowe wyzwanie dla dziewczynek.")
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

# --- STOPKA Z GRAFIKĄ ---
# Sidebar ze zdjęciem USA
st.sidebar.image("https://img.icons8.com/color/96/usa.png")
st.sidebar.markdown("---")
st.sidebar.write("👨‍👩‍👧‍👧 **CREW:**")
st.sidebar.write("* Tata (Kierownik)")
st.sidebar.write("* Mama (Logistyka)")
st.sidebar.write("* Córka (7 lat)")
st.sidebar.write("* Córka (4 lata)")

# Kolarz z trzema miastami na samym dole, jako "kolarz"
st.markdown("---")
st.markdown("### ✨ NASZA TRASA W OBIEKTYWIE")
# Używam linku do hostowanego kolarza retro pocztówki, wygenerowanego wcześniej
st.image("https://i.imgur.com/GzW7wM1.png", caption="Poznań ➡️ Chicago ➡️ Des Moines (Iowa)", use_container_width=True)
