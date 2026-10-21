import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Radar przetargów")
szablony = Jinja2Templates(directory="app/templates")
FOLDER_DANYCH = Path("data")
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


def najnowszy_plik():
    pliki = sorted(FOLDER_DANYCH.glob("*.json"))
    if pliki:
        return pliki[-1]
    return None


def czas_polski(tekst):
    if not tekst:
        return "brak"
    czas = datetime.fromisoformat(tekst.replace("Z", "+00:00"))
    return czas.astimezone(WARSZAWA).strftime("%d.%m.%Y %H:%M")


@app.get("/")
def strona_glowna(request: Request, woj: str = "", szukaj: str = ""):
    plik = najnowszy_plik()
    ogloszenia = []
    if plik:
        ogloszenia = json.loads(plik.read_text(encoding="utf-8"))

    if woj:
        ogloszenia = [o for o in ogloszenia if o["organizationProvince"] == woj]
    if szukaj:
        fraza = szukaj.lower()
        ogloszenia = [o for o in ogloszenia if fraza in o["orderObject"].lower()]

    wiersze = []
    for o in ogloszenia:
        wiersze.append({
            "numer": o["bzpNumber"],
            "przedmiot": o["orderObject"],
            "zamawiajacy": o["organizationName"],
            "miasto": o["organizationCity"],
            "wojewodztwo": WOJEWODZTWA.get(o["organizationProvince"], o["organizationProvince"]),
            "termin": czas_polski(o["submittingOffersDate"]),
        })

    return szablony.TemplateResponse(request, "index.html", {
        "wiersze": wiersze,
        "wojewodztwa": WOJEWODZTWA,
        "woj": woj,
        "szukaj": szukaj,
        "dzien": plik.stem if plik else "brak danych",
    })
