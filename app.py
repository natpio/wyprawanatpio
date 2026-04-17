import streamlit as st
import datetime
from data import init_state, save_and_sync, safe_rerun, display_safe_image, get_weather
from ui import apply_custom_css, render_boarding_pass, jetlag_widget, render_customs_card

st.set_page_config(page_title="IOWA '26 | OPERATION HUB 🇺🇸", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

# Inicjalizacja CSS i Bazy Danych
apply_custom_css()
init_state("Plan")
init_state("Zadania", ["Status"])
init_state("Bagaz", ["Spakowane"])
init_state("Grywalizacja", ["Zaliczone"])

# Opcja odświeżania bazy
_, col_sync = st.columns([8, 2])
if col_sync.button("🔄 Wymuś Odświeżenie Chmury", width="stretch"):
    st.cache_data.clear()
    for key in list(st.session_state.keys()):
        if key.startswith("df_"): del st.session_state[key]
    safe_rerun()

# Bilet Lotniczy na samej górze
target_date = datetime.datetime(2026, 6, 30, 8, 0)
render_boarding_pass((target_date - datetime.datetime.now()).days)

if st.session_state.get("show_balloons", False):
    st.balloons()
    st.session_state["show_balloons"] = False

# Główne Zakładki
t1, t2, t3, t4, t5 = st.tabs(["📍 Roadmap", "✅ Checklist", "🧳 Cargo", "🎮 Kids Hub", "🛂 Odprawa"])

# --- ZAKŁADKA 1: ROADMAP ---
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
                ed_p = st.data_editor(df_p, width="stretch", hide_index=True, num_rows="dynamic")
                if st.button("Zapisz Roadmap"):
                    st.session_state["df_Plan"] = ed_p
                    if save_and_sync("Plan"): safe_rerun()
    with c_right:
        display_safe_image("chicago")
        st.write("")
        display_safe_image("desmoines")

# --- ZAKŁADKA 2: CHECKLIST (Z ARCHIWUM) ---
with t2:
    df_z = st.session_state.get("df_Zadania")
    if not df_z.empty:
        done, total = df_z["Status"].sum(), len(df_z)
        st.progress(done/total if total > 0 else 0, text=f"Ukończono: {done}/{total}")
        
        # Filtrowanie danych
        df_todo = df_z[~df_z['Status']]
        df_done = df_z[df_z['Status']]
        
        st.markdown("#### ⏳ Do zrobienia")
        if df_todo.empty:
            st.success("Wszystkie zadania z listy zostały wykonane! 🎉")
        else:
            for i, r in df_todo.iterrows():
                c1, c2 = st.columns([3, 1])
                html_task = f"<div style='background:rgba(255,255,255,0.95); border-left:5px solid #0B2447; border-radius:8px; padding:12px; margin-bottom:8px;'><div style='font-weight:600;'>📝 {r['Zadanie']}</div><span class='route-tag'>{r['Kategoria']}</span></div>"
                c1.markdown(html_task.replace('\n', ''), unsafe_allow_html=True)
                with c2:
                    st.write("")
                    if st.button("ZROBIONE", type="primary", key=f"z_todo_{i}"): 
                        st.session_state["df_Zadania"].at[i, "Status"] = True
                        if save_and_sync("Zadania"): safe_rerun()

        st.write("")
        # Archiwum
        with st.expander(f"🗃️ Archiwum Ukończonych Zadań ({len(df_done)})"):
            for i, r in df_done.iterrows():
                c1, c2 = st.columns([3, 1])
                html_task = f"<div style='background:rgba(40,167,69,0.1); border-left:5px solid #28a745; border-radius:8px; padding:12px; margin-bottom:8px;'><div style='font-weight:600; text-decoration:line-through; opacity:0.6;'>✅ {r['Zadanie']}</div><span class='route-tag'>{r['Kategoria']}</span></div>"
                c1.markdown(html_task.replace('\n', ''), unsafe_allow_html=True)
                with c2:
                    st.write("")
                    if st.button("COFNIJ", key=f"z_done_{i}"): 
                        st.session_state["df_Zadania"].at[i, "Status"] = False
                        if save_and_sync("Zadania"): safe_rerun()

        with st.expander("⚙️ Admin Zadań"):
            ed_z = st.data_editor(df_z, column_config={"Status": st.column_config.CheckboxColumn("OK", width="small")}, hide_index=True, num_rows="dynamic", width="stretch")
            if st.button("Zapisz Edycję Zadań"): 
                st.session_state["df_Zadania"] = ed_z
                if save_and_sync("Zadania"): safe_rerun()

# --- ZAKŁADKA 3: CARGO (Z ARCHIWUM) ---
with t3:
    df_b = st.session_state.get("df_Bagaz")
    if not df_b.empty:
        who = st.multiselect("Bagaż osoby:", options=df_b["Wlasciciel"].unique(), default=df_b["Wlasciciel"].unique())
        filtered = df_b[df_b["Wlasciciel"].isin(who)]
        
        if not filtered.empty: 
            st.progress(filtered["Spakowane"].sum()/len(filtered), text=f"Spakowano: {filtered['Spakowane'].sum()}/{len(filtered)}")
            
            # Filtrowanie na Spakowane i Do Spakowania
            df_to_pack = filtered[~filtered['Spakowane']]
            df_packed = filtered[filtered['Spakowane']]
            
            st.markdown("#### 📦 Do spakowania")
            if df_to_pack.empty:
                st.success("Wszystko spakowane! Walizki można zamykać! 🎒")
            else:
                for i, r in df_to_pack.iterrows():
                    c1, c2 = st.columns([3, 1])
                    html_cargo = f"<div style='background:rgba(255,255,255,0.95); border-left:5px solid #0B2447; border-radius:8px; padding:12px; margin-bottom:8px;'><div style='font-weight:600;'>📦 {r['Przedmiot']}</div><span style='background:#0B2447; color:white; padding:3px 10px; border-radius:20px; font-size:0.7rem;'>{r['Wlasciciel']}</span></div>"
                    c1.markdown(html_cargo.replace('\n', ''), unsafe_allow_html=True)
                    with c2:
                        st.write("")
                        if st.button("DO WALIZKI", type="primary", key=f"b_topack_{i}"): 
                            st.session_state["df_Bagaz"].at[i, "Spakowane"] = True
                            if save_and_sync("Bagaz"): safe_rerun()

            st.write("")
            # Archiwum spakowanych
            with st.expander(f"🎒 Spakowane ({len(df_packed)})"):
                for i, r in df_packed.iterrows():
                    c1, c2 = st.columns([3, 1])
                    html_cargo = f"<div style='background:rgba(40,167,69,0.1); border-left:5px solid #28a745; border-radius:8px; padding:12px; margin-bottom:8px;'><div style='font-weight:600; text-decoration:line-through; opacity:0.6;'>✅ {r['Przedmiot']}</div><span style='background:#0B2447; color:white; padding:3px 10px; border-radius:20px; font-size:0.7rem;'>{r['Wlasciciel']}</span></div>"
                    c1.markdown(html_cargo.replace('\n', ''), unsafe_allow_html=True)
                    with c2:
                        st.write("")
                        if st.button("WYPAKUJ", key=f"b_packed_{i}"): 
                            st.session_state["df_Bagaz"].at[i, "Spakowane"] = False
                            if save_and_sync("Bagaz"): safe_rerun()

        with st.expander("⚙️ Admin Bagażu"):
            ed_b = st.data_editor(df_b, column_config={"Spakowane": st.column_config.CheckboxColumn("OK", width="small")}, hide_index=True, num_rows="dynamic", width="stretch")
            if st.button("Zapisz Edycję Bagażu"): 
                st.session_state["df_Bagaz"] = ed_b
                if save_and_sync("Bagaz"): safe_rerun()

# --- ZAKŁADKA 4: KIDS HUB (Z ARCHIWUM) ---
with t4:
    df_g = st.session_state.get("df_Grywalizacja")
    if not df_g.empty:
        score, max_s = df_g[df_g["Zaliczone"]]["Punkty_do_zdobycia"].sum(), df_g["Punkty_do_zdobycia"].sum()
        st.metric("Zebrane Diamenty", f"{score} / {max_s} 💎")
        st.progress(score/max_s if max_s > 0 else 0)
        
        df_g_todo = df_g[~df_g['Zaliczone']]
        df_g_done = df_g[df_g['Zaliczone']]
        
        st.markdown("#### 🎯 Bieżące Misje")
        if df_g_todo.empty:
            st.success("Wszystkie misje wykonane! Jesteście super podróżnikami! 🏆")
        else:
            for i, r in df_g_todo.iterrows():
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"<div style='background:rgba(255,255,255,0.95); border-left:4px solid #FFC72C; padding:10px; margin-bottom:5px; border-radius:8px;'>⭐️ <strong style='color:#0f2027;'>{r['Etap']}</strong> <span style='color: #0B2447; font-weight: bold;'> (+{r['Punkty_do_zdobycia']} 💎)</span></div>", unsafe_allow_html=True)
                with c2:
                    if st.button("ZROBIONE!", type="primary", key=f"g_todo_{i}"): 
                        st.session_state["df_Grywalizacja"].at[i, "Zaliczone"] = True
                        st.session_state["show_balloons"] = True
                        if save_and_sync("Grywalizacja"): safe_rerun()

        st.write("")
        # Archiwum misji
        with st.expander(f"🏆 Zdobyte Trofea ({len(df_g_done)})"):
            for i, r in df_g_done.iterrows():
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"<div style='background:rgba(40,167,69,0.1); border-left:4px solid #28a745; padding:10px; margin-bottom:5px; border-radius:8px; opacity:0.7;'><strong style='color:#28a745;'>✅ {r['Etap']}</strong></div>", unsafe_allow_html=True)
                with c2:
                    if st.button("COFNIJ", key=f"g_done_{i}"): 
                        st.session_state["df_Grywalizacja"].at[i, "Zaliczone"] = False
                        if save_and_sync("Grywalizacja"): safe_rerun()

        with st.expander("⚙️ Admin Gry"):
            ed_g = st.data_editor(df_g, column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)}, hide_index=True, num_rows="dynamic", width="stretch")
            if st.button("Zapisz Edycję Gry"): 
                st.session_state["df_Grywalizacja"] = ed_g
                if save_and_sync("Grywalizacja"): safe_rerun()

# --- ZAKŁADKA 5: ODPRAWA CELNA ---
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
