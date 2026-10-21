# API BZP: ustalenia

Adres: https://ezamowienia.gov.pl/mo-board/api/v1/notice

Dostęp: publiczny, bez rejestracji i klucza API.

## Sprawdzone zachowanie (21.10.2026)

- `NoticeType=ContractNotice` działa: zwraca tylko ogłoszenia o zamówieniu.
- `PublicationDateFrom` działa.
- `PublicationDateTo` jest wymagany (bez niego API zwraca błąd 400), ale nie ogranicza wyników: API zwraca ogłoszenia od daty "od" do limitu.
- Limit: maksymalnie 500 ogłoszeń na zapytanie.
- Sortowanie: od najstarszych do najnowszych.
- Daty są w UTC (litera Z na końcu). Czas polski to UTC+1 zimą i UTC+2 latem.

## Kontrola kompletności

Endpoint `/notice/stats` zwraca dokładną liczbę ogłoszeń danego typu w zakresie dat.
Test 20.10.2026: stats = 463, pobrano 463 z tego dnia. Zgodne.

## Do sprawdzenia

- Jak pobrać więcej niż 500 ogłoszeń z jednego dnia (stronicowanie).
