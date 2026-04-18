import streamlit as st
import datetime
from data import init_state, save_and_sync, toggle_status, get_weather
from ui import apply_custom_css, render_boarding_pass, jetlag_widget, display_safe_image, render_customs_card

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="IOWA '26 | OPERATION HUB 🇺🇸", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

apply_custom_css()

for sheet in ["Plan", "Zadania", "Bagaz", "Grywalizacja"]:
    init_state(sheet)

_, col_sync = st.columns([8, 2])
if col_sync.button("🔄 Wymuś Odświeżenie Chmury"):
    st.cache_data.clear()
    for key in list(st.session_state.keys()):
        if key.startswith("df_"): del st.session_state[key]
    st.rerun()

if st.session_state.get("show_balloons", False):
    st.balloons()
    st.session_state["show_balloons"] = False

target_date = datetime.datetime(2026, 6, 30, 8, 0)
days_left = (target_date - datetime.datetime.now()).days
render_boarding_pass(days_left)

st.markdown("### 🌤️ Jet-Lag Planner (Pogoda i Czas Lokalny)")
w1, w2, w3 = st.columns(3)
with w1: jetlag_widget("Poznań", "🇵🇱", get_weather(52.4064, 16.9252), "Europe/Warsaw", "Baza Domowa (CET)", "#0B2447")
with w2: jetlag_widget("Chicago", "🇺🇸", get_weather(41.85, -87.65), "America/Chicago", "-7 Godzin (CDT)", "#FFC72C")
with w3: jetlag_widget("Des Moines", "🌽", get_weather(41.5868, -93.625), "America/Chicago", "-7 Godzin (CDT)", "#C62828")

st.write("")

# --- 2. GŁÓWNE ZAKŁADKI ---
t1, t2, t3, t4, t5 = st.tabs(["📍 Roadmap & Info", "✅ Checklist", "🧳 Cargo", "🎮 Kids Hub", "🛂 Odprawa"])

# ZAKŁADKA 1: PLAN
with t1:
    st.markdown("### 🗺️ Trasa: Poznań ➡️ Chicago ➡️ Des Moines")
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.markdown("#### Harmonogram")
        df_p = st.session_state.get("df_Plan")
        if df_p is not None and not df_p.empty:
            for _, r in df_p.iterrows():
                card_html = f"""<div class="route-card"><div class="route-date">{r['Dzien']}</div><div style="width: 100%;"><div class="route-tag">{r['Etap']}</div><p style="margin:0; font-weight:600;">{r['Opis']}</p></div></div>"""
                st.markdown(card_html.replace('\n', ''), unsafe_allow_html=True)
            
            with st.expander("⚙️ Tryb Edycji Harmonogramu"):
                ed_p = st.data_editor(df_p, use_container_width=True, hide_index=True, num_rows="dynamic")
                if st.button("Zapisz Roadmap"):
                    st.session_state["df_Plan"] = ed_p
                    save_and_sync("Plan")
                    st.rerun()

    with c_right:
        st.markdown("#### Punkty Orientacyjne")
        display_safe_image("chicago")
        st.write("")
        display_safe_image("desmoines")

