import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime
from tvdatafeed import TvDatafeed, Interval
from analyse.tech_analysis import analysiere_technik
from utils.news_api import hole_news, bewerte_sentiment

# === TITEL ===
st.title("📈 Live-News zur Marktlage")
st.header("📊 Technische Analyse (ES1!)")

# === TECHNISCHE ANALYSE ===
signal = None  # Sicherstellen, dass signal global verfügbar ist
daten = None
if st.button("Technische Analyse starten", key="analyse_button"):
    signal, daten = analysiere_technik()
    st.markdown(f"**📍 Analyseergebnis:** `{signal}`")
    st.dataframe(daten)

# === EIGENE EINSCHÄTZUNG ===
eigene_einschaetzung = st.selectbox("Was würdest du heute tun?", ["Long", "Short", "No Trade"])
kommentar = st.text_input("Kommentar (optional)")

# === ORDNER SICHERSTELLEN ===
os.makedirs("data", exist_ok=True)

# === ENTSCHEIDUNG SPEICHERN ===
if signal and st.button("📁 Entscheidung speichern", key="speichern_button_1"):
    heute = datetime.now().strftime("%Y-%m-%d")
    neue_entscheidung = pd.DataFrame([{
        "Datum": heute,
        "KI-Signal": signal,
        "Eigene Einschätzung": eigene_einschaetzung,
        "Kommentar": kommentar
    }])

    try:
        alt = pd.read_csv("data/entscheidungen.csv")
        df = pd.concat([alt, neue_entscheidung], ignore_index=True)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = neue_entscheidung

    df.to_csv("data/entscheidungen.csv", index=False)
    st.success("✅ Entscheidung gespeichert.")
    st.dataframe(neue_entscheidung)
elif st.button("📁 Entscheidung speichern", key="speichern_button_2") and not signal:
    st.error("⚠️ Bitte zuerst auf 'Technische Analyse starten' klicken.")

# === VERGANGENE ENTSCHEIDUNGEN ===
if st.checkbox("📊 Vergangene Entscheidungen anzeigen"):
    try:
        gespeicherte = pd.read_csv("data/entscheidungen.csv")
        st.dataframe(gespeicherte)

        # === TREFFERQUOTE BERECHNEN ===
        if "KI-Signal" in gespeicherte.columns and "Eigene Einschätzung" in gespeicherte.columns:
            gespeicherte["Treffer"] = gespeicherte["KI-Signal"] == gespeicherte["Eigene Einschätzung"]
            trefferquote = round(gespeicherte["Treffer"].mean() * 100, 2)
            st.metric("✔️ Übereinstimmungsquote", f"{trefferquote}%")

    except FileNotFoundError:
        st.info("Noch keine Entscheidungen gespeichert.")
    except pd.errors.EmptyDataError:
        st.info("Datei ist leer 🧾 es wurden noch keine gültigen Daten gespeichert.")

# === NEWS MODULE ===
st.subheader("📰 Live-News zur Marktlage")
thema = st.text_input("Gib ein Thema ein (z. B. 'Fed', 'S&P 500', 'Inflation'):")
if st.button("News abrufen"):
    news = hole_news(thema)
    if not news:
        st.warning("Keine News gefunden.")
    else:
        for n in news:
            try:
                st.write(f"🗞 {n['title']} | Quelle: {n['source']['name']} | Datum: {n['publishedAt']}")
            except Exception:
                continue

# === CHART ANZEIGEN ===
st.subheader("📉 Chartvergleich")
if st.button("Chart anzeigen"):
    tv = TvDatafeed()  # Demo-Modus
    df = tv.get_hist(symbol="ES1!", exchange="CME", interval=Interval.in_15_minute, n_bars=1000)
    df = df[(df.index >= "2025-05-15 13:00") & (df.index <= "2025-05-15 18:00")]

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df["open"],
                                         high=df["high"],
                                         low=df["low"],
                                         close=df["close"])])
    fig.update_layout(title="15-min Candlestick Chart für ES1!", xaxis_title="Zeit", yaxis_title="Preis")
    st.plotly_chart(fig)
