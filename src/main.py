import os
import requests
import json

env_path = os.path.abspath('.env')

def load_env(filepath= env_path):
    if not os.path.exists(filepath):
        raise FileNotFoundError("Nie znaleziono .env")

    with open(filepath) as f:
         for line in f:
             line = line.strip()
             key, val = line.split("=", 1)
             os.environ[key.strip()] = val.strip()


def split_datetime(dt_str):
    """Bezpiecznie rozdziela czas ISO (np. '2026-11-24T14:35:00') na ('2026-11-24', '14:35')."""
    if not dt_str or "T" not in dt_str:
        return None, None
    date_part, time_part = dt_str.split("T", 1)
    return date_part, time_part[:5]


def parse_train(data):
    """ Przetwarzamy JSONa do potrzebnych nam danych"""
    stations_data = data.get("stations", {})
    trains_data = data.get("trains", [])

    if not trains_data:
        print("Nie znaleziono pociagu!")
        return None

    train = trains_data[0]

    status_map = {
        "P": "W trasie",
        "C": "Pociag skonczyl bieg",
        "S": "Pociag jeszcze nie odjechal",
        "X": "Pociag Odwolany"
    }

    parsed = {
        "orderId": train.get('orderId'),
        "scheduleId": train.get('scheduleId'),
        "operatingDate": train.get('operatingDate'),
        "trainStatus": status_map.get(train.get('trainStatus'), train.get('trainStatus')),
        "currentDelay": 0,
        "lastStation" : None,
        "nextStation": None,
        "timeLine": []
    }

    stations = train.get('stations', [])

    for st in stations:
        st_id = str(st.get('stationId'))
        st_name = stations_data.get(st_id, f"Stacja #{st_id}")

        is_confirmed = st.get('isConfirmed', False)
        planned_arr = st.get('plannedArrival')
        planned_dep = st.get('plannedDeparture')
        actual_arr = st.get('actualArrival')
        actual_dep = st.get('actualDeparture')

        planned_arr_date, planned_arr_time = split_datetime(planned_arr)
        planned_dep_date, planned_dep_time = split_datetime(planned_dep)
        actual_arr_date, actual_arr_time = split_datetime(actual_arr)
        actual_dep_date, actual_dep_time = split_datetime(actual_dep)

        arrival_delay = st.get('arrivalDelayMinutes') or 0
        departure_delay = st.get('departureDelayMinutes') or 0

        station_info = {
            "name": st_name,
            "planned_arrival_date": planned_arr_date,
            "planned_arrival_time": planned_arr_time,
            "planned_departure_date": planned_dep_date,
            "planned_departure_time": planned_dep_time,
            "actual_arrival_date": actual_arr_date,
            "actual_arrival_time": actual_arr_time,
            "actual_departure_date": actual_dep_date,
            "actual_departure_time": actual_dep_time,
            "is_confirmed": is_confirmed,
            "arrival_delay": arrival_delay,
            "departure_delay": departure_delay
        }

        parsed["timeLine"].append(station_info)

        if is_confirmed:
            parsed["lastStation"] = st_name
            parsed["currentDelay"] = departure_delay or arrival_delay
        elif parsed["nextStation"] is None and parsed["lastStation"] is not None:
            parsed["nextStation"] = st_name

    return parsed

        
def main():
    load_env()
    PKL_API = os.getenv("PLK_API")

    if not PKL_API:
        print("PKL_API nie znalezione!")
        return

    PKL_API = PKL_API.strip().strip('"').strip("'")

    url = "https://pdp-api.plk-sa.pl/api/v1/operations?withPlanned=true&pageSize=1"
    headers = {
        "Authorization": f"Bearer {PKL_API}",
        "Accept": "application/json"
    }


    response = requests.get(url= url, headers= headers)
    print(response.status_code) 
    data = response.json()
    train_info = parse_train(data)

    if train_info:
        print("=" * 60)
        print(f" Pociąg ID: {train_info['orderId']} | Status: {train_info['trainStatus']}")
        print(f" Obecne opóźnienie: {train_info['currentDelay']} min")
        print(f" Ostatnia stacja: {train_info['lastStation']}")
        print(f" Następna stacja: {train_info['nextStation']}")
        print("=" * 60)
        print("Trasa:")
        for s in train_info["timeLine"]:
            ikona = "✔️" if s["is_confirmed"] else "⚪"
            arr_delay_str = f"(+{s['arrival_delay']} min)" if s["arrival_delay"] > 0 else "(o czasie)"
            dep_delay_str = f"(+{s['departure_delay']} min)" if s["departure_delay"] > 0 else "(o czasie)"

            arr_str = f"Przyjazd: {s['planned_arrival_time']} {arr_delay_str}" if s['planned_arrival_time'] else "Stacja początkowa"
            dep_str = f"Odjazd: {s['planned_departure_time']} {dep_delay_str}" if s['planned_departure_time'] else "Stacja końcowa"

            print(f"  {ikona} {s['name']:<28} | {arr_str:<30} | {dep_str}")

        
if __name__ == "__main__":
    main()
