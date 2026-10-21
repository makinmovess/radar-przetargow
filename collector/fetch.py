import json
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

API = "https://ezamowienia.gov.pl/mo-board/api/v1/notice"


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
    print(f"Zapisano do {plik}")

    if len(ogloszenia) != oczekiwane:
        print("UWAGA: liczby się nie zgadzają, część ogłoszeń mogła zostać pominięta")
        sys.exit(1)


if __name__ == "__main__":
    main()
