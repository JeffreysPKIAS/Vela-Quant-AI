import pandas as pd

def analysiere_technik():
    sma_trend = "steigend"
    rsi = 42
    orb_breakout = True
    gap = "neutral"
    tagesrange = "hoch"

    bewertung = pd.DataFrame({
        "Kriterium": ["Trend", "RSI", "Opening Range", "Gap", "Tagesrange"],
        "Bewertung": [sma_trend, rsi, "Breakout" if orb_breakout else "kein Ausbruch", gap, tagesrange]
    })

    score = 0
    begruendung = []

    if sma_trend == "steigend":
        score += 1
        begruendung.append("Trend ist stabil steigend (SMA)")

    if rsi < 50:
        score += 1
        begruendung.append(f"RSI bei {rsi} → Potenzial für Long")

    if orb_breakout:
        score += 1
        begruendung.append("Opening Range wurde nach oben durchbrochen")

    if gap == "neutral":
        begruendung.append("Kein negatives Gap – Marktstart stabil")

    if tagesrange == "hoch":
        score += 1
        begruendung.append("Tagesvolatilität überdurchschnittlich")

    if score >= 3:
        signal = "Long"
    elif score <= 1:
        signal = "Short"
    else:
        signal = "No Trade"

    begruendung.append(f"→ Gesamtbewertung ergibt ein {signal}-Signal mit {'hoher' if score >= 3 else 'niedriger' if score <= 1 else 'neutraler'} Konfidenz")

    return signal, bewertung, "  \n".join(begruendung)
