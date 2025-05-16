import requests

def hole_news(api_key, suchbegriff="Fed", max_artikel=5):
    url = f"https://newsapi.org/v2/everything?q={suchbegriff}&language=en&sortBy=publishedAt&pageSize={max_artikel}&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        daten = response.json()
        artikel = daten["articles"]
        nachrichten = []

        for artikel in artikel:
            titel = artikel["title"]
            quelle = artikel["source"]["name"]
            datum = artikel["publishedAt"]
            link = artikel["url"]
            nachrichten.append(f"📰 **{titel}**\nQuelle: {quelle}\nDatum: {datum}\n[Zur News]({link})\n")

        return nachrichten
    else:
        return [f"Fehler: {response.status_code} - {response.text}"]
from textblob import TextBlob

from textblob import TextBlob

def bewerte_sentiment(text):
    blob = TextBlob(text)
    polarität = blob.sentiment.polarity  # Wert zwischen -1 (negativ) und +1 (positiv)

    if polarität > 0.2:
        return "🟢 Positiv"
    elif polarität < -0.2:
        return "🔴 Negativ"
    else:
        return "🟡 Neutral"
