import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime
from tvdatafeed import TvDatafeed, Interval
from analyse.tech_analysis import analysiere_technik
from utils.news_api import hole_news

# === APP EINSTELLUNGEN ===
st.set_page_config(page_title="Vela Quant", page_icon="📈", layout="wide")

# === DESIGN ===
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #f5f5f5;
        }
        .stButton>button {
            color: white;
            background-color: #1f77b4;
            border-radius: 5px;
            padding: 0.5em 1em;
            font-weight: bold;
        }
        .stSelectbox > div, .stTextInput > div {
            background-color: #1c1e26;
        }
        .stDataFrame, .stTable {
            background-color: #1e2127;
        }
        .block-container {
            padding-top: 2rem;
        }
        .stMetricValue {
            color: #21ba45;
        }
    </style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
st.sidebar.image("https://em-content.zobj.net/source/microsoft-teams/363/chart-increasing_1f4c8.png", width=50)
st.sidebar.title("📊 Trading KI Menü")
st.sidebar.markdown("Nutze die Navigation für deine tägliche Marktanalyse.")
zeitraum = st.sidebar.selectbox("Zeitraum auswählen", ["Heute", "Gestern", "Letzte Woche"])
strategie = st.sidebar.selectbox("Strategie wählen", ["Opening Range", "Momentum", "Breakout", "News-basiert"])
theme_toggle = st.sidebar.radio("Theme", ["Dark", "Light"], index=0)
st.sidebar.markdown("[📖 Dokumentation öffnen](https://example.com)")

# === SIDEBAR LIVE-DASHBOARD ===
try:
    gespeicherte = pd.read_csv("data/entscheidungen.csv")
    heute = datetime.now().strftime("%Y-%m-%d")
    heute_eintrag = gespeicherte[gespeicherte["Datum"] == heute]
    if not heute_eintrag.empty:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📅 **Heute**")
        ki_signal = heute_eintrag.iloc[-1]["KI-Signal"]
        eigene_entscheidung = heute_eintrag.iloc[-1]["Eigene Einschätzung"]
        st.sidebar.markdown(f"**KI-Signal:** `{ki_signal}`")
        st.sidebar.markdown(f"**Eigene Entscheidung:** `{eigene_entscheidung}`")
    if "KI-Signal" in gespeicherte.columns and "Eigene Einschätzung" in gespeicherte.columns:
        gespeicherte["Treffer"] = gespeicherte["KI-Signal"] == gespeicherte["Eigene Einschätzung"]
        trefferquote = round(gespeicherte["Treffer"].mean() * 100, 2)
        st.sidebar.metric("✔️ Gesamt-Trefferquote", f"{trefferquote}%")
except Exception:
    pass

# === TITEL ===
st.title("🤖 Willkommen bei Vela Quant – Tägliche Analysen für den ES1!")
st.caption("Entwickelt für systematische S&P500-Futures-Trades um 13:25 Uhr London-Zeit")
st.markdown("---")

# === TABS ===
tabs = st.tabs(["🧠 Analyse", "📝 Entscheidung", "📊 Verlauf", "🗞️ News", "📉 Chart"])

# === TAB 1: Analyse ===
with tabs[0]:
    st.subheader("🔍 Technische Analyse")
    signal = None
    daten = None
    if st.button("🚦 Analyse durchführen", key="analyse_button_tab"):
        signal, daten = analysiere_technik()
        if signal:
            color = "#21ba45" if "long" in signal.lower() else "#db2828" if "short" in signal.lower() else "#fbbd08"
            st.markdown(f"""
                <div style='border-left: 6px solid {color}; padding: 1rem; background-color: #1c1e26; border-radius: 8px;'>
                    <h4 style='margin: 0;'>📍 Analyseergebnis:</h4>
                    <p style='font-size: 24px; font-weight: bold; color: {color};'>{signal}</p>
                    <p style='font-size: 14px; color: #aaa;'>
                        {"Bullish-Signal → Long-Trend wahrscheinlich" if "long" in signal.lower() else "Bearish-Signal → Short-Trend wahrscheinlich" if "short" in signal.lower() else "Kein klares Signal erkannt."}
                    </p>
                </div>
            """, unsafe_allow_html=True)
        with st.expander("Details zur Analyse anzeigen"):
            st.dataframe(daten, use_container_width=True)

