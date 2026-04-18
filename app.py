import streamlit as st
import datetime

# --- PRAWIDŁOWE IMPORTY Z MODUŁÓW ---
from data import init_state, save_and_sync, toggle_status_callback, get_weather
from ui import apply_custom_css, render_boarding_pass, jetlag_clock, display_safe_image, render_customs_card

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(page_title="IOWA '26 | OPERATION HUB 🇺🇸", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

# Inicjalizacja wyglądu
apply_custom_css()

# Wczytanie danych do pamięci z chmury (zabezpieczone)
for sheet in ["Plan", "Zadania", "Bagaz", "Grywalizacja"]:
    init_state(sheet)

# --- 2. GÓRNY PANEL (ODŚWIEŻANIE) ---
_, col_sync = st.columns([8, 2])
if col_sync.button("🔄 Wymuś Odświeżenie Chmury", use_container_width=True):
    st.cache_data.clear()
    for key in list(st.session_state.keys()):
        if key.startswith("df_"): 
            del st.session_state[key]
    st.rerun()

# Aktywacja balonów (Kids Hub)
if st.session_state.get("show_balloons", False):
    st.balloons()
    st.session_state["show_balloons"] = False

# --- 3. BOARDING PASS ---
target_date = datetime.datetime(2026, 6, 30, 8, 0)
render_boarding_pass((target_date - datetime.datetime.now()).days)

# --- 4. ZEGARY STREFOWE I POGODA ---
st.markdown("### 🌤️ Jet-Lag Planner")
c1, c2, c3 = st.columns(3)
with c1: 
    jetlag_clock("Poznań", "Europe/Warsaw", f"Teraz: {get_weather(52.4, 16.9)}")
with c2: 
    jetlag_clock("Chicago", "America/Chicago", f"Teraz: {get_weather(41.8, -87.6)}")
with c3: 
    jetlag_clock("Des Moines", "America/Chicago", f"Teraz: {get_weather(41.5, -93.6)}")

st.write("")

# --- 5. GŁÓWNE ZAKŁADKI ---
t1, t2, t3, t4, t5 = st.tabs(["📍 Trasa", "✅ Zadania", "🧳 Bagaż", "🎮 Misje", "🛂 Odprawa"])


# ==========================================
# ZAKŁADKA 1: TRASA I PLAN
# ==========================================
with t1:
    st.markdown("### 🗺️ Trasa: Poznań ➡️ Chicago ➡️ Des Moines")
    display_safe_image("mapa", "Strategiczna Mapa Operacji")
    st.divider()

    col_timeline, col_features = st.columns([2, 1])
    with col_timeline:
        st.markdown("#### Harmonogram")
        df_p = st.session_state.get("df_Plan")
        if df_p is not None and not df_p.empty:
            for index, row in df_p.iterrows():
                st.markdown(f"""<div class="route-card"><div class="route-date">{row['Dzien']}</div><div><div class="route-tag">{row['Etap']}</div><p style="margin: 0; font-weight: 600;">{row['Opis']}</p></div></div>""", unsafe_allow_html=True)
            
            with st.expander("⚙️ Tryb Edycji Harmonogramu"):
                ed_p = st.data_editor(df_p, hide_index=True, num_rows="dynamic", use_container_width=True)
                if st.button("Zapisz Harmonogram"):
                    st.session_state["df_Plan"] = ed_p
                    if save_and_sync("Plan"): st.rerun()

    with col_features:
        st.markdown("#### Punkty Orientacyjne")
        display_safe_image("chicago")
        st.write("")
        display_safe_image("desmoines")


# ==========================================
# ZAKŁADKA 2: ZADANIA (ARCHIWUM)
# ==========================================
with t2:
    st.markdown("### ✅ Pre-Departure Checklist")
    df_z = st.session_state.get("df_Zadania")
    if df_z is not None and not df_z.empty:
        done = df_z['Status'].sum()
        total = len(df_z)
        st.progress(done / total if total > 0 else 0, text=f"Ukończono: {done}/{total}")
        
        df_todo = df_z[df_z['Status'] == False]
        df_done = df_z[df_z['Status'] == True]
        
        st.markdown("#### ⏳ Do zrobienia")
        if df_todo.empty:
            st.success("Wszystkie zadania wykonane! 🎉")
        else:
            for i, r in df_todo.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"<div style='background:rgba(255,255,255,0.95); border-left:5px solid #0B2447; border-radius:8px; padding:12px; margin-bottom:8px;'>📝 <strong>{r['Zadanie']}</strong> <span class='route-tag'>{r['Kategoria']}</span></div>", unsafe_allow_html=True)
                with c2:
                    st.write("")
                    # CALLBACK: Akcja dzieje się zanim strona się przeładuje
                    st.button("ZROBIONE", type="primary", key=f"z_todo_{i}", on_click=toggle_status_callback, args=("Zadania", i, "Status"))

        st.write("")
        with st.expander(f"🗃️ Archiwum Ukończonych Zadań ({len(df_done)})"):
            for i, r in df_done.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"<div style='background:rgba(40,167,69,0.1); border-left:5px solid #28a745; border-radius:8px; padding:12px; margin-bottom:8px; opacity:0.7;'><strike>✅ <strong>{r['Zadanie']}</strong></strike> <span class='route-tag'>{r['Kategoria']}</span></div>", unsafe_allow_html=True)
                with c2:
                    st.write("")
                    st.button("COFNIJ", key=f"z_done_{i}", on_click=toggle_status_callback, args=("Zadania", i, "Status"))

        with st.expander("⚙️ Admin Zadań"):
            ed_z = st.data_editor(df_z, column_config={"Status": st.column_config.CheckboxColumn("OK", width="small")}, hide_index=True, num_rows="dynamic", use_container_width=True)
            if st.button("Zapisz Edycję Zadań"): 
                st.session_state["df_Zadania"] = ed_z
                if save_and_sync("Zadania"): st.rerun()


