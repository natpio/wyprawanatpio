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
if col_sync.button("🔄 Odśwież chmurę", use_container_width=True):
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
                ed_p = st.data_editor(df_p, use_container_width=True, hide_index=True, num_rows="dynamic")
                if st.button("Zapisz Roadmap"):
                    st.session_state["df_Plan"] = ed_p
                    save_and_sync("Plan")
                    safe_rerun()
    with c_right:
        display_safe_image("chicago")
        st.write("")
        display_safe_image("desmoines")

# --- ZAKŁADKA 2: CHECKLIST ---
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
                    if st.button("COFNIJ", key=f"z_{i}"): st.session_state["df_Zadania"].at[i, "Status"] = False; save_and_sync("Zadania"); safe_rerun()
                else:
                    if st.button("ZROBIONE", type="primary", key=f"z_{i}"): st.session_state["df_Zadania"].at[i, "Status"] = True; save_and_sync("Zadania"); safe_rerun()
        with st.expander("⚙️ Admin Zadań"):
            ed_z = st.data_editor(df_z, column_config={"Status": st.column_config.CheckboxColumn("OK", width="small")}, hide_index=True, num_rows="dynamic")
            if st.button("Zapisz Zadania"): st.session_state["df_Zadania"] = ed_z; save_and_sync("Zadania"); safe_rerun()

# --- ZAKŁADKA 3: CARGO ---
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
                    if st.button("WYPAKUJ", key=f"b_{i}"): st.session_state["df_Bagaz"].at[i, "Spakowane"] = False; save_and_sync("Bagaz"); safe_rerun()
                else:
                    if st.button("DO WALIZKI", type="primary", key=f"b_{i}"): st.session_state["df_Bagaz"].at[i, "Spakowane"] = True; save_and_sync("Bagaz"); safe_rerun()
        with st.expander("⚙️ Admin Bagażu"):
            ed_b = st.data_editor(df_b, column_config={"Spakowane": st.column_config.CheckboxColumn("OK", width="small")}, hide_index=True, num_rows="dynamic")
            if st.button("Zapisz Bagaż"): st.session_state["df_Bagaz"] = ed_b; save_and_sync("Bagaz"); safe_rerun()

# --- ZAKŁADKA 4: KIDS HUB ---
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
                elif st.button("ZROBIONE", type="primary", key=f"g_{i}"): st.session_state["df_Grywalizacja"].at[i, "Zaliczone"] = True; st.session_state["show_balloons"] = True; save_and_sync("Grywalizacja"); safe_rerun()
        with st.expander("⚙️ Admin Gry"):
            ed_g = st.data_editor(df_g, hide_index=True, num_rows="dynamic")
            if st.button("Zapisz Gry"): st.session_state["df_Grywalizacja"] = ed_g; save_and_sync("Grywalizacja"); safe_rerun()

# --- ZAKŁADKA 5: ODPRAWA (CUSTOMS) ---
with t5:
    st.info("💡 Wypełnij raz - przepisz w samolocie na niebieski druk!")
    c_form, c_card = st.columns([1, 1.2])
    with c_form:
        c_name = st.text_input("1. Imię i Nazwisko", value=st.session_state.get("c_name", ""))
        c_dob = st.text_input("2. Data urodzenia (MM/DD/RR)", value=st.session_state.get("c_dob", ""))
        c_mem = st.number_input("3. Liczba osób z Tobą", min_value=0, value=st.session_state.get("c_mem", 3))
        c_addr = st.text_input("4. Adres w USA", value=st.session_state.get("c_addr", "Des Moines, IA"))
        c_pass = st.text_input("5-6. Wydanie i Nr Paszportu", value=st.session_state.get("c_pass", "POLAND, "))
        c_fly = st.text_input("9. Linia i Nr Lotu", value=st.session_state.get("c_fly", ""))
        c_gift = st.number_input("15. Wartość prezentów zostawianych w USA ($)", min_value=0, value=st.session_state.get("c_gift", 0))
        # Zapisujemy do sesji
        for k, v in zip(["c_name", "c_dob", "c_mem", "c_addr", "c_pass", "c_fly", "c_gift"], [c_name, c_dob, c_mem, c_addr, c_pass, c_fly, c_gift]):
            st.session_state[k] = v
    with c_card:
        render_customs_card(c_name, c_dob, c_mem, c_addr, c_pass, c_fly, c_gift)
