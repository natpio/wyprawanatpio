import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
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
                st.error(f"⚠️ Plik {file_path} jest uszkodzony. Wgraj go ponownie na GitHuba.")
                return
    st.info(f"💡 [Brak grafiki] Wgraj plik '{filename_base}.png' lub '.jpg' do repozytorium.")

def apply_custom_css():
    mapa_b64 = get_base64_of_bin_file("mapa.png") or get_base64_of_bin_file("mapa.jpg")
    
    if mapa_b64:
        bg_css = f'background-image: linear-gradient(rgba(248, 249, 250, 0.88), rgba(248, 249, 250, 0.88)), url("data:image/png;base64,{mapa_b64}");'
    else:
        bg_css = 'background-color: #f8f9fa; background-image: linear-gradient(135deg, rgba(244, 0, 0, 0.05) 0%, rgba(255, 199, 44, 0.05) 100%), radial-gradient(#d3dce6 1px, transparent 1px);'

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
    .c-num {{ font-weight: 800; color: #0284c7; margin-right: 5px; }}
    .c-ans {{ font-weight: 800; color: #C62828; text-transform: uppercase; border-bottom: 1px dashed #C62828; }}

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

def render_boarding_pass(days_left):
    html = f"""
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
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)

def jetlag_widget(city, flag, weather, timezone, subtitle, border_color):
    html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Open+Sans:wght@400;600;800&display=swap');
    body {{ margin: 0; padding: 0; background: transparent; }}
    .card {{ background: rgba(255, 255, 255, 0.95); border-radius: 12px; padding: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid {border_color}; font-family: 'Open Sans', sans-serif; box-sizing: border-box; height: 100%; }}
    .city {{ font-weight: 800; font-size: 1.1rem; color: #0B2447; margin-bottom: 5px; text-transform: uppercase; }}
    .weather {{ font-size: 1.4rem; color: #C62828; font-weight: 800; margin-bottom: 5px; }}
    .clock {{ font-family: 'Anton', sans-serif; font-size: 2.5rem; color: #0B2447; line-height: 1.2; margin-bottom: 5px; }}
    .sub {{ font-size: 0.75rem; color: #64748b; font-weight: 800; text-transform: uppercase; }}
    </style>
    <div class="card">
        <div class="city">{flag} {city}</div>
        <div class="weather">{weather}</div>
        <div class="clock" id="clock_{city.replace(' ','')}">--:--:--</div>
        <div class="sub">{subtitle}</div>
    </div>
    <script>
    function updateTime_{city.replace(' ','')}() {{
        const now = new Date();
        const opts = {{ hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }};
        document.getElementById('clock_{city.replace(' ','')}').innerText = now.toLocaleTimeString('en-GB', {{timeZone: '{timezone}', ...opts}});
    }}
    setInterval(updateTime_{city.replace(' ','')}, 1000);
    updateTime_{city.replace(' ','')}();
    </script>
    """
    components.html(html, height=175)

def render_customs_card(d):
    html = f"""
    <div class="customs-card">
        <h3 class="customs-title">CUSTOMS DECLARATION</h3>
        <div class="customs-sub">CBP Form 6059B (Cheat Sheet)</div>
        <div class="customs-line"><span class="c-num">1.</span> Family Name, First Name: <span class="c-ans">{d['c_last']} {d['c_first']}</span></div>
        <div class="customs-line"><span class="c-num">2.</span> Birth date (MM/DD/YY): <span class="c-ans">{d['c_dob']}</span></div>
        <div class="customs-line"><span class="c-num">3.</span> Number of family members traveling with you: <span class="c-ans">{d['c_mem']}</span></div>
        <div class="customs-line"><span class="c-num">4.</span> U.S. Street Address / Hotel: <span class="c-ans">{d['c_street']} {d['c_city']} {d['c_state']}</span></div>
        <div class="customs-line"><span class="c-num">5-6.</span> Passport issued by / Number: <span class="c-ans">{d['c_pass_country']} {d['c_pass_no']}</span></div>
        <div class="customs-line"><span class="c-num">7.</span> Country of Residence: <span class="c-ans">{d['c_residence']}</span></div>
        <div class="customs-line"><span class="c-num">8.</span> Countries visited on this trip prior to U.S. arrival: <span class="c-ans">{d['c_visited']}</span></div>
        <div class="customs-line"><span class="c-num">9.</span> Airline/Flight No.: <span class="c-ans">{d['c_fly']}</span></div>
        <div class="customs-line"><span class="c-num">10.</span> The primary purpose of this trip is business: <span class="c-ans">{d['c_10']}</span></div>
        <div style="margin-top: 15px; font-weight: bold; color: #0284c7; font-size: 0.85rem;">QUESTIONS 11 - 14:</div>
        <div class="customs-line"><span class="c-num">11.</span> Bringing fruits, plants, meats, food? <span class="c-ans">{d['c_11a']}</span></div>
        <div class="customs-line"><span class="c-num">12.</span> Proximity to livestock/farms? <span class="c-ans">{d['c_12']}</span></div>
        <div class="customs-line"><span class="c-num">13.</span> Carrying currency over $10,000 U.S.? <span class="c-ans">{d['c_13']}</span></div>
        <div class="customs-line"><span class="c-num">14.</span> Have commercial merchandise? <span class="c-ans">{d['c_14']}</span></div>
        <div style="margin-top: 15px;">
            <span class="c-num">15.</span> Visitors - total value of all articles that will remain in the U.S.: <span class="c-ans">${d['c_15']}</span>
        </div>
    </div>
    """
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)