# ==========================================
# ZAKŁADKA 3: BAGAŻ (ARCHIWUM)
# ==========================================
with t3:
    st.markdown("### 🧳 Cargo Manifest")
    df_b = st.session_state.get("df_Bagaz")
    if df_b is not None and not df_b.empty:
        who = st.multiselect("Bagaż kogo pakujemy?", options=df_b["Wlasciciel"].unique(), default=df_b["Wlasciciel"].unique())
        filtered = df_b[df_b["Wlasciciel"].isin(who)]
        
        if not filtered.empty: 
            st.progress(filtered["Spakowane"].sum() / len(filtered), text=f"Spakowano: {filtered['Spakowane'].sum()}/{len(filtered)}")
            
            df_to_pack = filtered[filtered['Spakowane'] == False]
            df_packed = filtered[filtered['Spakowane'] == True]
            
            st.markdown("#### 📦 Do spakowania")
            if df_to_pack.empty:
                st.success("Wszystko spakowane! Walizki można zamykać! 🎒")
            else:
                for i, r in df_to_pack.iterrows():
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"<div style='background:rgba(255,255,255,0.95); border-left:5px solid #0B2447; border-radius:8px; padding:12px; margin-bottom:8px;'>📦 <strong>{r['Przedmiot']}</strong> <span style='background:#0B2447; color:white; padding:3px 10px; border-radius:20px; font-size:0.7rem;'>{r['Wlasciciel']}</span></div>", unsafe_allow_html=True)
                    with c2:
                        st.write("")
                        st.button("DO WALIZKI", type="primary", key=f"b_topack_{i}", on_click=toggle_status_callback, args=("Bagaz", i, "Spakowane"))

            st.write("")
            with st.expander(f"🎒 Spakowane w walizce ({len(df_packed)})"):
                for i, r in df_packed.iterrows():
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"<div style='background:rgba(40,167,69,0.1); border-left:5px solid #28a745; border-radius:8px; padding:12px; margin-bottom:8px; opacity:0.7;'><strike>✅ <strong>{r['Przedmiot']}</strong></strike> <span style='background:#0B2447; color:white; padding:3px 10px; border-radius:20px; font-size:0.7rem;'>{r['Wlasciciel']}</span></div>", unsafe_allow_html=True)
                    with c2:
                        st.write("")
                        st.button("WYPAKUJ", key=f"b_packed_{i}", on_click=toggle_status_callback, args=("Bagaz", i, "Spakowane"))

        with st.expander("⚙️ Admin Bagażu"):
            ed_b = st.data_editor(df_b, column_config={"Spakowane": st.column_config.CheckboxColumn("OK", width="small")}, hide_index=True, num_rows="dynamic", use_container_width=True)
            if st.button("Zapisz Edycję Bagażu"): 
                st.session_state["df_Bagaz"] = ed_b
                if save_and_sync("Bagaz"): st.rerun()


