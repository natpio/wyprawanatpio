import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import os
import base64
import requests
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

st.set_page_config(page_title="IOWA '26 | OPERATION HUB 🇺🇸", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

# --- FUNKCJE POMOCNICZE ---
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

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
                # AKTUALIZACJA STREAMLIT: width="stretch" zamiast use_container_width=True
                st.image(img, caption=caption, width="stretch")
                return
            except Exception:
                st.error(f"⚠️ Plik {file_path} jest uszkodzony. Wgraj go ponownie.")
                return
    st.info(f"💡 [Brak grafiki] Wgraj plik '{filename_base}.png' do repozytorium na GitHub.")

# --- API POGODOWE ---
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
    except Exception:
        return "Brak danych 🌡️"

# --- POŁĄCZENIE Z BAZĄ ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1SVabwrxRpf2Q7dAdRIR3xC9HCQs2sFMI4Z3dAn9HArY"

@st.cache_resource
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

conn = get_connection()

def load_data(sheet_name):
    return conn.read(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, ttl=0)

def init_state(sheet_name, bool_cols=[]):
    state_key = f"df_{sheet_name}"
    if state_key not in st.session_state:
        try:
            df = load_data(sheet_name)
            for col in bool_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip().str.upper().isin(["TRUE", "1", "YES", "T", "TAK"])
            st.session_state[state_key] = df
        except Exception as e:
            st.error(f"Błąd ładowania danych: {e}")
            st.session_state[state_key] = pd.DataFrame()

init_state("Plan")
init_state("Zadania", ["Status"])
init_state("Bagaz", ["Spakowane"])
init_state("Grywalizacja", ["Zaliczone"])

def save_and_sync(sheet_name):
    try:
        df = st.session_state[f"df_{sheet_name}"].copy()
        
        for col in df.columns:
            df[col] = df[col].apply(lambda x: "TRUE" if x is True or str(x).strip().upper() == "TRUE" else ("FALSE" if x is False or str(x).strip().upper() == "FALSE" else x))
            
        conn.update(spreadsheet=SPREADSHEET_URL, worksheet=sheet_name, data=df)
        st.cache_data.clear()
        return True
        
    except Exception as e:
        st.error(f"🚨 BŁĄD ZAPISU DO CHMURY: {e}")
        st.info("Prawdopodobnie aplikacja nie ma uprawnień do EDYCJI Twojego pliku Google Sheets. Czy na pewno wgrałeś plik 'secrets.toml' i dodałeś maila roboczego jako Edytora?")
        st.stop() 

# --- ZAAWANSOWANY CSS ---
mapa_b64 = get_base64_of_bin_file("mapa.png") or get_base64_of_bin_file("mapa.jpg")
bg_css = f'background-image: linear-gradient(rgba(248, 249, 250, 0.88), rgba(248, 249, 250, 0.88)), url("data:image/png;base64,{mapa_b64}");' if mapa_b64 else 'background-color: #f8f9fa; background-image: linear-gradient(135deg, rgba(244, 0, 0, 0.05) 0%, rgba(255, 199, 44, 0.05) 100%), radial-gradient(#d3dce6 1px, transparent 1px);'

css = f"""
<style>
header[data-testid="stHeader"] {{ visibility: hidden; }} footer {{ visibility: hidden; }} #MainMenu {{ visibility: hidden; }} section[data-testid="stSidebar"] {{ display: none; }}
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Open+Sans:wght@400;600;800&family=Libre+Barcode+39+Text&display=swap');
.stApp {{ {bg_css} background-size: cover; background-position: center; background-attachment: fixed; font-family: 'Open Sans', sans-serif !important; }}
.boarding-pass-wrapper {{ display: flex; justify-content: center; margin-top: -10px; margin-bottom: 30px; }}
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
.route-card {{ background: rgba(255,255,255,0.95); border-radius: 12px; padding: 20px; margin-bottom: 15px; border-left: 6px solid #C62828; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; align-items: center; }}
.route-date {{ font-family: 'Anton'; font-size: 1.5rem; color: #0B2447; min-width: 110px; text-align: center; border-right: 2px dashed #e2e8f0; padding-right: 15px; margin-right: 15px; }}
.route-tag {{ display: inline-block; background: #FFC72C; color: #0B2447; font-size: 0.7rem; font-weight: 800; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; margin-bottom: 5px; }}
.stTabs [data-baseweb="tab-list"] {{ background-color: rgba(255, 255, 255, 0.8); border-radius: 12px; padding: 6px; gap: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); backdrop-filter: blur(5px); }}
.stTabs [data-baseweb="tab"] {{ border-radius: 8px !important; padding: 10px 20px !important; border: none !important; font-weight: 800 !important; color: #64748b; transition: all 0.2s ease; text-transform: uppercase; }}
.stTabs [aria-selected="true"] {{ background-color: #0B2447 !important; color: #FFC72C !important; box-shadow: 0 4px 8px rgba(0,0,0,0.08) !important; }}
.stButton>button {{ background-color: #C62828 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 5px 15px !important; font-weight: 800 !important; box-shadow: 0 2px 6px rgba(198, 40, 40, 0.3) !important; text-transform: uppercase; }}
div[data-testid="stDataFrame"] {{ background-color: rgba(255, 255, 255, 0.95) !important; border-radius: 16px !important; overflow: hidden !important; border: 2px solid #e2e8f0 !important; box-shadow: 0 10px 20px rgba(0,0,0,0.04) !important; backdrop-filter: blur(10px); }}

.customs-card {{ background-color: #e0f2fe; border: 2px solid #0284c7; border-radius: 12px; padding: 25px; font-family: 'Courier New', Courier, monospace; color: #0f172a; box-shadow: 0 10px 25px rgba(2, 132, 199, 0.15); }}
.customs-title {{ text-align: center; font-family: 'Anton', sans-serif; color: #0284c7; font-size: 1.8rem; margin-top: 0; margin-bottom: 5px; letter-spacing: 1px; }}
.customs-sub {{ text-align: center; font-family: 'Open Sans', sans-serif; color: #64748b; font-size: 0.8rem; margin-bottom: 20px; text-transform: uppercase; font-weight: bold; }}
.customs-line {{ border-bottom: 1px solid #bae6fd; padding-bottom: 8px; margin-bottom: 12px; font-size: 0.95rem; line-height: 1.4; }}
.c-num {{ font-weight: 800; color: #0284c7; margin-right: 5px; display: inline-block; min-width: 25px; }}
.c-ans {{ font-weight: 800; color: #C62828; text-transform: uppercase; border-bottom: 1px dashed #C62828; padding-left: 5px; padding-right: 5px; }}

@media (max-width: 768px) {{
    .ticket {{ flex-direction: column; }} .ticket-left {{ border-right: none; border-bottom: 3px dashed #cbd5e1; padding-bottom: 25px; }} .ticket-left::after, .ticket-left::before {{ display: none; }} 
    .ticket-header {{ font-size: 1.1rem; flex-direction: column; gap: 8px; text-align: center; }} .ticket-row {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
    .ticket-row[style*="align-items: center"] {{ flex-direction: row; flex-wrap: wrap; justify-content: center; gap: 5px; }} .ticket-airport {{ font-size: 1.5rem; }} .ticket-airport span {{ font-size: 0.7rem; }}
    .ticket-right {{ min-width: 100%; padding: 15px; }} .countdown-num {{ font-size: 3rem; margin-bottom: 0px; }} .ticket-barcode {{ font-size: 2.2rem; }}
    .route-card {{ flex-direction: column; align-items: flex-start; padding: 15px; }} .route-date {{ border-right: none; border-bottom: 2px dashed #e2e8f0; margin-right: 0; padding-right: 0; margin-bottom: 10px; padding-bottom: 5px; width: 100%; text-align: left; font-size: 1.2rem; }}
    .stTabs [data-baseweb="tab"] {{ font-size: 0.65rem !important; padding: 8px 6px !important; }}
}}
</style>
"""
st.markdown(css.replace('\n', ''), unsafe_allow_html=True)

# WIDGETY HTML
def render_boarding_pass(days_left):
    html = f"""<div class="boarding-pass-wrapper"><div class="ticket"><div class="ticket-left"><div class="ticket-header"><span>🇺🇸 OPERATION: IOWA 2026</span><span class="flight-class">FAMILY CLASS</span></div><div class="ticket-body"><div class="ticket-row"><div class="ticket-field"><small>Passenger</small><strong>THE CREW (4)</strong></div><div class="ticket-field"><small>Date</small><strong>30 JUN 2026</strong></div><div class="ticket-field"><small>Final Destination</small><strong>DES MOINES, IA 🌽</strong></div></div><div class="ticket-row" style="margin-top: 15px; align-items: center; justify-content: center; gap: 10px;"><div class="ticket-field"><small>Origin</small><div class="ticket-airport">POZ <span>Poznań</span></div></div><div style="font-size: 1.2rem;">✈️</div><div class="ticket-field"><small>Transfer Hub</small><div class="ticket-airport" style="color: #0B2447;">ORD <span>Chicago</span></div></div><div style="font-size: 1.2rem;">🚗</div><div class="ticket-field"><small>Destination</small><div class="ticket-airport">DSM <span>Des Moines</span></div></div></div></div></div><div class="ticket-right"><div class="countdown-num">{max(0, days_left)}</div><div class="countdown-lbl">Days Left</div><div class="ticket-barcode">*IOWA2026*</div></div></div></div>"""
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)

