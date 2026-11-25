from api_client import api_get
from cache_utils import read_json_cache, write_json_cache
from config import PROJECT_ROOT

CACHE_FILE = PROJECT_ROOT / "stations_cache.json"


def get_stations_dict(headers):
    """Zwraca słownik { 'stationId': 'Nazwa Stacji' }, korzystając z lokalnego cache."""
    cached = read_json_cache(CACHE_FILE)
    if isinstance(cached, dict):
        return cached

    print("Pobieram słownik stacji kolejowych...")
    url = "https://pdp-api.plk-sa.pl/api/v1/dictionaries/stations?pageSize=4000"
    data = api_get(url, headers=headers)
    if not data:
        return {}

    stations = {str(s["id"]): s["name"] for s in data.get("stations", [])}
    write_json_cache(CACHE_FILE, stations, indent=2)
    return stations


def extract_route_details(route, stations_dict):
    """
    Wyciąga numer handlowy (np. IC 23112), relację (Skąd ➔ Dokąd),
    godzinę startu, flagę przejścia przez północ oraz listę stacji z obiektu trasy.
    """
    carrier = route.get("carrierCode") or ""
    nat_num = str(route.get("nationalNumber") or "")
    full_number = f"{carrier} {nat_num}".strip() if nat_num else carrier

    st_list = route.get("stations", [])
    if st_list:
        start_name = stations_dict.get(str(st_list[0]["stationId"]), "Nieznana")
        end_name = stations_dict.get(str(st_list[-1]["stationId"]), "Nieznana")
        relation = f"{start_name} ➔ {end_name}"
        departure_time = (st_list[0].get("departureTime") or "")[:5]
        crosses_midnight = any((s.get("arrivalDay") or 0) >= 1 for s in st_list)
    else:
        relation = "Trasa nieznana"
        departure_time = ""
        crosses_midnight = False

    return {
        "fullNumber": full_number,       # np. "IC 23112" lub "PR 49011"
        "nationalNumber": nat_num,       # np. "23112"
        "relation": relation,            # np. "Hrubieszów Miasto ➔ Kraków Główny"
        "departureTime": departure_time, # np. "06:57"
        "name": route.get("name") or "", # np. "HETMAN" (lub "" dla Polregio)
        "crosses_midnight": crosses_midnight,
        "stations": st_list,
    }


def get_route_details(headers, schedule_id, order_id, stations_dict):
    """
    Pobiera szczegóły pojedynczej trasy z API: numer handlowy (np. IC 23112) oraz relację (Skąd ➔ Dokąd).
    """
    url = f"https://pdp-api.plk-sa.pl/api/v1/schedules/route/{schedule_id}/{order_id}"
    data = api_get(url, headers=headers)
    if not data:
        return None

    return extract_route_details(data, stations_dict)