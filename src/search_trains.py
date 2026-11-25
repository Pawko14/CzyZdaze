import datetime

from schedules import get_schedules_for_day
from stations import extract_route_details


def matches_by_name(route, query_lower):
    """Sprawdza, czy nazwa pociągu (np. HETMAN) zawiera szukaną frazę."""
    name = (route.get("name") or "").lower()
    return bool(name and query_lower in name)


def matches_by_number(route, query_lower):
    """
    Sprawdza, czy numer krajowy (np. 23112, 49011) lub pełny z przewoźnikiem (np. IC 23112)
    pasuje do podanej frazy.
    """
    nat_num = str(route.get("nationalNumber") or "").lower()
    if not nat_num:
        return False

    carrier = (route.get("carrierCode") or "").lower()
    full_num = f"{carrier} {nat_num}".strip()

    # Wymagamy co najmniej jednej cyfry, aby wpisanie samego kodu np. "IC" w trybie auto
    # nie zwróciło wszystkich pociągów danego przewoźnika
    if not any(ch.isdigit() for ch in query_lower):
        return False

    return query_lower in nat_num or query_lower in full_num


def _route_matches(route, query_lower, mode):
    """Dopasowuje trasę zgodnie z wybranym trybem ('name', 'number' lub 'auto')."""
    if mode == "name":
        return matches_by_name(route, query_lower)
    if mode == "number":
        return matches_by_number(route, query_lower)
    return matches_by_name(route, query_lower) or matches_by_number(route, query_lower)


def search_trains(headers, query, date_str, stations_dict, mode="auto"):
    """
    Wyszukuje pociągi z podanego dnia oraz z dnia poprzedniego (tylko nocne).
    Obsługuje wyszukiwanie po nazwie ('name'), numerze ('number') lub obu naraz ('auto').
    """
    query_lower = query.strip().lower()
    if not query_lower:
        return []

    target_date = datetime.date.fromisoformat(date_str)
    yesterday_str = (target_date - datetime.timedelta(days=1)).isoformat()

    matches = []

    for day in [yesterday_str, date_str]:
        routes = get_schedules_for_day(headers, day)

        for r in routes:
            if not _route_matches(r, query_lower, mode):
                continue

            details = extract_route_details(r, stations_dict)

            # Wczorajsze pociągi kończące bieg przed północą nie jadą już w podanym dniu
            if day == yesterday_str and not details["crosses_midnight"]:
                continue

            matches.append({
                **r,
                "operatingDate": day,
                "details": details,
            })

    return matches