def jetlag_widget(city, flag, weather, timezone, subtitle, border_color):
    html = f"""
    <style>@import url('https://fonts.googleapis.com/css2?family=Anton&family=Open+Sans:wght@400;600;800&display=swap'); body {{ margin: 0; padding: 0; background: transparent; }} .card {{ background: rgba(255, 255, 255, 0.95); border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid {border_color}; font-family: 'Open Sans', sans-serif; box-sizing: border-box; height: 100%; }} .city {{ font-weight: 800; font-size: 1.1rem; color: #0B2447; margin-bottom: 5px; text-transform: uppercase; }} .weather {{ font-size: 1.4rem; color: #C62828; font-weight: 800; margin-bottom: 5px; }} .clock {{ font-family: 'Anton', sans-serif; font-size: 2.5rem; color: #0B2447; line-height: 1.2; margin-bottom: 5px; }} .sub {{ font-size: 0.75rem; color: #64748b; font-weight: 800; text-transform: uppercase; }}</style>
    <div class="card"><div class="city">{flag} {city}</div><div class="weather">{weather}</div><div class="clock" id="clock_{city.replace(' ','')}">--:--:--</div><div class="sub">{subtitle}</div></div>
    <script>
    function updateTime_{city.replace(' ','')}() {{ const now = new Date(); const opts = {{ hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }}; document.getElementById('clock_{city.replace(' ','')}').innerText = now.toLocaleTimeString('en-GB', {{timeZone: '{timezone}', ...opts}}); }}
    setInterval(updateTime_{city.replace(' ','')}, 1000); updateTime_{city.replace(' ','')}();
    </script>
    """
    # AKTUALIZACJA STREAMLIT: Zastąpiono components.v1 na nowoczesny i wolny od błędów st.html / st.markdown
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)

