from collector import fetch


class FalszywaOdpowiedz:
    def __init__(self, dane):
        self.dane = dane

    def raise_for_status(self):
        pass

    def json(self):
        return self.dane


def test_pobierz_dzien_odrzuca_ogloszenia_z_innych_dni(monkeypatch):
    dane = [
        {"publicationDate": "2026-10-20T04:41:34Z"},
        {"publicationDate": "2026-10-20T23:10:00Z"},
        {"publicationDate": "2026-10-21T06:47:32Z"},
    ]
    monkeypatch.setattr(fetch.requests, "get", lambda *args, **kwargs: FalszywaOdpowiedz(dane))

    wynik = fetch.pobierz_dzien("2026-10-20")

    assert len(wynik) == 2


def test_pobierz_dzien_wysyla_date_koncowa(monkeypatch):
    wyslane = {}

    def falszywy_get(url, params, timeout):
        wyslane.update(params)
        return FalszywaOdpowiedz([])

    monkeypatch.setattr(fetch.requests, "get", falszywy_get)

    fetch.pobierz_dzien("2026-10-20")

    assert wyslane["PublicationDateTo"] == "2026-10-20T23:59:59Z"


def test_policz_w_statystykach_bierze_ogloszenia_o_zamowieniu(monkeypatch):
    dane = [
        {"noticeType": "TenderResultNotice", "numberOfNotices": 513},
        {"noticeType": "ContractNotice", "numberOfNotices": 463},
    ]
    monkeypatch.setattr(fetch.requests, "get", lambda *args, **kwargs: FalszywaOdpowiedz(dane))

    assert fetch.policz_w_statystykach("2026-10-20") == 463


def test_wzor_cpv_wyciaga_same_kody():
    tekst = "45000000-7 (Roboty budowlane),45233220-7 (Roboty w zakresie nawierzchni dróg)"
    assert fetch.WZOR_CPV.findall(tekst) == ["45000000-7", "45233220-7"]
