import requests
from datetime import datetime, timedelta

def hole_news(api_key, suchbegriff="Fed", max_artikel=10):
    if not api_key:
        return ["❌ Fehler: Kein API-Key übergeben."]

    von_datum = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={suchbegriff}&from={von_datum}&language=en&sortBy=publishedAt&"
        f"pageSize={max_artikel}&apiKey={api_key}"
    )

    response = requests.get(url)

    if response.status_code == 200:
        daten = response.json()
        artikel = daten.get("articles", [])
        nachrichten = []

        for artikel in artikel:
            nachrichten.append({
                "title": artikel["title"],
                "source": artikel["source"]["name"],
                "publishedAt": artikel["publishedAt"],
                "url": artikel["url"]
            })

        return nachrichten
    else:
        return [{"title": f"Fehler: {response.status_code}", "source": "System", "publishedAt": "", "url": ""}]