def render_customs_card(d):
    html = f"""<div class="customs-card"><h3 class="customs-title">CUSTOMS DECLARATION</h3><div class="customs-sub">CBP Form 6059B (Cheat Sheet)</div><div class="customs-line"><span class="c-num">1.</span> Family Name: <span class="c-ans">{d['c_last']}</span> | First: <span class="c-ans">{d['c_first']}</span> | Middle: <span class="c-ans">{d['c_middle']}</span></div><div class="customs-line"><span class="c-num">2.</span> Birth date (MM/DD/YY): <span class="c-ans">{d['c_dob']}</span></div><div class="customs-line"><span class="c-num">3.</span> Number of family members traveling with you: <span class="c-ans">{d['c_mem']}</span></div><div class="customs-line"><span class="c-num">4.</span> (a) U.S. Street Address: <span class="c-ans">{d['c_street']}</span></div><div class="customs-line">&nbsp;&nbsp;&nbsp;(b) City: <span class="c-ans">{d['c_city']}</span> &nbsp;&nbsp;(c) State: <span class="c-ans">{d['c_state']}</span></div><div class="customs-line"><span class="c-num">5.</span> Passport issued by: <span class="c-ans">{d['c_pass_country']}</span></div><div class="customs-line"><span class="c-num">6.</span> Passport number: <span class="c-ans">{d['c_pass_no']}</span></div><div class="customs-line"><span class="c-num">7.</span> Country of Residence: <span class="c-ans">{d['c_residence']}</span></div><div class="customs-line"><span class="c-num">8.</span> Countries visited on this trip prior to U.S. arrival: <span class="c-ans">{d['c_visited']}</span></div><div class="customs-line"><span class="c-num">9.</span> Airline/Flight No.: <span class="c-ans">{d['c_fly']}</span></div><div class="customs-line"><span class="c-num">10.</span> The primary purpose of this trip is business: <span class="c-ans">{d['c_10']}</span></div><div style="margin-top: 15px; font-weight: bold; color: #0284c7; font-size: 0.85rem;">11. I am (We are) bringing:</div><div class="customs-line">&nbsp;&nbsp;(a) fruits, vegetables, plants, seeds, food, insects: <span class="c-ans">{d['c_11a']}</span></div><div class="customs-line">&nbsp;&nbsp;(b) meats, animals, animal/wildlife products: <span class="c-ans">{d['c_11b']}</span></div><div class="customs-line">&nbsp;&nbsp;(c) disease agents, cell cultures, snails: <span class="c-ans">{d['c_11c']}</span></div><div class="customs-line">&nbsp;&nbsp;(d) soil or have been on a farm/ranch/pasture: <span class="c-ans">{d['c_11d']}</span></div><div class="customs-line"><span class="c-num">12.</span> I have (We have) been in close proximity of livestock: <span class="c-ans">{d['c_12']}</span></div><div class="customs-line"><span class="c-num">13.</span> Carrying currency/monetary instruments over $10,000 U.S.: <span class="c-ans">{d['c_13']}</span></div><div class="customs-line"><span class="c-num">14.</span> I have (We have) commercial merchandise: <span class="c-ans">{d['c_14']}</span></div><div style="margin-top: 15px;"><span class="c-num">15.</span> Visitors - total value of all articles that will remain in the U.S.: <span class="c-ans">${d['c_15']}</span></div></div>"""
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)


