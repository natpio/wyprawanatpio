import streamlit as st
import base64
import os
import datetime
from PIL import Image, ImageFile

# Nowoczesna biblioteka do stref czasowych (z wbudowanym zabezpieczeniem dla starszych serwerów)
try:
    from zoneinfo import ZoneInfo
except ImportError:
    import pytz as ZoneInfo

ImageFile.LOAD_TRUNCATED_IMAGES = True

def get_base64_of_bin_file(bin_file):
    """Pomocnicza funkcja do ładowania obrazków w tle CSS"""
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def apply_custom_css():
    """Wstrzykuje tło z mapy oraz całą architekturę graficzną"""
    mapa_b64 = get_base64_of_bin_file("mapa.png") or get_base64_of_bin_file("mapa.jpg")
    
    if mapa_b64:
        bg_css = f'background-image: linear-gradient(rgba(248, 249, 250, 0.88), rgba(248, 249, 250, 0.88)), url("data:image/png;base64,{mapa_b64}");'
    else:
        bg_css = 'background-color: #f8f9fa; background-image: linear-gradient(135deg, rgba(244, 0, 0, 0.05) 0%, rgba(255, 199, 44, 0.05) 100%), radial-gradient(#d3dce6 1px, transparent 1px);'
    
    css = f"""
    <style>
    /* Ukrywanie zbędnych elementów interfejsu Streamlit */
    header[data-testid="stHeader"] {{ visibility: hidden; display: none; }}
    div[data-testid="stHeader"] {{ visibility: hidden; display: none; }}
    footer {{ visibility: hidden; display: none; }}
    #MainMenu {{ visibility: hidden; display: none; }}
    section[data-testid="stSidebar"] {{ display: none; }} 
    
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Open+Sans:wght@400;600;800&display=swap');
    
    .stApp {{ {bg_css} background-size: cover; background-attachment: fixed; font-family: 'Open Sans', sans-serif !important; }}
    
    /* STYLE BILETU LOTNICZEGO */
    .boarding-pass-wrapper {{ display: flex; justify-content: center; margin-top: 10px; margin-bottom: 30px; }}
    .ticket {{ display: flex; background: #ffffff; border-radius: 16px; box-shadow: 0 15px 35px rgba(0,0,0,0.15); overflow: hidden; width: 100%; max-width: 1100px; border: 1px solid #e2e8f0; }}
    .ticket-left {{ flex: 3; border-right: 3px dashed #cbd5e1; padding: 20px; }}
    .ticket-header {{ background-color: #0B2447; color: #FFC72C; padding: 15px; font-family: 'Anton', sans-serif; font-size: 1.5rem; display: flex; justify-content: space-between; align-items: center; margin: -20px -20px 20px -20px; }}
    
    /* STYLE ZAKŁADEK I KART HARMONOGRAMU */
    .route-card {{ background: white; border-radius: 12px; padding: 15px; margin-bottom: 10px; border-left: 6px solid #C62828; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    .route-date {{ font-family: 'Anton', sans-serif; font-size: 1.2rem; color: #0B2447; }}
    .route-tag {{ background: #FFC72C; color: #0B2447; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; }}
    
    /* STYLE ZEGARÓW POGODOWYCH */
    .clock-container {{ background: rgba(255, 255, 255, 0.95); border-radius: 12px; padding: 10px; text-align: center; border-top: 4px solid #0B2447; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    .clock-time {{ font-family: 'Anton', sans-serif; font-size: 2rem; color: #0B2447; }}
    
    /* STYLE FORMULARZA CELNEGO */
    .customs-card {{ background-color: #e0f2fe; border: 2px solid #0284c7; border-radius: 12px; padding: 25px; font-family: 'Courier New', Courier, monospace; color: #0f172a; box-shadow: 0 10px 25px rgba(2, 132, 199, 0.15); }}
    .customs-title {{ text-align: center; font-family: 'Anton', sans-serif; color: #0284c7; font-size: 1.8rem; margin-top: 0; margin-bottom: 5px; letter-spacing: 1px; }}
    .customs-sub {{ text-align: center; font-family: 'Open Sans', sans-serif; color: #64748b; font-size: 0.8rem; margin-bottom: 20px; text-transform: uppercase; font-weight: bold; }}
    .customs-line {{ border-bottom: 1px solid #bae6fd; padding-bottom: 8px; margin-bottom: 12px; font-size: 0.95rem; line-height: 1.4; }}
    .c-num {{ font-weight: 800; color: #0284c7; margin-right: 5px; display: inline-block; min-width: 25px; }}
    .c-ans {{ font-weight: 800; color: #C62828; text-transform: uppercase; border-bottom: 1px dashed #C62828; padding-left: 5px; padding-right: 5px; }}
    </style>
    """
    st.markdown(css.replace('\n', ''), unsafe_allow_html=True)