# ==========================================
# ZAKŁADKA 4: KIDS HUB (ARCHIWUM)
# ==========================================
with t4:
    st.markdown("### 🎮 Kids Hub (Mission Log)")
    df_g = st.session_state.get("df_Grywalizacja")
    if df_g is not None and not df_g.empty:
        score = df_g[df_g["Zaliczone"] == True]["Punkty_do_zdobycia"].sum()
        max_s = df_g["Punkty_do_zdobycia"].sum()
        st.metric("Zebrane Diamenty", f"{score} / {max_s} 💎")
        if max_s > 0: st.progress(score / max_s)
        
        df_g_todo = df_g[df_g['Zaliczone'] == False]
        df_g_done = df_g[df_g['Zaliczone'] == True]
        
        st.markdown("#### 🎯 Bieżące Misje")
        if df_g_todo.empty:
            st.success("Wszystkie misje wykonane! Jesteście super podróżnikami! 🏆")
        else:
            for i, r in df_g_todo.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"<div style='background:rgba(255,255,255,0.95); border-left:4px solid #FFC72C; padding:10px; margin-bottom:5px; border-radius:8px;'>⭐️ <strong style='color:#0f2027;'>{r['Etap']}</strong> <span style='color: #0B2447; font-weight: bold;'> (+{r['Punkty_do_zdobycia']} 💎)</span></div>", unsafe_allow_html=True)
                with c2:
                    st.button("ZROBIONE!", type="primary", key=f"g_todo_{i}", on_click=toggle_status_callback, args=("Grywalizacja", i, "Zaliczone"))

        st.write("")
        with st.expander(f"🏆 Zdobyte Trofea ({len(df_g_done)})"):
            for i, r in df_g_done.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"<div style='background:rgba(40,167,69,0.1); border-left:4px solid #28a745; padding:10px; margin-bottom:5px; border-radius:8px; opacity:0.7;'>✅ <strong style='color:#28a745;'>{r['Etap']}</strong></div>", unsafe_allow_html=True)
                with c2:
                    st.button("COFNIJ", key=f"g_done_{i}", on_click=toggle_status_callback, args=("Grywalizacja", i, "Zaliczone"))

        with st.expander("⚙️ Admin Gry"):
            ed_g = st.data_editor(df_g, column_config={"Zaliczone": st.column_config.CheckboxColumn("Zaliczone?", default=False)}, hide_index=True, num_rows="dynamic", use_container_width=True)
            if st.button("Zapisz Edycję Gry"): 
                st.session_state["df_Grywalizacja"] = ed_g
                if save_and_sync("Grywalizacja"): st.rerun()