# --- ODŚWIEŻANIE ---
_, col_sync = st.columns([8, 2])
# AKTUALIZACJA STREAMLIT: Zastąpiono use_container_width=True
if col_sync.button("🔄 Wymuś Odświeżenie Chmury", width="stretch"):
    st.cache_data.clear()
    for key in list(st.session_state.keys()):
        if key.startswith("df_"): del st.session_state[key]
    safe_rerun()

# --- TOP ---
target_date = datetime.datetime(2026, 6, 30, 8, 0)
render_boarding_pass((target_date - datetime.datetime.now()).days)

if st.session_state.get("show_balloons", False):
    st.balloons()
    st.session_state["show_balloons"] = False

# --- ZAKŁADKI ---
t1, t2, t3, t4, t5 = st.tabs(["📍 Roadmap", "✅ Checklist", "🧳 Cargo", "🎮 Kids Hub", "🛂 Odprawa"])

# ZAKŁADKA 1
with t1:
    st.markdown("### 🌤️ Jet-Lag Planner")
    w1, w2, w3 = st.columns(3)
    with w1: jetlag_widget("Poznań", "🇵🇱", get_weather(52.4064, 16.9252), "Europe/Warsaw", "Baza Domowa", "#0B2447")
    with w2: jetlag_widget("Chicago", "🇺🇸", get_weather(41.85, -87.65), "America/Chicago", "-7 Godzin", "#FFC72C")
    with w3: jetlag_widget("Des Moines", "🌽", get_weather(41.5868, -93.625), "America/Chicago", "-7 Godzin", "#C62828")
    
    st.divider()
    c_left, c_right = st.columns([2, 1])
    with c_left:
        df_p = st.session_state.get("df_Plan")
        if not df_p.empty:
            for _, r in df_p.iterrows():
                card = f"""<div class="route-card"><div class="route-date">{r['Dzien']}</div><div style="width: 100%;"><div class="route-tag">{r['Etap']}</div><p style="margin:0; font-weight:600;">{r['Opis']}</p></div></div>"""
                st.markdown(card.replace('\n', ''), unsafe_allow_html=True)
            with st.expander("⚙️ Tryb Edycji"):
                # AKTUALIZACJA STREAMLIT: Zastąpiono use_container_width=True
                ed_p = st.data_editor(df_p, width="stretch", hide_index=True, num_rows="dynamic")
                if st.button("Zapisz Roadmap"):
                    st.session_state["df_Plan"] = ed_p
                    if save_and_sync("Plan"): safe_rerun()
    with c_right:
        display_safe_image("chicago")
        st.write("")
        display_safe_image("desmoines")