# ZAKŁADKA 2: ZADANIA
with t2:
    st.markdown("### ✅ Pre-Departure Checklist")
    df_z = st.session_state.get("df_Zadania")
    if df_z is not None and not df_z.empty:
        done = df_z['Status'].sum()
        total = len(df_z)
        st.progress(done / total if total > 0 else 0, text=f"Ukończono: {done}/{total}")
        st.write("")
        
        df_todo = df_z[df_z['Status'] == False]
        df_done = df_z[df_z['Status'] == True]
        
        st.markdown("#### ⏳ Do zrobienia")
        if df_todo.empty:
            st.success("Wszystkie zadania wykonane! 🎉")
        else:
            for i, r in df_todo.iterrows():
                c1, c2 = st.columns([3, 1])
                # TWÓJ ORYGINALNY WYGLĄD:
                html_task = f"<div style='background: rgba(255,255,255,0.95); border-left: 5px solid #0B2447; border-radius: 8px; padding: 12px 15px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><div style='font-weight:600; margin-bottom: 5px;'>📝 {r['Zadanie']}</div><span class='route-tag'>{r['Kategoria']}</span></div>"
                c1.markdown(html_task.replace('\n', ''), unsafe_allow_html=True)
                with c2:
                    st.write("")
                    st.button("ZROBIONE!", type="primary", key=f"z_todo_{i}", on_click=toggle_status, args=("Zadania", i, "Status"))

        st.write("")
        with st.expander(f"🗃️ Archiwum Ukończonych Zadań ({len(df_done)})"):
            for i, r in df_done.iterrows():
                c1, c2 = st.columns([3, 1])
                # TWÓJ ORYGINALNY WYGLĄD:
                html_task = f"<div style='background: rgba(40, 167, 69, 0.1); border-left: 5px solid #28a745; border-radius: 8px; padding: 12px 15px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-decoration: line-through; opacity: 0.6;'><div style='font-weight:600; margin-bottom: 5px;'>✅ {r['Zadanie']}</div><span class='route-tag'>{r['Kategoria']}</span></div>"
                c1.markdown(html_task.replace('\n', ''), unsafe_allow_html=True)
                with c2:
                    st.write("")
                    st.button("COFNIJ", key=f"z_done_{i}", on_click=toggle_status, args=("Zadania", i, "Status"))

        st.write("")
        with st.expander("⚙️ Tryb Edycji (Admin)"):
            ed_z = st.data_editor(df_z, column_config={"Status": st.column_config.CheckboxColumn("OK", width="small")}, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("Zapisz Zmiany"):
                st.session_state["df_Zadania"] = ed_z
                save_and_sync("Zadania")
                st.rerun()

# ZAKŁADKA 3: BAGAŻE
with t3:
    st.markdown("### 🧳 Cargo Manifest")
    df_b = st.session_state.get("df_Bagaz")
    if df_b is not None and not df_b.empty:
        who = st.multiselect("Pokaż bagaż osoby:", options=df_b["Wlasciciel"].unique(), default=df_b["Wlasciciel"].unique())
        filtered = df_b[df_b["Wlasciciel"].isin(who)]
        
        if not filtered.empty:
            done_b = filtered["Spakowane"].sum()
            total_b = len(filtered)
            st.progress(done_b / total_b, text=f"Spakowano: {done_b}/{total_b} rzeczy")
            st.write("")
            
            df_to_pack = filtered[filtered['Spakowane'] == False]
            df_packed = filtered[filtered['Spakowane'] == True]
            
            st.markdown("#### 📦 Do spakowania")
            if df_to_pack.empty: st.success("Walizki gotowe do drogi! 🎒")
            for i, r in df_to_pack.iterrows():
                c1, c2 = st.columns([3, 1])
                # TWÓJ ORYGINALNY WYGLĄD:
                html_cargo = f"<div style='background: rgba(255,255,255,0.95); border-left: 5px solid #0B2447; border-radius: 8px; padding: 12px 15px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><div style='font-weight:600; margin-bottom: 5px;'>📦 {r['Przedmiot']}</div><span style='background: #0B2447; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;'>{r['Wlasciciel']}</span></div>"
                c1.markdown(html_cargo.replace('\n', ''), unsafe_allow_html=True)
                with c2:
                    st.write("")
                    st.button("DO WALIZKI", type="primary", key=f"b_topack_{i}", on_click=toggle_status, args=("Bagaz", i, "Spakowane"))

            st.write("")
            with st.expander(f"🎒 Spakowane ({len(df_packed)})"):
                for i, r in df_packed.iterrows():
                    c1, c2 = st.columns([3, 1])
                    # TWÓJ ORYGINALNY WYGLĄD:
                    html_cargo = f"<div style='background: rgba(40, 167, 69, 0.1); border-left: 5px solid #28a745; border-radius: 8px; padding: 12px 15px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-decoration: line-through; opacity: 0.6;'><div style='font-weight:600; margin-bottom: 5px;'>🎒 {r['Przedmiot']}</div><span style='background: #0B2447; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;'>{r['Wlasciciel']}</span></div>"
                    c1.markdown(html_cargo.replace('\n', ''), unsafe_allow_html=True)
                    with c2:
                        st.write("")
                        st.button("WYPAKUJ", key=f"b_packed_{i}", on_click=toggle_status, args=("Bagaz", i, "Spakowane"))
            
            st.write("")
            with st.expander("⚙️ Edycja Bagażu"):
                ed_b = st.data_editor(df_b, column_config={"Spakowane": st.column_config.CheckboxColumn("OK", width="small")}, use_container_width=True, hide_index=True, num_rows="dynamic")
                if st.button("Zapisz Bagaż"):
                    st.session_state["df_Bagaz"] = ed_b
                    save_and_sync("Bagaz")
                    st.rerun()

# ZAKŁADKA 4: DZIECI
with t4:
    st.markdown("### 🎮 Kids Hub")
    df_g = st.session_state.get("df_Grywalizacja")
    if df_g is not None and not df_g.empty:
        score = df_g[df_g["Zaliczone"] == True]["Punkty_do_zdobycia"].sum()
        max_s = df_g["Punkty_do_zdobycia"].sum()
        st.metric("Zebrane Diamenty", f"{score} / {max_s} 💎")
        if max_s > 0: st.progress(score / max_s)
        st.divider()
        
        df_todo = df_g[df_g['Zaliczone'] == False]
        df_done = df_g[df_g['Zaliczone'] == True]
        
        if df_todo.empty: st.success("Wszystkie misje wykonane! 🏆")
        for i, r in df_todo.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"<div style='background-color: rgba(255,255,255,0.95); border-left: 4px solid #FFC72C; border-radius: 8px; padding: 10px 15px; margin-bottom: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>⭐️ <strong>{r['Etap']}</strong> <span style='color: #0B2447; font-weight: bold;'> (+{r['Punkty_do_zdobycia']} 💎)</span></div>", unsafe_allow_html=True)
            with c2:
                st.button("ZROBIONE!", type="primary", key=f"g_todo_{i}", on_click=toggle_status, args=("Grywalizacja", i, "Zaliczone"))
        
        st.write("")
        with st.expander(f"🏆 Pokoik Trofeów ({len(df_done)})"):
            for i, r in df_done.iterrows():
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"<div style='background-color: rgba(40,167,69,0.1); border-left: 4px solid #28a745; border-radius: 8px; padding: 10px 15px; margin-bottom: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); opacity: 0.8;'><strong style='color:#28a745;'>✅ {r['Etap']}</strong></div>", unsafe_allow_html=True)
                with c2:
                    st.button("COFNIJ", key=f"g_done_{i}", on_click=toggle_status, args=("Grywalizacja", i, "Zaliczone"))
        
        with st.expander("⚙️ Tryb Rodzica"):
            ed_g = st.data_editor(df_g, column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)}, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("Zapisz zasady gry"):
                st.session_state["df_Grywalizacja"] = ed_g
                save_and_sync("Grywalizacja")
                st.rerun()

