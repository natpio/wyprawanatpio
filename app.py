import streamlit as st
import datetime

st.set_page_config(page_title="Misja Chicago", page_icon="✈️", layout="centered")

st.title("🗽 Kierunek Chicago: Projekt Rodzina")

# Odliczanie
wyjazd = datetime.date(2026, 6, 30)
dzis = datetime.date.today()
zostalo_dni = (wyjazd - dzis).days

st.info(f"🚨 Do wyjazdu Flixbusem z Poznania zostało: **{zostalo_dni} dni!**")

# Zakładki
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Plan", "📄 Dokumenty", "🧳 Pakowanie", "🎮 Dla Dzieci"])

with tab1:
    st.subheader("Oś czasu")
    st.markdown("""
    - **30.06 (Wtorek):** Pakujemy się do Flixbusa (Poznań -> Warszawa).
    - **Noc 30.06:** Nocleg w Warszawie. Ładujemy baterie!
    - **01.07 (Środa Rano):** Transfer na Okęcie (WAW).
    - **01.07 (Lot 1):** WAW ✈️ MUC (Monachium).
    - **01.07 (Lot 2):** MUC ✈️ ORD (Chicago).
    """)

with tab2:
    st.subheader("Zadania i Dokumenty")
    st.write("Tu wyląduje st.data_editor z Google Sheets dla ESTA, paszportów i biletów.")

with tab3:
    st.subheader("Moduł Pakowania")
    st.write("Podział na bagaże. Pamiętajcie o mokrych chusteczkach!")

with tab4:
    st.subheader("Punkty Dziewczynek 🌟")
    if st.button("Udana kontrola bezpieczeństwa!"):
        st.balloons()
        st.success("Brawo! +10 punktów zdobytych!")