# ZAKŁADKA 2
with t2:
    df_z = st.session_state.get("df_Zadania")
    if not df_z.empty:
        done, total = df_z["Status"].sum(), len(df_z)
        st.progress(done/total if total > 0 else 0, text=f"Ukończono: {done}/{total}")
        for i, r in df_z.iterrows():
            c1, c2 = st.columns([3, 1])
            is_done = r['Status']
            bg, border, strike, icon = ("rgba(40,167,69,0.1)", "#28a745", "text-decoration:line-through; opacity:0.6;", "✅") if is_done else ("rgba(255,255,255,0.95)", "#0B2447", "", "📝")
            html_task = f"<div style='background:{bg}; border-left:5px solid {border}; border-radius:8px; padding:12px; margin-bottom:8px;'><div style='font-weight:600; {strike}'>{icon} {r['Zadanie']}</div><span class='route-tag'>{r['Kategoria']}</span></div>"
            c1.markdown(html_task.replace('\n', ''), unsafe_allow_html=True)
            with c2:
                if is_done:
                    if st.button("COFNIJ", key=f"z_{i}"): 
                        st.session_state["df_Zadania"].at[i, "Status"] = False
                        if save_and_sync("Zadania"): safe_rerun()
                else:
                    if st.button("ZROBIONE", type="primary", key=f"z_{i}"): 
                        st.session_state["df_Zadania"].at[i, "Status"] = True
                        if save_and_sync("Zadania"): safe_rerun()
        with st.expander("⚙️ Admin Zadań"):
            # AKTUALIZACJA STREAMLIT: Zastąpiono use_container_width=True
            ed_z = st.data_editor(df_z, column_config={"Status": st.column_config.CheckboxColumn("OK", width="small")}, hide_index=True, num_rows="dynamic", width="stretch")
            if st.button("Zapisz Zadania"): 
                st.session_state["df_Zadania"] = ed_z
                if save_and_sync("Zadania"): safe_rerun()

# ZAKŁADKA 3
with t3:
    df_b = st.session_state.get("df_Bagaz")
    if not df_b.empty:
        who = st.multiselect("Bagaż osoby:", options=df_b["Wlasciciel"].unique(), default=df_b["Wlasciciel"].unique())
        filtered = df_b[df_b["Wlasciciel"].isin(who)]
        if len(filtered) > 0: st.progress(filtered["Spakowane"].sum()/len(filtered), text=f"Spakowano: {filtered['Spakowane'].sum()}/{len(filtered)}")
        for i, r in filtered.iterrows():
            c1, c2 = st.columns([3, 1])
            is_packed = r['Spakowane']
            bg, border, strike, icon = ("rgba(40,167,69,0.1)", "#28a745", "text-decoration:line-through; opacity:0.6;", "🎒") if is_packed else ("rgba(255,255,255,0.95)", "#0B2447", "", "📦")
            html_cargo = f"<div style='background:{bg}; border-left:5px solid {border}; border-radius:8px; padding:12px; margin-bottom:8px;'><div style='font-weight:600; {strike}'>{icon} {r['Przedmiot']}</div><span style='background:#0B2447; color:white; padding:3px 10px; border-radius:20px; font-size:0.7rem;'>{r['Wlasciciel']}</span></div>"
            c1.markdown(html_cargo.replace('\n', ''), unsafe_allow_html=True)
            with c2:
                if is_packed:
                    if st.button("WYPAKUJ", key=f"b_{i}"): 
                        st.session_state["df_Bagaz"].at[i, "Spakowane"] = False
                        if save_and_sync("Bagaz"): safe_rerun()
                else:
                    if st.button("DO WALIZKI", type="primary", key=f"b_{i}"): 
                        st.session_state["df_Bagaz"].at[i, "Spakowane"] = True
                        if save_and_sync("Bagaz"): safe_rerun()
        with st.expander("⚙️ Admin Bagażu"):
            # AKTUALIZACJA STREAMLIT: Zastąpiono use_container_width=True
            ed_b = st.data_editor(df_b, column_config={"Spakowane": st.column_config.CheckboxColumn("OK", width="small")}, hide_index=True, num_rows="dynamic", width="stretch")
            if st.button("Zapisz Bagaż"): 
                st.session_state["df_Bagaz"] = ed_b
                if save_and_sync("Bagaz"): safe_rerun()

