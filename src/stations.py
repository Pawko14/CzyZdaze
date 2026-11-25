import os
import json
import requests

CACHE_FILE = "stations_cache.json"

def get_stations_dict(headers):
    """Zwraca słownik { 'stationId': 'Nazwa Stacji' }, korzystając z lokalnego cache."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Pobieram słownik stacji kolejowych...")
    url = "https://pdp-api.plk-sa.pl/api/v1/dictionaries/stations?pageSize=4000"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        stations = {str(s["id"]): s["name"] for s in data.get("stations", [])}
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(stations, f, ensure_ascii=False, indent=2)
        return stations
    return {}


def get_route_details(headers, schedule_id, order_id, stations_dict):
    """
    Pobiera szczegóły trasy: numer handlowy (np. IC 23112) oraz relację (Skąd ➔ Dokąd).
    """
    url = f"https://pdp-api.plk-sa.pl/api/v1/schedules/route/{schedule_id}/{order_id}"
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None

    data = res.json()
    carrier = data.get("carrierCode", "")
    nat_num = data.get("nationalNumber", "")
    full_number = f"{carrier} {nat_num}".strip() if nat_num else carrier

    st_list = data.get("stations", [])
    if st_list:
        start_name = stations_dict.get(str(st_list[0]["stationId"]), "Nieznana")
        end_name = stations_dict.get(str(st_list[-1]["stationId"]), "Nieznana")
        relation = f"{start_name} ➔ {end_name}"
        crosses_midnight =  any((s.get("arrivalDay") or 0) >= 1 for s in st_list)
    else:
        relation = "Trasa nieznana"
        crosses_midnight = False

    return {
        "fullNumber": full_number,      # np. "IC 23112"
        "nationalNumber": nat_num,        # np. "23112"
        "relation": relation,            # np. "Hrubieszów Miasto ➔ Kraków Główny"
        "name": data.get("name", ""),     # np. "HETMAN"
        "crosses_midnight": crosses_midnight,
        "stations": st_list
    }