# ==========================================
# ZAKŁADKA 5: FORMULARZ CELNY
# ==========================================
with t5:
    st.info("💡 F5 wyczyści te pola. Formularz celny wypełnia się **JEDEN na całą rodzinę**.")
    c_form, c_card = st.columns([1, 1.2])
    with c_form:
        c_last = st.text_input("1. Nazwisko (Family Name)", value=st.session_state.get("c_last", ""))
        c1a, c1b = st.columns(2)
        with c1a: c_first = st.text_input("1. Imię (First Name)", value=st.session_state.get("c_first", ""))
        with c1b: c_middle = st.text_input("1. Drugie imię/Inicjał", value=st.session_state.get("c_middle", ""))
        
        c2a, c2b = st.columns(2)
        with c2a: c_dob = st.text_input("2. Data ur. (MM/DD/RR)", value=st.session_state.get("c_dob", ""))
        with c2b: c_mem = st.number_input("3. Członkowie rodziny z Tobą", min_value=0, value=st.session_state.get("c_mem", 3))
        
        c_street = st.text_input("4a. Hotel / Ulica w USA", value=st.session_state.get("c_street", ""))
        c4a, c4b = st.columns(2)
        with c4a: c_city = st.text_input("4b. Miasto w USA", value=st.session_state.get("c_city", "Des Moines"))
        with c4b: c_state = st.text_input("4c. Stan", value=st.session_state.get("c_state", "IA"))
        
        c5a, c5b = st.columns(2)
        with c5a: c_pass_country = st.text_input("5. Paszport wydany przez", value=st.session_state.get("c_pass_country", "POLAND"))
        with c5b: c_pass_no = st.text_input("6. Numer paszportu", value=st.session_state.get("c_pass_no", ""))
        
        c_residence = st.text_input("7. Państwo zamieszkania", value=st.session_state.get("c_residence", "POLAND"))
        c_visited = st.text_input("8. Odwiedzone kraje przed przylotem", value=st.session_state.get("c_visited", "NONE"))
        c_fly = st.text_input("9. Linia i nr lotu", value=st.session_state.get("c_fly", ""))
        
        st.markdown("---")
        def r_idx(key): return 1 if "Tak" in st.session_state.get(key, "Nie") else 0
        
        c_10 = st.radio("10. Cel to biznes?", ["Nie", "Tak"], index=r_idx("c_10"), horizontal=True)
        c_11a = st.radio("11a. Owoce/Rośliny?", ["Nie", "Tak"], index=r_idx("c_11a"), horizontal=True)
        c_11b = st.radio("11b. Mięso/Zwierzęta?", ["Nie", "Tak"], index=r_idx("c_11b"), horizontal=True)
        c_11c = st.radio("11c. Czynniki chorobotwórcze?", ["Nie", "Tak"], index=r_idx("c_11c"), horizontal=True)
        c_11d = st.radio("11d. Byłeś na farmie?", ["Nie", "Tak"], index=r_idx("c_11d"), horizontal=True)
        c_12 = st.radio("12. Kontakt z żywym inwentarzem?", ["Nie", "Tak"], index=r_idx("c_12"), horizontal=True)
        c_13 = st.radio("13. Gotówka > 10 000 USD?", ["Nie", "Tak"], index=r_idx("c_13"), horizontal=True)
        c_14 = st.radio("14. Towary na sprzedaż?", ["Nie", "Tak"], index=r_idx("c_14"), horizontal=True)
        c_15 = st.number_input("15. Wartość prezentów w USA [$]", min_value=0, value=st.session_state.get("c_15", 0))

        # Zapamiętaj w sesji, żeby nie zniknęło przy przełączaniu zakładek
        keys = ['c_last','c_first','c_middle','c_dob','c_mem','c_street','c_city','c_state','c_pass_country','c_pass_no','c_residence','c_visited','c_fly','c_10','c_11a','c_11b','c_11c','c_11d','c_12','c_13','c_14','c_15']
        vals = [c_last,c_first,c_middle,c_dob,c_mem,c_street,c_city,c_state,c_pass_country,c_pass_no,c_residence,c_visited,c_fly,c_10,c_11a,c_11b,c_11c,c_11d,c_12,c_13,c_14,c_15]
        for k, v in zip(keys, vals): 
            st.session_state[k] = v

    with c_card:
        def yn(val): return "YES (X)" if "Tak" in val else "NO (X)"
        dict_data = {
            'c_last': c_last.upper(), 'c_first': c_first.upper(), 'c_middle': c_middle.upper(),
            'c_dob': c_dob, 'c_mem': c_mem, 'c_street': c_street.upper(), 'c_city': c_city.upper(), 'c_state': c_state.upper(),
            'c_pass_country': c_pass_country.upper(), 'c_pass_no': c_pass_no.upper(),
            'c_residence': c_residence.upper(), 'c_visited': c_visited.upper(), 'c_fly': c_fly.upper(),
            'c_10': yn(c_10), 'c_11a': yn(c_11a), 'c_11b': yn(c_11b), 'c_11c': yn(c_11c), 'c_11d': yn(c_11d), 
            'c_12': yn(c_12), 'c_13': yn(c_13), 'c_14': yn(c_14), 'c_15': c_15
        }
        render_customs_card(dict_data)
