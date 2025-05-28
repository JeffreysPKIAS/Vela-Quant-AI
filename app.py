import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from analyse.tech_analysis import analysiere_technik

# === SETUP ===
st.set_page_config(page_title="Vela Quant AI", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")
load_dotenv()
gnews_api_key = os.getenv("GNEWS_API_KEY")

# === CUSTOM STYLE ===
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #0B0F1A;
        color: #FFFFFF;
        font-family: 'Segoe UI', sans-serif;
    }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #1C2230;
        color: white;
        border-radius: 0.5rem;
        margin-right: 0.5rem;
        padding: 0.5rem 1rem;
    }
    .stButton>button {
        background-color: transparent;
        border: 2px solid #00bfa6;
        color: #00bfa6;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #00bfa620;
        cursor: pointer;
    }
    .stSlider > div {
        color: #00bfa6;
    }
    </style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("""
    <h1 style='color:#00bfa6;'>Vela Quant AI</h1>
    <p>Eine smarte Web-App für Futures-Trading mit Fokus auf den S&P 500</p>
    <hr style='border-color:#1C2230;'>
""", unsafe_allow_html=True)

# === TABS ===
tabs = st.tabs(["Analyse", "Entscheidung", "Verlauf", "News", "Chart"])

# === TAB 1 – Analyse ===
with tabs[0]:
    st.markdown("## 🧠 <span style='color:#00bfa6'>Technische Analyse</span>", unsafe_allow_html=True)
    with st.container(border=True):
        if st.button("🚦 Analyse starten", key="analyse_button"):
            signal, bewertung = analysiere_technik()
            st.markdown(f"**📈 Ergebnis:** `{signal}`")
            st.dataframe(bewertung, use_container_width=True)

# === TAB 2 – Entscheidung ===
with tabs[1]:
    st.markdown("## 📝 <span style='color:#00bfa6'>Entscheidung speichern</span>", unsafe_allow_html=True)
    with st.container(border=True):
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
            except:
                df = neue_entscheidung
            df.to_csv("data/entscheidungen.csv", index=False)
            st.success("✅ Entscheidung gespeichert.")
            st.dataframe(neue_entscheidung, use_container_width=True)

# === TAB 3 – Verlauf ===
with tabs[2]:
    st.markdown("## 📊 <span style='color:#00bfa6'>Verlauf</span>", unsafe_allow_html=True)
    with st.container(border=True):
        try:
            df = pd.read_csv("data/entscheidungen.csv")
            st.dataframe(df, use_container_width=True)
            heute = datetime.now().strftime("%Y-%m-%d")
            heute_df = df[df["Datum"] == heute]
            if not heute_df.empty:
                ki = heute_df.iloc[-1]["KI-Signal"]
                eigene = heute_df.iloc[-1]["Eigene Einschätzung"]
                punkte = 1 if ki == eigene else 0
                st.metric("✅ Übereinstimmung", f"{punkte * 100:.1f}%")
            # Neues KPI Panel
            total = len(df)
            treffer = df[df["KI-Signal"] == df["Eigene Einschätzung"]].shape[0]
            quote = (treffer / total) * 100 if total > 0 else 0
            st.metric("📊 Gesamttrades", total)
            st.metric("🎯 Trefferquote", f"{quote:.1f}%")
        except:
            st.info("Noch keine Entscheidungen vorhanden.")

# === TAB 4 – News ===
with tabs[3]:
    st.markdown("## 🗞️ <span style='color:#00bfa6'>Marktnachrichten</span>", unsafe_allow_html=True)
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            thema = st.text_input("🔎 Thema eingeben", value="S&P 500")
        with col2:
            max_results = st.slider("Anzahl Artikel", 1, 20, 10)

        def hole_gnews(api_key, suchbegriff="S&P 500", max_artikel=10):
            url = f"https://gnews.io/api/v4/search?q={suchbegriff}&lang=en&token={api_key}&max={max_artikel}"
            try:
                response = requests.get(url)
                data = response.json()
                return data.get("articles", [])
            except Exception as e:
                return [f"Fehler bei Anfrage: {e}"]

        if st.button("📥 News abrufen", key="gnews_button"):
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
                        except:
                            continue

# === TAB 5 – Chart ===
with tabs[4]:
    st.markdown("## 📉 <span style='color:#00bfa6'>Live-Chart</span>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("""
            <iframe src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_12345&symbol=VANTAGE%3ASP500&interval=15&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=dark&style=1&timezone=Europe%2FBerlin&withdateranges=1&hide_side_toolbar=0&allow_symbol_change=1&calendar=1&hotlist=1&autosize=1"
                    width="100%" height="600" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
        """, unsafe_allow_html=True)
