import datetime

from split_datetime import split_datetime

def calculate_delay(planned_time, actual_time):
    """
    Liczy różnicę w minutach między czasem planowanym ('07:40:00')
    a rzeczywistym ('2026-11-25T07:42:00').
    """
    if not planned_time or not actual_time:
        return 0
    
    # 1. Parsujemy czas rzeczywisty
    actual_dt = datetime.datetime.fromisoformat(actual_time)
    
    # 2. Tworzymy obiekt datetime dla planu z tą samą datą
    planned_t = datetime.time.fromisoformat(planned_time)
    planned_dt = datetime.datetime.combine(actual_dt.date(), planned_t)
    
    # 3. Różnica w minutach
    diff_minutes = int((actual_dt - planned_dt).total_seconds() / 60)

    if diff_minutes < -720:
        diff_minutes += 1440
    
    # Jeśli pociąg jedzie przed czasem, opóźnienie to 0
    return max(0, diff_minutes)   


def parse_train(train, sched_stations, stations_data):
    """ Przetwarzamy JSONa do potrzebnych nam danych"""
    # stations_data = data.get("stations", {})
    # trains_data = data.get("trains", [])

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
        sched_info = sched_stations.get(st.get("stationId"), {})

        is_confirmed = st.get('isConfirmed', False)
        planned_arr = sched_info.get('arrivalTime')
        planned_dep = sched_info.get('departureTime')
        actual_arr = st.get('actualArrival')
        actual_dep = st.get('actualDeparture')

        # planned_arr_date, planned_arr_time = split_datetime(planned_arr)
        # planned_dep_date, planned_dep_time = split_datetime(planned_dep)
        actual_arr_date, actual_arr_time = split_datetime(actual_arr)
        actual_dep_date, actual_dep_time = split_datetime(actual_dep)

        arr_platform = sched_info.get('arrivalPlatform')
        arr_track = sched_info.get('arrivalTrack')

        dep_platform = sched_info.get('departurePlatform')
        dep_track = sched_info.get('departureTrack')

        arrival_delay = calculate_delay(planned_arr, actual_arr)
        departure_delay = calculate_delay(planned_dep,actual_dep)

        station_info = {
            "name": st_name,

            # "planned_arrival_date": planned_arr_date,
            "planned_arrival_time": planned_arr,
            "actual_arrival_date": actual_arr_date,
            "actual_arrival_time": actual_arr_time,
            "arrival_platform": arr_platform,
            "arrival_track": arr_track,
            "arrival_delay": arrival_delay,

            # "planned_departure_date": planned_dep_date,
            "planned_departure_time": planned_dep,
            "actual_departure_date": actual_dep_date,
            "actual_departure_time": actual_dep_time,
            "departure_platform": dep_platform,
            "departure_track": dep_track,
            "departure_delay": departure_delay,

            "is_confirmed": is_confirmed
        }

        parsed["timeLine"].append(station_info)

        if is_confirmed:
            parsed["lastStation"] = st_name
            parsed["currentDelay"] = departure_delay or arrival_delay
        elif parsed["nextStation"] is None and parsed["lastStation"] is not None:
            parsed["nextStation"] = st_name

    return parsed
