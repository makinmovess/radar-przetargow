import os
from zoneinfo import ZoneInfo

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row

load_dotenv()

app = FastAPI(title="Radar przetargów")
szablony = Jinja2Templates(directory="app/templates")
WARSZAWA = ZoneInfo("Europe/Warsaw")

WOJEWODZTWA = {
    "PL02": "dolnośląskie",
    "PL04": "kujawsko-pomorskie",
    "PL06": "lubelskie",
    "PL08": "lubuskie",
    "PL10": "łódzkie",
    "PL12": "małopolskie",
    "PL14": "mazowieckie",
    "PL16": "opolskie",
    "PL18": "podkarpackie",
    "PL20": "podlaskie",
    "PL22": "pomorskie",
    "PL24": "śląskie",
    "PL26": "świętokrzyskie",
    "PL28": "warmińsko-mazurskie",
    "PL30": "wielkopolskie",
    "PL32": "zachodniopomorskie",
}

BRANZE = {
    "it": ("IT, sprzęt i oprogramowanie", ["30", "32", "48", "72"]),
    "budowlane": ("Roboty budowlane", ["45"]),
    "medyczne": ("Sprzęt i środki medyczne", ["33"]),
    "paliwa": ("Paliwa i energia", ["09"]),
    "zywnosc": ("Żywność", ["15"]),
    "transport": ("Pojazdy i transport", ["34", "60"]),
    "komunalne": ("Odpady i sprzątanie", ["90"]),
}


def adres_bazy():
    uzytkownik = os.environ["POSTGRES_USER"]
    haslo = os.environ["POSTGRES_PASSWORD"]
    baza = os.environ["POSTGRES_DB"]
    host = os.environ.get("POSTGRES_HOST", "localhost")
    return f"postgresql://{uzytkownik}:{haslo}@{host}:5432/{baza}"


def czas_polski(czas):
    if czas is None:
        return "brak"
    return czas.astimezone(WARSZAWA).strftime("%d.%m.%Y %H:%M")


@app.get("/")
def strona_glowna(request: Request, woj: str = "", szukaj: str = "", branza: str = ""):
    warunki = ["termin_ofert > now()"]
    parametry = []

    if woj:
        warunki.append("wojewodztwo = %s")
        parametry.append(woj)
    if branza in BRANZE:
        warunki.append("EXISTS (SELECT 1 FROM unnest(kody_cpv) AS k WHERE left(k, 2) = ANY(%s))")
        parametry.append(BRANZE[branza][1])
    if szukaj:
        warunki.append("przedmiot ILIKE %s")
        parametry.append(f"%{szukaj}%")

    sql = f"""
        SELECT bzp_number, przedmiot, zamawiajacy, miasto, wojewodztwo, termin_ofert
        FROM przetargi
        WHERE {" AND ".join(warunki)}
        ORDER BY termin_ofert
        LIMIT 500
    """

    with psycopg.connect(adres_bazy(), row_factory=dict_row) as polaczenie:
        rekordy = polaczenie.execute(sql, parametry).fetchall()
        ostatnie = polaczenie.execute("SELECT max(pobrano) AS czas FROM przetargi").fetchone()["czas"]

    wiersze = []
    for r in rekordy:
        wiersze.append({
            "numer": r["bzp_number"],
            "przedmiot": r["przedmiot"],
            "zamawiajacy": r["zamawiajacy"],
            "miasto": r["miasto"],
            "wojewodztwo": WOJEWODZTWA.get(r["wojewodztwo"], r["wojewodztwo"]),
            "termin": czas_polski(r["termin_ofert"]),
        })

    return szablony.TemplateResponse(request, "index.html", {
        "wiersze": wiersze,
        "wojewodztwa": WOJEWODZTWA,
        "branze": BRANZE,
        "woj": woj,
        "branza": branza,
        "szukaj": szukaj,
        "ostatnie": czas_polski(ostatnie),
    })
