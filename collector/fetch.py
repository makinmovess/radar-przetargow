import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import psycopg
import requests
from dotenv import load_dotenv

load_dotenv()

API = "https://ezamowienia.gov.pl/mo-board/api/v1/notice"
WZOR_CPV = re.compile(r"\d{8}-\d")

SQL_ZAPISU = """
    INSERT INTO przetargi (
        object_id, bzp_number, przedmiot, rodzaj, kody_cpv, zamawiajacy,
        miasto, wojewodztwo, termin_ofert, data_publikacji, tresc_html
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (object_id) DO NOTHING
"""


def adres_bazy():
    uzytkownik = os.environ["POSTGRES_USER"]
    haslo = os.environ["POSTGRES_PASSWORD"]
    baza = os.environ["POSTGRES_DB"]
    host = os.environ.get("POSTGRES_HOST", "localhost")
    return f"postgresql://{uzytkownik}:{haslo}@{host}:5432/{baza}"


def pobierz_dzien(dzien):
    parametry = {
        "NoticeType": "ContractNotice",
        "PublicationDateFrom": f"{dzien}T00:00:00Z",
        "PublicationDateTo": f"{dzien}T23:59:59Z",
        "PageSize": 500,
    }
    odpowiedz = requests.get(API, params=parametry, timeout=30)
    odpowiedz.raise_for_status()
    wszystkie = odpowiedz.json()
    return [o for o in wszystkie if o["publicationDate"].startswith(dzien)]


def policz_w_statystykach(dzien):
    parametry = {
        "PublicationDateFrom": f"{dzien}T00:00:00Z",
        "PublicationDateTo": f"{dzien}T23:59:59Z",
    }
    odpowiedz = requests.get(API + "/stats", params=parametry, timeout=30)
    odpowiedz.raise_for_status()
    for wpis in odpowiedz.json():
        if wpis["noticeType"] == "ContractNotice":
            return wpis["numberOfNotices"]
    return 0


def zapisz_do_bazy(ogloszenia):
    nowe = 0
    with psycopg.connect(adres_bazy()) as polaczenie:
        with polaczenie.cursor() as kursor:
            for o in ogloszenia:
                kursor.execute(SQL_ZAPISU, (
                    o["objectId"],
                    o["bzpNumber"],
                    o["orderObject"],
                    o.get("orderType"),
                    WZOR_CPV.findall(o.get("cpvCode") or ""),
                    o.get("organizationName"),
                    o.get("organizationCity"),
                    o.get("organizationProvince"),
                    o.get("submittingOffersDate"),
                    o["publicationDate"],
                    o.get("htmlBody"),
                ))
                nowe += kursor.rowcount
    return nowe


def main():
    if len(sys.argv) > 1:
        dzien = sys.argv[1]
    else:
        dzien = str(date.today() - timedelta(days=1))

    ogloszenia = pobierz_dzien(dzien)
    oczekiwane = policz_w_statystykach(dzien)
    print(f"Dzień {dzien}: pobrano {len(ogloszenia)}, według statystyk {oczekiwane}")

    Path("data").mkdir(exist_ok=True)
    plik = f"data/{dzien}.json"
    with open(plik, "w", encoding="utf-8") as f:
        json.dump(ogloszenia, f, ensure_ascii=False, indent=2)
    print(f"Kopia zapasowa w {plik}")

    nowe = zapisz_do_bazy(ogloszenia)
    print(f"Zapisano do bazy nowych: {nowe}, pominięto istniejących: {len(ogloszenia) - nowe}")

    if len(ogloszenia) != oczekiwane:
        print("UWAGA: liczby się nie zgadzają, część ogłoszeń mogła zostać pominięta")
        sys.exit(1)


if __name__ == "__main__":
    main()
