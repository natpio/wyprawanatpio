import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os
import base64
from PIL import Image, ImageFile

# Zabezpieczenie przed "uciętymi" plikami graficznymi
ImageFile.LOAD_TRUNCATED_IMAGES = True

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="IOWA '26 | OPERATION HUB 🇺🇸",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNKCJE POMOCNICZE ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

def display_safe_image(filename_base, caption=""):
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    for ext in extensions:
        file_path = f"{filename_base}{ext}"
        if os.path.exists(file_path):
            try:
                img = Image.open(file_path)
                img.load()
                st.image(img, caption=caption, use_container_width=True)
                return
            except Exception:
                st.error(f"⚠️ Plik {file_path} jest uszkodzony. Wgraj go ponownie.")
                return
    st.info(f"💡 [Brak grafiki] Wgraj plik '{filename_base}.png' do repozytorium na GitHub.")

# --- 2. ZAAWANSOWANY CSS Z DYNAMICZNYM TŁEM ---
mapa_b64 = get_base64_of_bin_file("mapa.png")
if not mapa_b64:
    mapa_b64 = get_base64_of_bin_file("mapa.jpg")

if mapa_b64:
    bg_css = f"""
    .stApp {{
        background-image: linear-gradient(rgba(248, 249, 250, 0.88), rgba(248, 249, 250, 0.88)), url("data:image/png;base64,{mapa_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Open Sans', sans-serif !important;
    }}
    """
else:
    bg_css = """
    .stApp {
        background-color: #f8f9fa;
        background-image: linear-gradient(135deg, rgba(244, 0, 0, 0.05) 0%, rgba(255, 199, 44, 0.05) 100%), radial-gradient(#d3dce6 1px, transparent 1px);
        background-size: 100% 100%, 20px 20px;
        background-attachment: fixed;
        font-family: 'Open Sans', sans-serif !important;
    }
    """

