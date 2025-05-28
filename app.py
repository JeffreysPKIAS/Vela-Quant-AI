import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dateutil.parser import parse
from tvdatafeed import TvDatafeed, Interval
from analyse.tech_analysis import analysiere_technik
from utils.news_api import hole_news
from dotenv import load_dotenv
load_dotenv()

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
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
    </style>
""", unsafe_allow_html=True)

# === TITEL ===
st.title("🤖 Willkommen bei Vela Quant – Tägliche ES1!-Signale")
st.caption("Systematische S&P500-Futures-Strategie um 13:25 Uhr London-Zeit")
st.markdown("---")

# === TABS ===
tabs = st.tabs(["🧠 Analyse", "📝 Entscheidung", "📊 Verlauf", "🗞️ News", "📉 Chart"])

# === TAB 1 – Analyse ===
with tabs[0]:
    st.subheader("🔎 Technische Analyse")
    if st.button("🚦 Analyse durchführen", key="analyse_button"):
        signal, bewertung = analysiere_technik()
        st.markdown(f"**📈 Ergebnis:** `{signal}`")
        st.dataframe(bewertung)

# === TAB 2 – Entscheidung ===
with tabs[1]:
    st.subheader("📝 Entscheidung speichern")
    eigene = st.selectbox("Was würdest du heute tun?", ["Long", "Short", "No Trade"])
    kommentar = st.text_input("Kommentar (optional)")
    heute = datetime.now().strftime("%Y-%m-%d")

    if st.button("📂 Entscheidung speichern", key="speichern_button"):
        signal, _ = analysiere_technik()
        neue_entscheidung = pd.DataFrame([{
            "Datum": heute,
            "KI-Signal": signal,
            "Eigene Einschätzung": eigene,
            "Kommentar": kommentar
        }])
        os.makedirs("data", exist_ok=True)
        try:
            alt = pd.read_csv("data/entscheidungen.csv")
            df = pd.concat([alt, neue_entscheidung], ignore_index=True)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            df = neue_entscheidung
        df.to_csv("data/entscheidungen.csv", index=False)
        st.success("✅ Entscheidung gespeichert.")
        st.dataframe(neue_entscheidung)

# === TAB 3 – Verlauf ===
with tabs[2]:
    st.subheader("📊 Vergangene Entscheidungen")
    try:
        df = pd.read_csv("data/entscheidungen.csv")
        st.dataframe(df)
        if not df.empty:
            heute = datetime.now().strftime("%Y-%m-%d")
            heute_df = df[df["Datum"] == heute]
            if not heute_df.empty:
                ki = heute_df.iloc[-1]["KI-Signal"]
                eigene = heute_df.iloc[-1]["Eigene Einschätzung"]
                punkte = 1 if ki == eigene else 0
                st.metric("✅ Übereinstimmung", f"{punkte * 100:.1f}%")
    except Exception:
        st.info("Noch keine Entscheidungen vorhanden.")

# === TAB 4 – News ===
with tabs[3]:
    st.subheader("🗞️ Marktnachrichten")

    import os
    import requests
    from dotenv import load_dotenv

    # .env laden
    dotenv_path = os.path.join(os.getcwd(), ".env")
    load_dotenv(dotenv_path)
    gnews_api_key = os.getenv("GNEWS_API_KEY")

    col1, col2 = st.columns([3, 1])
    with col1:
        thema = st.text_input("🔎 Thema eingeben", value="S&P 500", help="Beispiele: Fed, Inflation, Apple", key="gnews_input")
    with col2:
        max_results = st.slider("Anzahl Artikel", 1, 20, 10, key="gnews_max")

    def hole_gnews(api_key, suchbegriff="S&P 500", max_artikel=10):
        url = f"https://gnews.io/api/v4/search?q={suchbegriff}&lang=en&token={api_key}&max={max_artikel}"
        try:
            response = requests.get(url)
            data = response.json()
            return data.get("articles", [])
        except Exception as e:
            return [f"Fehler bei Anfrage: {e}"]

    if st.button("News abrufen", key="gnews_button"):
        if not gnews_api_key:
            st.error("❌ Fehler: Kein GNEWS_API_KEY geladen. Bitte .env prüfen.")
        else:
            news = hole_gnews(gnews_api_key, suchbegriff=thema, max_artikel=max_results)
            if not news:
                st.warning("Keine News gefunden.")
            elif isinstance(news[0], str):
                st.error(news[0])
            else:
                for artikel in news:
                    try:
                        titel = artikel.get("title", "Kein Titel")
                        link = artikel.get("url", "#")
                        datum = artikel.get("publishedAt", "")[:10]
                        beschreibung = artikel.get("description", "")
                        quelle = artikel.get("source", {}).get("name", "Unbekannt")

                        st.markdown(f"### [{titel}]({link})")
                        st.write(f"📰 {quelle} | 📅 {datum}")
                        st.write(beschreibung)
                        st.markdown("---")
                    except Exception as e:
                        st.error(f"Fehler bei der Darstellung eines Artikels: {e}")

# === TAB 5 – Chart ===
with tabs[4]:
    st.subheader("📉 Live-Chart (TradingView)")

    st.markdown("""
        <div class="tradingview-widget-container">
          <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_12345&symbol=VANTAGE%3ASP500&interval=15&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=dark&style=1&timezone=Europe%2FBerlin&withdateranges=1&hide_side_toolbar=0&allow_symbol_change=1&calendar=1&hotlist=1&autosize=1"
                  width="100%" height="600" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
        </div>
    """, unsafe_allow_html=True)