# === TAB 2: Entscheidung ===
with tabs[1]:
    st.subheader("📋 Entscheidung abgeben")
    with st.container():
        st.markdown("<div style='background-color: #1e2127; padding: 1rem; border-radius: 10px;'>", unsafe_allow_html=True)
        eigene_einschaetzung = st.selectbox("Was würdest du heute tun?", ["Long", "Short", "No Trade"])
        trade_geplant = st.radio("Planst du heute aktiv einen Trade einzugehen?", ["Ja", "Nein"], horizontal=True)
        kommentar = st.text_input("Kommentar (optional)")
        st.markdown("</div>", unsafe_allow_html=True)
    os.makedirs("data", exist_ok=True)
    if signal and st.button("💾 Entscheidung speichern", key="speichern_button_1_tab"):
        heute = datetime.now().strftime("%Y-%m-%d")
        neue_entscheidung = pd.DataFrame([{
            "Datum": heute,
            "KI-Signal": signal,
            "Eigene Einschätzung": eigene_einschaetzung,
            "Trade geplant": trade_geplant,
            "Kommentar": kommentar
        }])
        try:
            alt = pd.read_csv("data/entscheidungen.csv")
            df = pd.concat([alt, neue_entscheidung], ignore_index=True)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            df = neue_entscheidung
        df.to_csv("data/entscheidungen.csv", index=False)
        st.success("✅ Entscheidung gespeichert.")
        st.dataframe(neue_entscheidung, use_container_width=True)
    elif st.button("💾 Entscheidung speichern", key="speichern_button_2_tab") and not signal:
        st.error("⚠️ Es wurde noch keine Analyse durchgeführt. Bitte zuerst auf 'Analyse durchführen' klicken.")

# === TAB 3: Verlauf ===
with tabs[2]:
    st.subheader("📈 Verlauf & Trefferquote")
    try:
        gespeicherte = pd.read_csv("data/entscheidungen.csv")
        st.dataframe(gespeicherte, use_container_width=True)
        if "KI-Signal" in gespeicherte.columns and "Eigene Einschätzung" in gespeicherte.columns:
            gespeicherte["Treffer"] = gespeicherte["KI-Signal"] == gespeicherte["Eigene Einschätzung"]
            trefferquote = round(gespeicherte["Treffer"].mean() * 100, 2)
            st.metric("✔️ Übereinstimmungsquote", f"{trefferquote}%")
            balkenfarbe = "#21ba45" if trefferquote > 75 else "#fbbd08" if trefferquote >= 50 else "#db2828"
            st.markdown(f"""
                <div style='margin-top: 1rem; background: #333; border-radius: 10px; overflow: hidden;'>
                    <div style='width: {trefferquote}%; background: {balkenfarbe}; padding: 0.3rem 0; text-align: center;'>
                        <span style='color: white; font-weight: bold;'>{trefferquote}% Trefferquote</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        if "Trade geplant" in gespeicherte.columns:
            geplant_counts = gespeicherte["Trade geplant"].value_counts()
            st.markdown("---")
            st.markdown("### 📊 Anzahl aktiver Trade-Pläne")
            st.bar_chart(geplant_counts)
    except Exception:
        st.info("Keine Daten verfügbar.")

# === TAB 4: News ===
with tabs[3]:
    st.subheader("🗞️ Marktnachrichten")
    col1, col2 = st.columns([2, 1])
    with col1:
        thema = st.text_input("🔎 Thema eingeben", help="Beispiele: Fed, Inflation, Apple", key="news_input")
    with col2:
        quellenauswahl = st.selectbox("Quelle filtern (optional)", ["Alle", "Bloomberg", "Reuters", "CNBC", "Wall Street Journal"], key="quelle_input")
    if st.button("News abrufen", key="news_button"):
        news = hole_news(thema)
        if not news:
            st.warning("Keine News gefunden.")
        else:
            gefunden = False
            for n in news:
                try:
                    quelle = n['source']['name']
                    if quellenauswahl == "Alle" or quellenauswahl.lower() in quelle.lower():
                        st.markdown(f"- [{n['title']}]({n['url']}) – *{quelle}* ({n['publishedAt'][:10]})")
                        gefunden = True
                except Exception:
                    continue
            if not gefunden:
                st.info("Für diese Quelle wurden keine passenden Artikel gefunden.")

# === TAB 5: Chart ===
with tabs[4]:
    st.subheader("📉 Candlestick Chart für ES1!")
    gewaehltes_datum = st.date_input("📅 Datum auswählen", value=datetime(2025, 5, 15), format="YYYY-MM-DD")
    zeitraum_start = datetime.combine(gewaehltes_datum, datetime.strptime("13:00", "%H:%M").time())
    zeitraum_ende = datetime.combine(gewaehltes_datum, datetime.strptime("18:00", "%H:%M").time())
    if st.button("Chart anzeigen", key="chart_button"):
        tv = TvDatafeed()
        df = tv.get_hist(symbol="ES1!", exchange="CME", interval=Interval.in_15_minute, n_bars=1000)
        df = df[(df.index >= zeitraum_start) & (df.index <= zeitraum_ende)]
        if df.empty:
            st.warning("Für das gewählte Datum sind keine Daten verfügbar.")
        else:
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                                                 open=df["open"],
                                                 high=df["high"],
                                                 low=df["low"],
                                                 close=df["close"])]
                           )
            fig.update_layout(title=f"15-min Candlestick Chart für {gewaehltes_datum.strftime('%d.%m.%Y')}",
                              xaxis_title="Zeit", yaxis_title="Preis")
            st.plotly_chart(fig, use_container_width=True)
