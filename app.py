import streamlit as st
import datetime
from data import init_state, manual_save, toggle_status_callback, get_weather
from ui import apply_custom_css, render_boarding_pass, jetlag_widget, render_customs_card, display_safe_image

st.set_page_config(page_title="IOWA '26 | OPERATION HUB 🇺🇸", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

# --- Inicjalizacja CSS i Bazy Danych ---
apply_custom_css()
init_state("Plan")
init_state("Zadania")
init_state("Bagaz")
init_state("Grywalizacja")

if st.session_state.get("show_balloons", False):
    st.balloons()
    st.session_state["show_balloons"] = False

# --- BOARDING PASS ---
target_date = datetime.datetime(2026, 6, 30, 8, 0)
render_boarding_pass((target_date - datetime.datetime.now()).days)

# --- GŁÓWNE ZAKŁADKI ---
tab_plan, tab_zadania, tab_bagaz, tab_dzieci, tab_celny = st.tabs(["📍 Roadmap & Map", "✅ Checklist", "🧳 Cargo", "🎮 Kids Hub", "🛂 Odprawa"])

# ZAKŁADKA 1: PLAN
with tab_plan:
    st.markdown("### 🌤️ Jet-Lag Planner")
    w1, w2, w3 = st.columns(3)
    with w1: jetlag_widget("Poznań", "🇵🇱", get_weather(52.4064, 16.9252), "Europe/Warsaw", "Baza Domowa", "#0B2447")
    with w2: jetlag_widget("Chicago", "🇺🇸", get_weather(41.85, -87.65), "America/Chicago", "-7 Godzin", "#FFC72C")
    with w3: jetlag_widget("Des Moines", "🌽", get_weather(41.5868, -93.625), "America/Chicago", "-7 Godzin", "#C62828")

    st.markdown("<h3 style='color: #0f2027;'>🗺️ Trasa: Poznań ➡️ Chicago ➡️ Des Moines</h3>", unsafe_allow_html=True)
    display_safe_image("mapa", "Strategiczna Mapa Operacji")
    st.divider()

    col_timeline, col_features = st.columns([2, 1])
    with col_timeline:
        st.markdown("<h4 style='color: #0f2027;'>Harmonogram</h4>", unsafe_allow_html=True)
        df_plan = st.session_state.get("df_Plan")
        if df_plan is not None and not df_plan.empty:
            for index, row in df_plan.iterrows():
                st.markdown(f"""<div class="route-card"><div class="route-date">{row['Dzien']}</div><div><div class="route-tag">{row['Etap']}</div><p style="margin: 0; font-weight: 600; color: #1e293b;">{row['Opis']}</p></div></div>""", unsafe_allow_html=True)
            with st.expander("⚙️ Tryb Edycji Harmonogramu"):
                edited_plan = st.data_editor(df_plan, use_container_width=True, hide_index=True, num_rows="dynamic")
                if st.button("Zapisz Harmonogram"):
                    st.session_state["df_Plan"] = edited_plan
                    manual_save("Plan")
                    st.rerun()

    with col_features:
        st.markdown("<h4 style='color: #0f2027;'>Punkty Orientacyjne</h4>", unsafe_allow_html=True)
        display_safe_image("chicago")
        st.write("")
        display_safe_image("desmoines")

# ZAKŁADKA 2: ZADANIA
with tab_zadania:
    st.markdown("<h3 style='color: #0f2027;'>Pre-Departure Checklist</h3>", unsafe_allow_html=True)
    df_zadania = st.session_state.get("df_Zadania")
    if df_zadania is not None and not df_zadania.empty:
        zrobione = df_zadania['Status'].sum()
        wszystkie = len(df_zadania)
        st.progress(zrobione / wszystkie if wszystkie > 0 else 0, text=f"STATUS: {zrobione}/{wszystkie} ukończonych zadań")
        st.write("")
        
        for i, r in df_zadania.iterrows():
            c1, c2 = st.columns([3, 1])
            is_done = r['Status']
            
            if is_done:
                bg, border, strike, icon = "rgba(40,167,69,0.1)", "#28a745", "text-decoration:line-through; opacity:0.6;", "✅"
            else:
                bg, border, strike, icon = "rgba(255,255,255,0.95)", "#0B2447", "", "📝"
                
            html_task = f"<div style='background:{bg}; border-left:5px solid {border}; border-radius:8px; padding:12px; margin-bottom:8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><div style='font-weight:600; {strike}; margin-bottom:5px; color:#0f2027;'>{icon} {r['Zadanie']}</div><span class='route-tag'>{r['Kategoria']}</span></div>"
            c1.markdown(html_task.replace('\n', ''), unsafe_allow_html=True)
            
            with c2:
                st.write("")
                if is_done:
                    st.button("COFNIJ", key=f"z_{i}", on_click=toggle_status_callback, args=("Zadania", i, "Status", is_done))
                else:
                    st.button("ZROBIONE", type="primary", key=f"z_{i}", on_click=toggle_status_callback, args=("Zadania", i, "Status", is_done))

        st.write("")
        with st.expander("⚙️ Admin - Edycja Tabeli Zadań"):
            edited_tasks = st.data_editor(df_zadania, column_config={"Status": st.column_config.CheckboxColumn("Wykonane?", width="small")}, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("Zapisz Aktualizacje Zadań"):
                st.session_state["df_Zadania"] = edited_tasks
                manual_save("Zadania")
                st.rerun()

# ZAKŁADKA 3: BAGAŻ
with tab_bagaz:
    st.markdown("<h3 style='color: #0f2027;'>Bagaż Family Cargo Manifest</h3>", unsafe_allow_html=True)
    df_bagaz = st.session_state.get("df_Bagaz")
    if df_bagaz is not None and not df_bagaz.empty:
        kategorie = st.multiselect("Bagaż kogo pakujemy?", options=df_bagaz["Wlasciciel"].unique(), default=df_bagaz["Wlasciciel"].unique())
        filtered_bagaz = df_bagaz[df_bagaz["Wlasciciel"].isin(kategorie)]
        
        if len(filtered_bagaz) > 0:
            st.progress(filtered_bagaz["Spakowane"].sum() / len(filtered_bagaz), text=f"Spakowano: {filtered_bagaz['Spakowane'].sum()}/{len(filtered_bagaz)}")
        
        for i, r in filtered_bagaz.iterrows():
            c1, c2 = st.columns([3, 1])
            is_packed = r['Spakowane']
            
            if is_packed:
                bg, border, strike, icon = "rgba(40,167,69,0.1)", "#28a745", "text-decoration:line-through; opacity:0.6;", "🎒"
            else:
                bg, border, strike, icon = "rgba(255,255,255,0.95)", "#0B2447", "", "📦"
                
            html_cargo = f"<div style='background:{bg}; border-left:5px solid {border}; border-radius:8px; padding:12px; margin-bottom:8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'><div style='font-weight:600; {strike}; margin-bottom:5px; color:#0f2027;'>{icon} {r['Przedmiot']}</div><span style='background:#0B2447; color:white; padding:3px 10px; border-radius:20px; font-size:0.7rem; font-weight:800;'>{r['Wlasciciel']}</span></div>"
            c1.markdown(html_cargo.replace('\n', ''), unsafe_allow_html=True)
            
            with c2:
                st.write("")
                if is_packed:
                    st.button("WYPAKUJ", key=f"b_{i}", on_click=toggle_status_callback, args=("Bagaz", i, "Spakowane", is_packed))
                else:
                    st.button("DO WALIZKI", type="primary", key=f"b_{i}", on_click=toggle_status_callback, args=("Bagaz", i, "Spakowane", is_packed))
        
        st.write("")
        with st.expander("⚙️ Admin - Edycja Tabeli Bagażu"):
            edited_bagaz = st.data_editor(df_bagaz, column_config={"Spakowane": st.column_config.CheckboxColumn("W walizce?", width="small")}, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("Zapisz Aktualizacje Bagażu"):
                st.session_state["df_Bagaz"] = edited_bagaz
                manual_save("Bagaz")
                st.rerun()

# ZAKŁADKA 4: DZIECI
with tab_dzieci:
    st.markdown("<h3 style='color: #0f2027;'>🎮 Kids Hub (Mission Log)</h3>", unsafe_allow_html=True)
    df_gry = st.session_state.get("df_Grywalizacja")
    if df_gry is not None and not df_gry.empty:
        suma_punktow = df_gry[df_gry['Zaliczone'] == True]['Punkty_do_zdobycia'].sum()
        max_punktow = df_gry['Punkty_do_zdobycia'].sum()
        
        st.metric("Zebrane Punkty / Cel", f"{suma_punktow} / {max_punktow} 💎")
        if max_punktow > 0: st.progress(int((suma_punktow / max_punktow) * 100))
        st.divider()
        
        for i, row in df_gry.iterrows():
            c1, c2 = st.columns([3, 1])
            is_zaliczone = row['Zaliczone']
            
            c1.markdown(f"<div style='background-color: rgba(255,255,255,0.95); border-left: 4px solid #FFC72C; border-radius: 8px; padding: 12px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>⭐️ <strong style='color:#0f2027;'>{row['Etap']}</strong> <span style='color: #C62828; font-weight: bold;'> (+{row['Punkty_do_zdobycia']} 💎)</span></div>", unsafe_allow_html=True)
            
            with c2:
                st.write("")
                if is_zaliczone:
                    st.markdown("<div style='padding: 10px; color: #28a745; font-weight: 800;'>✅ ZALICZONE</div>", unsafe_allow_html=True)
                else:
                    st.button("ZROBIONE!", type="primary", key=f"g_{i}", on_click=toggle_status_callback, args=("Grywalizacja", i, "Zaliczone", is_zaliczone))

        st.write("")
        with st.expander("⚙️ Admin - Tryb Rodzica"):
            edited_gry = st.data_editor(df_gry, column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)}, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("Zapisz zasady gry"):
                st.session_state["df_Grywalizacja"] = edited_gry
                manual_save("Grywalizacja")
                st.rerun()

# ZAKŁADKA 5: CELNY
with tab_celny:
    st.info("💡 Formularz celny wypełnia się **JEDEN na całą rodzinę**. Wpisz dane poniżej, a po prawej wygeneruje się ściągawka gotowa do szybkiego przepisania w samolocie.")
    
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
        c_fly = st.text_input("9. Linia lotnicza i nr lotu", value=st.session_state.get("c_fly", ""))
        
        st.markdown("---")
        def r_idx(key): return 1 if "Tak" in st.session_state.get(key, "Nie") else 0
        
        c_10 = st.radio("10. Cel podróży to biznes?", ["Nie", "Tak"], index=r_idx("c_10"), horizontal=True)
        c_11a = st.radio("11a. Wwozisz owoce, jedzenie?", ["Nie", "Tak"], index=r_idx("c_11a"), horizontal=True)
        c_11b = st.radio("11b. Wwozisz mięso?", ["Nie", "Tak"], index=r_idx("c_11b"), horizontal=True)
        c_11c = st.radio("11c. Wwozisz czynniki chorobotwórcze?", ["Nie", "Tak"], index=r_idx("c_11c"), horizontal=True)
        c_11d = st.radio("11d. Byłeś na farmie?", ["Nie", "Tak"], index=r_idx("c_11d"), horizontal=True)
        c_12 = st.radio("12. Bliski kontakt z żywym inwentarzem?", ["Nie", "Tak"], index=r_idx("c_12"), horizontal=True)
        c_13 = st.radio("13. Gotówka > 10 000 USD?", ["Nie", "Tak"], index=r_idx("c_13"), horizontal=True)
        c_14 = st.radio("14. Towary na sprzedaż?", ["Nie", "Tak"], index=r_idx("c_14"), horizontal=True)
        c_15 = st.number_input("15. Wartość prezentów w USA [$]", min_value=0, value=st.session_state.get("c_15", 0))

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
