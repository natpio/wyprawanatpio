import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. KONFIGURACJA STRONY (NATIVE APP FEEL) ---
st.set_page_config(
    page_title="CHICAGO '26 | Family Hub",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed" # Ukrywamy sidebar na start dla czystości
)

# --- 2. ZAAWANSOWANY CSS (POZIOM PRO) ---
st.markdown("""
    <style>
    /* Ukrywanie domyślnego UI Streamlita dla efektu aplikacji */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Import nowoczesnej czcionki - Inter (używana m.in. przez Stripe i Apple) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Tło aplikacji - subtelny, chłodny gradient */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* --- PREMIUM HERO SECTION (KARTA POKŁADOWA) --- */
    .hero-board {
        background: #0f2027; /* Fallback */
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        border-radius: 24px;
        padding: 40px;
        color: white;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        margin-top: -40px;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    
    .hero-board::after {
        content: "✈️";
        font-size: 150px;
        position: absolute;
        right: -20px;
        top: -30px;
        opacity: 0.05;
        transform: rotate(45deg);
    }

    .hero-title {
        font-weight: 800;
        font-size: 3.5rem;
        letter-spacing: -2px;
        margin: 0;
        background: -webkit-linear-gradient(#fff, #a1c4fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-weight: 300;
        font-size: 1.2rem;
        opacity: 0.8;
        margin-top: -10px;
        margin-bottom: 20px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Nowoczesne kafelki z danymi (Glassmorphism) */
    .metric-glass {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 15px 20px;
        text-align: center;
    }
    
    .metric-glass h3 { margin: 0; font-size: 0.9rem; font-weight: 400; color: #cbd5e1; text-transform: uppercase; letter-spacing: 1px; }
    .metric-glass h2 { margin: 0; font-size: 2.5rem; font-weight: 800; color: white; }

    /* --- STYLIZACJA ELEMENTÓW STREAMLIT --- */
    /* Pływające, nowoczesne zakładki (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        padding: 8px;
        gap: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 12px 24px !important;
        border: none !important;
        font-weight: 600 !important;
        color: #64748b;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #0f2027 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }

    /* Przyciski PRO */
    .stButton>button {
        background-color: #0f2027 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px 0 rgba(15, 32, 39, 0.39) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(15, 32, 39, 0.23) !important;
    }
    
    /* Czyste kontenery dla tabel */
    div[data-testid="stDataFrame"] {
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.02) !important;
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

# --- 4. OBLICZENIA CZASU ---
data_wyjazdu = datetime.datetime(2026, 6, 30, 8, 0)
teraz = datetime.datetime.now()
roznica = data_wyjazdu - teraz
dni = roznica.days
godziny = roznica.seconds // 3600

# --- 5. PREMIUM HERO SECTION (Wizualizacja) ---
st.markdown(f"""
    <div class="hero-board">
        <p class="hero-subtitle">Misión Principal | Poznań ➡️ Chicago</p>
        <h1 class="hero-title">OPERATION: CHICAGO</h1>
        <div style="display: flex; gap: 20px; margin-top: 30px; flex-wrap: wrap;">
            <div class="metric-glass">
                <h3>Odliczanie (Dni)</h3>
                <h2>{dni}</h2>
            </div>
            <div class="metric-glass">
                <h3>Godziny</h3>
                <h2>{godziny}</h2>
            </div>
            <div class="metric-glass">
                <h3>Status</h3>
                <h2>BOARDING</h2>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 6. GŁÓWNY INTERFEJS (ZAKŁADKI) ---
tab_plan, tab_zadania, tab_bagaz, tab_dzieci = st.tabs([
    "📍 Roadmap", 
    "✅ Checklist", 
    "🧳 Cargo", 
    "🎮 Kids Hub"
])

# --- ZAKŁADKA 1: PLAN PODRÓŻY ---
with tab_plan:
    col_text, col_img = st.columns([2, 1])
    with col_text:
        st.markdown("<h3 style='color: #0f2027;'>Harmonogram Lotów i Transferów</h3>", unsafe_allow_html=True)
        st.caption("Kliknij dwukrotnie w komórkę, aby ją edytować. Zaznacz po lewej, aby usunąć.")
        try:
            df_plan = load_data("Plan")
            edited_plan = st.data_editor(
                df_plan, 
                use_container_width=True, 
                hide_index=True, 
                num_rows="dynamic",
                height=400
            )
            if st.button("Zapisz harmonogram", key="save_plan"):
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Plan", data=edited_plan)
                st.toast("Zapisano pomyślnie!", icon="✅")
        except Exception as e:
            st.error(f"Błąd: {e}")
    
    with col_img:
        # Eleganckie, pionowe zdjęcie dopasowane do nowoczesnego designu
        st.image("https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?q=80&w=800&auto=format&fit=crop", 
                 caption="Windy City Awaits", use_container_width=True, clamp=True)

# --- ZAKŁADKA 2: ZADANIA ---
with tab_zadania:
    st.markdown("<h3 style='color: #0f2027;'>Logistyka & Dokumenty</h3>", unsafe_allow_html=True)
    try:
        df_zadania = load_data("Zadania")
        df_zadania["Status"] = df_zadania["Status"].astype(str).str.upper() == "TRUE"
        
        # Nowoczesny pasek postępu dla zadań
        zrobione = df_zadania['Status'].sum()
        wszystkie = len(df_zadania)
        st.progress(zrobione / wszystkie if wszystkie > 0 else 0, text=f"Proces przygotowań: {zrobione}/{wszystkie} ukończono")
        
        st.write("") # Odstęp
        
        edited_tasks = st.data_editor(
            df_zadania, 
            column_config={"Status": st.column_config.CheckboxColumn("Wykonane?", default=False)},
            use_container_width=True, hide_index=True, num_rows="dynamic"
        )
        if st.button("Aktualizuj listę", key="save_tasks"):
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Zadania", data=edited_tasks)
            st.toast("Checklista zaktualizowana!", icon="✈️")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# --- ZAKŁADKA 3: PAKOWANIE ---
with tab_bagaz:
    st.markdown("<h3 style='color: #0f2027;'>Centrum Zaopatrzenia</h3>", unsafe_allow_html=True)
    try:
        df_bagaz = load_data("Bagaz")
        df_bagaz["Spakowane"] = df_bagaz["Spakowane"].astype(str).str.upper() == "TRUE"
        
        # Nowoczesne, wbudowane filtry nad tabelą
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            kategorie = st.multiselect("Bagaż kogo pakujemy?", options=df_bagaz["Wlasciciel"].unique(), default=df_bagaz["Wlasciciel"].unique())
        
        filtered_bagaz = df_bagaz[df_bagaz["Wlasciciel"].isin(kategorie)]
        
        edited_bagaz = st.data_editor(
            filtered_bagaz,
            column_config={"Spakowane": st.column_config.CheckboxColumn("W walizce?", default=False)},
            use_container_width=True, hide_index=True, num_rows="dynamic", height=500
        )
        if st.button("Zatwierdź bagaże", key="save_bag"):
            df_bagaz.update(edited_bagaz)
            conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Bagaz", data=df_bagaz)
            st.toast("Zapisano stan walizek!", icon="🎒")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

# --- ZAKŁADKA 4: STREFA DZIECI ---
with tab_dzieci:
    st.markdown("<h3 style='color: #0f2027;'>🎮 Misje Specjalne dla Dziewczynek</h3>", unsafe_allow_html=True)
    try:
        df_gry = load_data("Grywalizacja")
        df_gry["Zaliczone"] = df_gry["Zaliczone"].astype(str).str.upper() == "TRUE"
        
        suma_punktow = df_gry[df_gry['Zaliczone'] == True]['Punkty_do_zdobycia'].sum()
        max_punktow = df_gry['Punkty_do_zdobycia'].sum()
        
        # Wielki, ładny wskaźnik postępu
        st.metric("Zebrane Punkty / Cel", f"{suma_punktow} / {max_punktow} 💎")
        if max_punktow > 0:
            st.progress(int((suma_punktow / max_punktow) * 100))
        
        st.divider()
        
        # Renderowanie misji jako osobne, estetyczne wiersze (zamiast surowej tabeli tam gdzie się da)
        for index, row in df_gry.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{row['Etap']}**")
            c2.markdown(f"🏆 `+{row['Punkty_do_zdobycia']} pkt`")
            
            if row['Zaliczone']:
                c3.markdown("✅ **Zaliczone**")
            else:
                if c3.button("ZROBIONE!", key=f"btn_{index}", help="Kliknij, jeśli zadanie wykonane!"):
                    st.balloons()
                    df_gry.at[index, 'Zaliczone'] = True
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=df_gry)
                    st.rerun()

        # Ukryty panel dla rodziców na samym dole
        with st.expander("⚙️ Tryb Administratora (Rodzica)"):
            st.caption("Zarządzaj listą zadań i punktacją")
            edited_gry = st.data_editor(
                df_gry,
                column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)},
                use_container_width=True, hide_index=True, num_rows="dynamic"
            )
            if st.button("Zapisz reguły gry", key="save_gry"):
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="Grywalizacja", data=edited_gry)
                st.toast("Reguły zaktualizowane!")
                st.rerun()
            
    except Exception as e:
        st.error(f"Błąd: {e}")