# ZAKŁADKA 4
with t4:
    df_g = st.session_state.get("df_Grywalizacja")
    if not df_g.empty:
        score, max_s = df_g[df_g["Zaliczone"]]["Punkty_do_zdobycia"].sum(), df_g["Punkty_do_zdobycia"].sum()
        st.metric("Zebrane Diamenty", f"{score} / {max_s} 💎")
        st.progress(score/max_s if max_s > 0 else 0)
        for i, r in df_g.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"<div style='background:rgba(255,255,255,0.95); border-left:4px solid #FFC72C; padding:10px; margin-bottom:5px; border-radius:8px;'>⭐️ <strong>{r['Etap']}</strong> (+{r['Punkty_do_zdobycia']} 💎)</div>", unsafe_allow_html=True)
            with c2:
                if r["Zaliczone"]: st.markdown("<div style='padding:10px; color:green; font-weight:800;'>✅ OK</div>", unsafe_allow_html=True)
                elif st.button("ZROBIONE", type="primary", key=f"g_{i}"): 
                    st.session_state["df_Grywalizacja"].at[i, "Zaliczone"] = True
                    st.session_state["show_balloons"] = True
                    if save_and_sync("Grywalizacja"): safe_rerun()
        with st.expander("⚙️ Admin Gry"):
            # AKTUALIZACJA STREAMLIT: Zastąpiono use_container_width=True
            ed_g = st.data_editor(df_g, column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)}, hide_index=True, num_rows="dynamic", width="stretch")
            if st.button("Zapisz Gry"): 
                st.session_state["df_Grywalizacja"] = ed_g
                if save_and_sync("Grywalizacja"): safe_rerun()