def render_boarding_pass(days):
    """Zgrabny i responsywny bilet lotniczy na górę strony"""
    html = f"""
    <div class="boarding-pass-wrapper">
        <div class="ticket">
            <div class="ticket-left">
                <div class="ticket-header">
                    <span>🇺🇸 OPERATION: IOWA 2026</span>
                </div>
                <div style="text-align: center; font-size: 1.5rem; font-weight: 800; color: #0B2447; margin-top: 20px;">FAMILIA NA POKŁADZIE!</div>
                <div style="text-align: center; color: #C62828; font-family: 'Anton', sans-serif; font-size: 4rem; line-height: 1;">{days} DNI</div>
                <div style="text-align: center; font-weight: 800; text-transform: uppercase; color: #64748b;">Do startu przygody</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)

def jetlag_clock(city, timezone, weather):
    """Generuje kartę zegara ze stabilną (pythonową) godziną lokalną"""
    try:
        now = datetime.datetime.now(ZoneInfo(timezone))
    except Exception:
        now = datetime.datetime.now()
        
    html = f"""
    <div class="clock-container">
        <div style="font-weight: 800; color: #0B2447; font-size: 0.9rem; text-transform: uppercase;">{city}</div>
        <div style="color: #C62828; font-weight: 800; font-size: 1.1rem;">{weather}</div>
        <div class="clock-time">{now.strftime('%H:%M')}</div>
    </div>
    """
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)

def display_safe_image(filename_base, caption=""):
    """Zabezpiecza ładowanie grafik. Jeśli obrazka brakuje - wyświetli ładną podpowiedź."""
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    for ext in extensions:
        file_path = f"{filename_base}{ext}"
        if os.path.exists(file_path):
            try:
                img = Image.open(file_path)
                img.load()
                # Bezpieczne wyświetlanie grafiki pod najnowszego Streamlita
                st.image(img, caption=caption, use_container_width=True)
                return
            except Exception:
                st.error(f"⚠️ Plik {file_path} jest uszkodzony.")
                return
    st.info(f"💡 [Brak grafiki] Wgraj plik '{filename_base}.png' lub '.jpg' do repozytorium.")

def render_customs_card(d):
    """Wierna wizualna kopia formularza celnego (CBP Form 6059B)"""
    html = f"""
    <div class="customs-card">
        <h3 class="customs-title">CUSTOMS DECLARATION</h3>
        <div class="customs-sub">CBP Form 6059B (Cheat Sheet)</div>
        <div class="customs-line"><span class="c-num">1.</span> Family Name: <span class="c-ans">{d.get('c_last', '')}</span> | First: <span class="c-ans">{d.get('c_first', '')}</span> | Middle: <span class="c-ans">{d.get('c_middle', '')}</span></div>
        <div class="customs-line"><span class="c-num">2.</span> Birth date (MM/DD/YY): <span class="c-ans">{d.get('c_dob', '')}</span></div>
        <div class="customs-line"><span class="c-num">3.</span> Number of family members traveling with you: <span class="c-ans">{d.get('c_mem', '')}</span></div>
        <div class="customs-line"><span class="c-num">4.</span> (a) U.S. Street Address: <span class="c-ans">{d.get('c_street', '')}</span></div>
        <div class="customs-line">&nbsp;&nbsp;&nbsp;(b) City: <span class="c-ans">{d.get('c_city', '')}</span> &nbsp;&nbsp;(c) State: <span class="c-ans">{d.get('c_state', '')}</span></div>
        <div class="customs-line"><span class="c-num">5.</span> Passport issued by: <span class="c-ans">{d.get('c_pass_country', '')}</span></div>
        <div class="customs-line"><span class="c-num">6.</span> Passport number: <span class="c-ans">{d.get('c_pass_no', '')}</span></div>
        <div class="customs-line"><span class="c-num">7.</span> Country of Residence: <span class="c-ans">{d.get('c_residence', '')}</span></div>
        <div class="customs-line"><span class="c-num">8.</span> Countries visited on this trip prior to U.S. arrival: <span class="c-ans">{d.get('c_visited', '')}</span></div>
        <div class="customs-line"><span class="c-num">9.</span> Airline/Flight No.: <span class="c-ans">{d.get('c_fly', '')}</span></div>
        <div class="customs-line"><span class="c-num">10.</span> The primary purpose of this trip is business: <span class="c-ans">{d.get('c_10', 'NO (X)')}</span></div>
        <div style="margin-top: 15px; font-weight: bold; color: #0284c7; font-size: 0.85rem;">11. I am (We are) bringing:</div>
        <div class="customs-line">&nbsp;&nbsp;(a) fruits, vegetables, plants, seeds, food, insects: <span class="c-ans">{d.get('c_11a', 'NO (X)')}</span></div>
        <div class="customs-line">&nbsp;&nbsp;(b) meats, animals, animal/wildlife products: <span class="c-ans">{d.get('c_11b', 'NO (X)')}</span></div>
        <div class="customs-line">&nbsp;&nbsp;(c) disease agents, cell cultures, snails: <span class="c-ans">{d.get('c_11c', 'NO (X)')}</span></div>
        <div class="customs-line">&nbsp;&nbsp;(d) soil or have been on a farm/ranch/pasture: <span class="c-ans">{d.get('c_11d', 'NO (X)')}</span></div>
        <div class="customs-line"><span class="c-num">12.</span> I have (We have) been in close proximity of livestock: <span class="c-ans">{d.get('c_12', 'NO (X)')}</span></div>
        <div class="customs-line"><span class="c-num">13.</span> Carrying currency/monetary instruments over $10,000 U.S.: <span class="c-ans">{d.get('c_13', 'NO (X)')}</span></div>
        <div class="customs-line"><span class="c-num">14.</span> I have (We have) commercial merchandise: <span class="c-ans">{d.get('c_14', 'NO (X)')}</span></div>
        <div style="margin-top: 15px;">
            <span class="c-num">15.</span> Visitors - total value of all articles that will remain in the U.S.: <span class="c-ans">${d.get('c_15', '0')}</span>
        </div>
    </div>
    """
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)