# ZAKŁADKA 5: ODPRAWA CELNA
with t5:
    st.markdown("### 🛂 Generator Deklaracji Celnej (CBP Form 6059B)")
    c_form, c_card = st.columns([1, 1.2])
    with c_form:
        st.markdown("#### 📝 Wprowadź dane:")
        c_last = st.text_input("1. Nazwisko (Family Name)", value=st.session_state.get("c_last", "KOWALSKI"))
        c_first = st.text_input("1. Imię (First Name)", value=st.session_state.get("c_first", "JAN"))
        c_dob = st.text_input("2. Data urodzenia (MM/DD/RRRR)", value=st.session_state.get("c_dob", "01/01/1980"))
        c_mem = st.number_input("3. Liczba członków rodziny z Tobą", min_value=0, value=st.session_state.get("c_mem", 3))
        c_street = st.text_input("4a. Ulica, nr, hotel", value=st.session_state.get("c_street", "123 Main St"))
        c_city = st.text_input("4b. Miasto", value=st.session_state.get("c_city", "Des Moines"))
        c_state = st.text_input("4c. Stan", value=st.session_state.get("c_state", "IA"))
        c_pass_country = st.text_input("5. Wydanie paszportu", value=st.session_state.get("c_pass_country", "POLAND"))
        c_pass_no = st.text_input("6. Nr Paszportu", value=st.session_state.get("c_pass_no", "EA1234567"))
        c_residence = st.text_input("7. Państwo zamieszkania", value=st.session_state.get("c_residence", "POLAND"))
        c_visited = st.text_input("8. Odwiedzone kraje", value=st.session_state.get("c_visited", "NONE"))
        c_fly = st.text_input("9. Lot", value=st.session_state.get("c_fly", "LH 430"))
        c_15 = st.number_input("15. Wartość pozostawianych prezentów ($)", min_value=0, value=st.session_state.get("c_15", 0))

        # Zapamiętanie w sesji
        for k, v in zip(["c_last", "c_first", "c_dob", "c_mem", "c_street", "c_city", "c_state", "c_pass_country", "c_pass_no", "c_residence", "c_visited", "c_fly", "c_15"], 
                        [c_last, c_first, c_dob, c_mem, c_street, c_city, c_state, c_pass_country, c_pass_no, c_residence, c_visited, c_fly, c_15]):
            st.session_state[k] = v

    with c_card:
        st.markdown("#### 🇺🇸 Gotowa Ściągawka:")
        dict_data = {
            'c_last': c_last.upper(), 'c_first': c_first.upper(), 'c_middle': "",
            'c_dob': c_dob, 'c_mem': c_mem, 'c_street': c_street.upper(), 'c_city': c_city.upper(), 'c_state': c_state.upper(),
            'c_pass_country': c_pass_country.upper(), 'c_pass_no': c_pass_no.upper(),
            'c_residence': c_residence.upper(), 'c_visited': c_visited.upper(), 'c_fly': c_fly.upper(),
            'c_10': "NO (X)", 'c_11a': "NO (X)", 'c_11b': "NO (X)", 'c_11c': "NO (X)", 'c_11d': "NO (X)", 
            'c_12': "NO (X)", 'c_13': "NO (X)", 'c_14': "NO (X)", 'c_15': c_15
        }
        render_customs_card(dict_data)