st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    #MainMenu {{ visibility: hidden; }}
    section[data-testid="stSidebar"] {{ display: none; }}

    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Open+Sans:wght@400;600;800&family=Libre+Barcode+39+Text&display=swap');

    {bg_css}

    /* --- BOARDING PASS UI --- */
    .boarding-pass-wrapper {{ display: flex; justify-content: center; margin-top: 10px; margin-bottom: 40px; }}
    .ticket {{ display: flex; background: white; border-radius: 16px; box-shadow: 0 15px 35px rgba(0,0,0,0.15); overflow: hidden; width: 100%; max-width: 1100px; border: 1px solid #e2e8f0; }}
    .ticket-left {{ flex: 3; border-right: 3px dashed #cbd5e1; position: relative; padding-bottom: 20px; }}
    .ticket-left::after, .ticket-left::before {{ content: ''; position: absolute; right: -12px; width: 20px; height: 20px; background-color: #f8f9fa; border-radius: 50%; z-index: 10; }}
    .ticket-left::before {{ top: -10px; }} .ticket-left::after {{ bottom: -10px; }}
    .ticket-header {{ background-color: #0B2447; color: #FFC72C; padding: 15px 25px; font-family: 'Anton'; font-size: 1.5rem; display: flex; justify-content: space-between; align-items: center; }}
    .flight-class {{ font-family: 'Open Sans'; font-size: 0.8rem; background: #C62828; color: white; padding: 4px 12px; border-radius: 20px; }}
    .ticket-body {{ padding: 25px; display: flex; flex-direction: column; gap: 15px; }}
    .ticket-row {{ display: flex; justify-content: space-between; align-items: center; }}
    .ticket-field {{ display: flex; flex-direction: column; }}
    .ticket-field small {{ color: #64748b; font-size: 0.7rem; text-transform: uppercase; font-weight: 800; }}
    .ticket-field strong {{ color: #0f2027; font-size: 1.1rem; font-weight: 800; }}
    .ticket-airport {{ font-family: 'Anton'; font-size: 2.5rem; color: #C62828; line-height: 1; display: flex; align-items: baseline; gap: 8px; }}
    .ticket-airport span {{ font-family: 'Open Sans'; font-size: 0.9rem; color: #0B2447; }}
    .ticket-right {{ flex: 1; background: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; min-width: 200px; }}
    .countdown-num {{ font-family: 'Anton'; font-size: 4rem; color: #0B2447; margin-bottom: -10px; }}
    .countdown-lbl {{ color: #C62828; font-weight: 800; text-transform: uppercase; font-size: 0.8rem; margin-bottom: 10px; }}
    .ticket-barcode {{ font-family: 'Libre Barcode 39 Text'; font-size: 3rem; color: #334155; }}

    /* --- ROADMAP CARDS --- */
    .route-card {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 6px solid #C62828; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; align-items: center; }}
    .route-date {{ font-family: 'Anton'; font-size: 1.5rem; color: #0B2447; min-width: 110px; text-align: center; border-right: 2px dashed #e2e8f0; padding-right: 15px; margin-right: 15px; }}
    .route-tag {{ display: inline-block; background: #FFC72C; color: #0B2447; font-size: 0.7rem; font-weight: 800; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; margin-bottom: 5px; }}
    
    /* --- TABELE I ZAKŁADKI --- */
    .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(255, 255, 255, 0.8); border-radius: 12px; padding: 6px; gap: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); backdrop-filter: blur(5px); }}
    .stTabs [data-baseweb="tab"] {{ border-radius: 8px !important; padding: 10px 20px !important; border: none !important; font-weight: 800 !important; color: #64748b; transition: all 0.2s ease; text-transform: uppercase; }}
    .stTabs [aria-selected="true"] {{ background-color: #0B2447 !important; color: #FFC72C !important; box-shadow: 0 4px 8px rgba(0,0,0,0.08) !important; }}
    .stButton>button {{ background-color: #C62828 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 5px 15px !important; font-weight: 800 !important; box-shadow: 0 2px 6px rgba(198, 40, 40, 0.3) !important; text-transform: uppercase; }}
    div[data-testid="stDataFrame"] {{ background-color: rgba(255, 255, 255, 0.95) !important; border-radius: 16px !important; overflow: hidden !important; border: 2px solid #e2e8f0 !important; box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important; backdrop-filter: blur(10px); }}

    /* --- RESPONSYWNOŚĆ (TELEFONY) --- */
    @media (max-width: 768px) {{
        .ticket {{ flex-direction: column; }}
        .ticket-left {{ border-right: none; border-bottom: 3px dashed #cbd5e1; padding-bottom: 25px; }}
        .ticket-left::after, .ticket-left::before {{ display: none; }} 
        .ticket-header {{ font-size: 1.1rem; flex-direction: column; gap: 8px; text-align: center; }}
        .ticket-row {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
        .ticket-row[style*="align-items: center"] {{ flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 5px; }}
        .ticket-airport {{ font-size: 1.5rem; }}
        .ticket-airport span {{ font-size: 0.7rem; }}
        .ticket-right {{ min-width: 100%; padding: 15px; }}
        .countdown-num {{ font-size: 3rem; margin-bottom: 0px; }}
        .ticket-barcode {{ font-size: 2.2rem; }}
        .route-card {{ flex-direction: column; align-items: flex-start; padding: 15px; }}
        .route-date {{ border-right: none; border-bottom: 2px dashed #e2e8f0; margin-right: 0; padding-right: 0; margin-bottom: 10px; padding-bottom: 5px; width: 100%; text-align: left; font-size: 1.2rem; }}
        .stTabs [data-baseweb="tab"] {{ font-size: 0.7rem !important; padding: 8px 10px !important; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. POŁĄCZENIE Z BAZĄ ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"

@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_connection()

def load_data(sheet_name):
    # Wczytanie z pominięciem cache, choć to nie zawsze wystarcza (dlatego dodano cache_data.clear niżej)
    return conn.read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl=0)

# NOWA POTĘŻNA FUNKCJA ZAPISUJĄCA (Zabija problemy z cachem)
def save_to_gsheets(worksheet_name, df):
    df_to_save = df.copy()
    # Tłumaczymy Boole na twardy tekst, żeby Google Sheets się nie pogubiło
    for col in df_to_save.columns:
        if df_to_save[col].dtype == bool:
            df_to_save[col] = df_to_save[col].map({True: "TRUE", False: "FALSE"})
    
    # Wysłanie do bazy
    conn.update(spreadsheet=SPREADSHEET_URL, worksheet=worksheet_name, data=df_to_save)
    
    # KLUCZOWE: Całkowite zresetowanie pamięci podręcznej aplikacji
    st.cache_data.clear()

# --- 4. LOGIKA CZASU ---
target_date = datetime.datetime(2026, 6, 30, 8, 0)
days_left = (target_date - datetime.datetime.now()).days

# --- 5. BILET (BOARDING PASS) ---
html_ticket = f"""
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
                <div class="ticket-row" style="margin-top: 15px; align-items: center; justify-content: center; gap: 10px;">
                    <div class="ticket-field">
                        <small>Origin</small>
                        <div class="ticket-airport">POZ <span>Poznań</span></div>
                    </div>
                    <div style="font-size: 1.2rem;">✈️</div>
                    <div class="ticket-field">
                        <small>Transfer Hub</small>
                        <div class="ticket-airport" style="color: #0B2447;">ORD <span>Chicago</span></div>
                    </div>
                    <div style="font-size: 1.2rem;">🚗</div>
                    <div class="ticket-field">
                        <small>Destination</small>
                        <div class="ticket-airport">DSM <span>Des Moines</span></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="ticket-right">
            <div class="countdown-num">{max(0, days_left)}</div>
            <div class="countdown-lbl">Days Left</div>
            <div class="ticket-barcode">*IOWA2026*</div>
        </div>
    </div>
</div>
"""
st.markdown(html_ticket.replace('\n', ''), unsafe_allow_html=True)

# --- 6. ZAKŁADKI ---
t1, t2, t3, t4 = st.tabs(["📍 Roadmap & Info", "✅ Checklist", "🧳 Cargo", "🎮 Kids Hub"])

# --- ZAKŁADKA 1: HARMONOGRAM I INFO ---
with t1:
    st.markdown("### 🗺️ Trasa: Poznań ➡️ Chicago ➡️ Des Moines")
    
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.markdown("#### Harmonogram")
        try:
            df_p = load_data("Plan")
            for _, r in df_p.iterrows():
                card_html = f"""<div class="route-card"><div class="route-date">{r['Dzien']}</div><div style="width: 100%;"><div class="route-tag">{r['Etap']}</div><p style="margin:0; font-weight:600;">{r['Opis']}</p></div></div>"""
                st.markdown(card_html.replace('\n', ''), unsafe_allow_html=True)
            
            st.write("")
            with st.expander("⚙️ Tryb Edycji Harmonogramu"):
                ed_p = st.data_editor(df_p, use_container_width=True, hide_index=True, num_rows="dynamic")
                if st.button("Zapisz Roadmap"):
                    save_to_gsheets("Plan", ed_p)
                    st.toast("Zapisano Harmonogram!", icon="✅")
                    st.rerun()
        except Exception as e: 
            st.error(f"Błąd bazy danych (Plan): {e}")

    with c_right:
        st.markdown("#### Punkty Orientacyjne")
        display_safe_image("chicago")
        st.write("")
        display_safe_image("desmoines")

# --- ZAKŁADKA 2: ZADANIA ---
with t2:
    st.markdown("### ✅ Pre-Departure Checklist")
    try:
        df_z = load_data("Zadania")
        df_z["Status"] = df_z["Status"].astype(str).str.upper() == "TRUE"
        done, total = df_z["Status"].sum(), len(df_z)
        
        st.progress(done/total if total > 0 else 0, text=f"Ukończono: {done}/{total}")
        st.write("")
        
        for i, r in df_z.iterrows():
            c1, c2 = st.columns([3, 1])
            is_done = r['Status']
            
            bg_color = "rgba(40, 167, 69, 0.1)" if is_done else "rgba(255,255,255,0.95)"
            border_color = "#28a745" if is_done else "#0B2447"
            strike = "text-decoration: line-through; opacity: 0.6;" if is_done else ""
            icon = "✅" if is_done else "📝"
            
            html_task = f"<div style='background: {bg_color}; border-left: 5px solid {border_color}; border-radius: 8px; padding: 12px 15px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); {strike}'><div style='font-weight:600; margin-bottom: 5px;'>{icon} {r['Zadanie']}</div><span class='route-tag'>{r['Kategoria']}</span></div>"
            c1.markdown(html_task.replace('\n', ''), unsafe_allow_html=True)
            
            with c2:
                st.write("")
                if is_done:
                    if st.button("COFNIJ", key=f"z_{i}"):
                        df_z.at[i, "Status"] = False
                        save_to_gsheets("Zadania", df_z)
                        st.rerun()
                else:
                    if st.button("ZROBIONE!", type="primary", key=f"z_{i}"):
                        df_z.at[i, "Status"] = True
                        save_to_gsheets("Zadania", df_z)
                        st.rerun()

        st.write("")
        with st.expander("⚙️ Tryb Edycji i Dodawania Zadań (Admin)"):
            ed_z = st.data_editor(
                df_z, 
                column_config={"Status": st.column_config.CheckboxColumn("OK", width="small")}, 
                use_container_width=True, 
                hide_index=True, 
                num_rows="dynamic"
            )
            if st.button("Zapisz Edycję Zadań"):
                save_to_gsheets("Zadania", ed_z)
                st.toast("Zapisano zmiany w bazie!")
                st.rerun()
                
    except Exception as e: 
        st.error(f"Błąd bazy danych (Zadania): {e}")

# --- ZAKŁADKA 3: BAGAŻE ---
with t3:
    st.markdown("### 🧳 Cargo Manifest")
    try:
        df_b = load_data("Bagaz")
        df_b["Spakowane"] = df_b["Spakowane"].astype(str).str.upper() == "TRUE"
        
        who = st.multiselect("Pokaż bagaż osoby:", options=df_b["Wlasciciel"].unique(), default=df_b["Wlasciciel"].unique())
        filtered_df = df_b[df_b["Wlasciciel"].isin(who)]
        
        done_b = filtered_df["Spakowane"].sum()
        total_b = len(filtered_df)
        if total_b > 0:
            st.progress(done_b/total_b, text=f"Spakowano: {done_b}/{total_b} rzeczy")
            st.write("")

        for i, r in filtered_df.iterrows():
            c1, c2 = st.columns([3, 1])
            is_packed = r['Spakowane']
            
            bg_color = "rgba(40, 167, 69, 0.1)" if is_packed else "rgba(255,255,255,0.95)"
            border_color = "#28a745" if is_packed else "#0B2447"
            strike = "text-decoration: line-through; opacity: 0.6;" if is_packed else ""
            icon = "🎒" if is_packed else "📦"
            
            html_cargo = f"<div style='background: {bg_color}; border-left: 5px solid {border_color}; border-radius: 8px; padding: 12px 15px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); {strike}'><div style='font-weight:600; margin-bottom: 5px;'>{icon} {r['Przedmiot']}</div><span style='background: #0B2447; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;'>{r['Wlasciciel']}</span></div>"
            c1.markdown(html_cargo.replace('\n', ''), unsafe_allow_html=True)
            
            with c2:
                st.write("")
                if is_packed:
                    if st.button("WYPAKUJ", key=f"b_{i}"):
                        df_b.at[i, "Spakowane"] = False 
                        save_to_gsheets("Bagaz", df_b)
                        st.rerun()
                else:
                    if st.button("DO WALIZKI", type="primary", key=f"b_{i}"):
                        df_b.at[i, "Spakowane"] = True
                        save_to_gsheets("Bagaz", df_b)
                        st.rerun()
        
        st.write("")
        with st.expander("⚙️ Tryb Edycji i Dodawania Bagażu (Admin)"):
            ed_b = st.data_editor(
                df_b, 
                column_config={"Spakowane": st.column_config.CheckboxColumn("OK", width="small")}, 
                use_container_width=True, 
                hide_index=True, 
                num_rows="dynamic"
            )
            if st.button("Zapisz Edycję Bagażu"):
                df_b.update(ed_b)
                save_to_gsheets("Bagaz", df_b)
                st.toast("Zapisano zmiany w bazie!")
                st.rerun()
                
    except Exception as e: 
        st.error(f"Błąd bazy danych (Bagaż): {e}")

# --- ZAKŁADKA 4: DZIECI ---
with t4:
    st.markdown("### 🎮 Kids Hub")
    try:
        df_g = load_data("Grywalizacja")
        df_g["Zaliczone"] = df_g["Zaliczone"].astype(str).str.upper() == "TRUE"
        score, max_s = df_g[df_g["Zaliczone"]]["Punkty_do_zdobycia"].sum(), df_g["Punkty_do_zdobycia"].sum()
        
        st.metric("Zebrane Diamenty", f"{score} / {max_s} 💎")
        st.progress(score/max_s if max_s > 0 else 0)
        st.divider()
        
        for i, r in df_g.iterrows():
            c1, c2 = st.columns([3, 1])
            html_mission = f"<div style='background-color: rgba(255,255,255,0.95); border-left: 4px solid #FFC72C; border-radius: 8px; padding: 10px 15px; margin-bottom: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>⭐️ <strong>{r['Etap']}</strong> <span style='color: #0B2447; font-weight: bold;'> (+{r['Punkty_do_zdobycia']} 💎)</span></div>"
            c1.markdown(html_mission.replace('\n', ''), unsafe_allow_html=True)
            
            with c2:
                if r["Zaliczone"]: 
                    st.markdown("<div style='padding: 10px; color: green; font-weight: 800;'>✅ ZALICZONE</div>", unsafe_allow_html=True)
                else:
                    if st.button("ZROBIONE!", type="primary", key=f"g_{i}"):
                        st.balloons()
                        df_g.at[i, "Zaliczone"] = True
                        save_to_gsheets("Grywalizacja", df_g)
                        st.rerun()
                
        st.write("")
        with st.expander("⚙️ Tryb Rodzica (Edycja i dodawanie misji)"):
            ed_g = st.data_editor(
                df_g, 
                column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)}, 
                use_container_width=True, 
                hide_index=True, 
                num_rows="dynamic"
            )
            if st.button("Zapisz zasady gry"):
                save_to_gsheets("Grywalizacja", ed_g)
                st.toast("Zaktualizowano misje!")
                st.rerun()
                
    except Exception as e: 
        st.error(f"Błąd bazy danych (Grywalizacja): {e}")