# ZAKŁADKA 5
with t5:
    st.info("💡 F5 zawsze wyczyści te pola. Jeśli przepisałeś formularz celny, dane po prostu giną w niepamięci przeglądarki.")
    c_form, c_card = st.columns([1, 1.2])
    with c_form:
        c_last = st.text_input("1. Nazwisko (Family Name)", value=st.session_state.get("c_last", ""))
        c1a, c1b = st.columns(2)
        with c1a: c_first = st.text_input("1. Imię (First Name)", value=st.session_state.get("c_first", ""))
        with c1b: c_middle = st.text_input("1. Drugie imię/Inicjał", value=st.session_state.get("c_middle", ""))
        
        c2a, c2b = st.columns(2)
        with c2a: c_dob = st.text_input("2. Data ur. (MM/DD/RR)", value=st.session_state.get("c_dob", ""))
        with c2b: c_mem = st.number_input("3. Członkowie rodziny z Tobą", min_value=0, value=st.session_state.get("c_mem", 3))
        
        c_street = st.text_input("4a. Ulica i numer / Hotel w USA", value=st.session_state.get("c_street", ""))
        c4a, c4b = st.columns(2)
        with c4a: c_city = st.text_input("4b. Miasto w USA", value=st.session_state.get("c_city", "Des Moines"))
        with c4b: c_state = st.text_input("4c. Stan", value=st.session_state.get("c_state", "IA"))
        
        c5a, c5b = st.columns(2)
        with c5a: c_pass_country = st.text_input("5. Paszport wydany przez", value=st.session_state.get("c_pass_country", "POLAND"))
        with c5b: c_pass_no = st.text_input("6. Numer paszportu", value=st.session_state.get("c_pass_no", ""))
        
        c_residence = st.text_input("7. Państwo zamieszkania", value=st.session_state.get("c_residence", "POLAND"))
        c_visited = st.text_input("8. Odwiedzone kraje przed przylotem", value=st.session_state.get("c_visited", "NONE"))
        c_fly = st.text_input("9. Linia lotnicza i nr lotu (Airline/Flight)", value=st.session_state.get("c_fly", ""))
        
        st.markdown("---")
        def r_idx(key): return 1 if "Tak" in st.session_state.get(key, "Nie") else 0
        
        c_10 = st.radio("10. Cel podróży to biznes?", ["Nie", "Tak"], index=r_idx("c_10"), horizontal=True)
        c_11a = st.radio("11a. Wwozisz owoce, rośliny, jedzenie?", ["Nie", "Tak"], index=r_idx("c_11a"), horizontal=True)
        c_11b = st.radio("11b. Wwozisz mięso, zwierzęta?", ["Nie", "Tak"], index=r_idx("c_11b"), horizontal=True)
        c_11c = st.radio("11c. Wwozisz czynniki chorobotwórcze?", ["Nie", "Tak"], index=r_idx("c_11c"), horizontal=True)
        c_11d = st.radio("11d. Wwozisz ziemię lub byłeś na farmie?", ["Nie", "Tak"], index=r_idx("c_11d"), horizontal=True)
        c_12 = st.radio("12. Bliski kontakt z żywym inwentarzem?", ["Nie", "Tak"], index=r_idx("c_12"), horizontal=True)
        c_13 = st.radio("13. Przewozisz gotówkę > 10 000 USD?", ["Nie", "Tak"], index=r_idx("c_13"), horizontal=True)
        c_14 = st.radio("14. Przewozisz towary na sprzedaż?", ["Nie", "Tak"], index=r_idx("c_14"), horizontal=True)
        c_15 = st.number_input("15. Wartość prezentów zostawianych w USA [$]", min_value=0, value=st.session_state.get("c_15", 0))

        keys = ['c_last','c_first','c_middle','c_dob','c_mem','c_street','c_city','c_state','c_pass_country','c_pass_no','c_residence','c_visited','c_fly','c_10','c_11a','c_11b','c_11c','c_11d','c_12','c_13','c_14','c_15']
        vals = [c_last,c_first,c_middle,c_dob,c_mem,c_street,c_city,c_state,c_pass_country,c_pass_no,c_residence,c_visited,c_fly,c_10,c_11a,c_11b,c_11c,c_11d,c_12,c_13,c_14,c_15]
        for k, v in zip(keys, vals): st.session_state[k] = v

    with c_card:
        st.markdown("#### 🇺🇸 Gotowa Ściągawka:")
        def yn(val): return "YES (X)" if "Tak" in val else "NO (X)"
        dict_data = {
            'c_last': c_last.upper() if c_last else "", 'c_first': c_first.upper() if c_first else "", 'c_middle': c_middle.upper() if c_middle else "",
            'c_dob': c_dob, 'c_mem': c_mem, 'c_street': c_street.upper() if c_street else "", 'c_city': c_city.upper() if c_city else "", 'c_state': c_state.upper() if c_state else "",
            'c_pass_country': c_pass_country.upper() if c_pass_country else "", 'c_pass_no': c_pass_no.upper() if c_pass_no else "",
            'c_residence': c_residence.upper() if c_residence else "", 'c_visited': c_visited.upper() if c_visited else "", 'c_fly': c_fly.upper() if c_fly else "",
            'c_10': yn(c_10), 'c_11a': yn(c_11a), 'c_11b': yn(c_11b), 'c_11c': yn(c_11c), 'c_11d': yn(c_11d), 'c_12': yn(c_12), 'c_13': yn(c_13), 'c_14': yn(c_14), 'c_15': c_15
        }
        render_customs_card(dict_data)
