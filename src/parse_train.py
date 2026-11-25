import datetime

from split_datetime import split_datetime

def calculate_delay(planned_time, actual_time, operating_date=None, day_offset=0, allow_early=True):
    """
    Liczy różnicę w minutach między czasem planowanym ('07:40:00')
    a rzeczywistym ('2026-11-25T07:42:00').
    Wartość dodatnia oznacza opóźnienie, ujemna przyjazd przed czasem, 0 oznacza punktualność.
    """
    if not planned_time or not actual_time:
        return 0

    actual_dt = datetime.datetime.fromisoformat(actual_time)
    if actual_dt.tzinfo is not None:
        # Normalizacja do lokalnego czasu bez strefy, aby uniknąć TypeError przy odejmowaniu
        actual_dt = actual_dt.astimezone().replace(tzinfo=None)
    planned_t = datetime.time.fromisoformat(planned_time)

    if operating_date:
        planned_date = datetime.date.fromisoformat(operating_date) + datetime.timedelta(days=day_offset or 0)
        planned_dt = datetime.datetime.combine(planned_date, planned_t)
        diff_minutes = int((actual_dt - planned_dt).total_seconds() / 60)
    else:
        # Fallback gdy brak operatingDate: okno [-2h, +22h] wokół doby
        planned_dt = datetime.datetime.combine(actual_dt.date(), planned_t)
        diff_minutes = int((actual_dt - planned_dt).total_seconds() / 60)
        if diff_minutes < -120:
            diff_minutes += 1440
        elif diff_minutes > 1320:
            diff_minutes -= 1440

    return diff_minutes if allow_early else max(0, diff_minutes)


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
    total_stations = len(stations)

    for idx, st in enumerate(stations):
        st_id = str(st.get('stationId'))
        st_name = stations_data.get(st_id, f"Stacja #{st_id}")
        sched_info = sched_stations.get(st_id, {})

        is_confirmed = st.get('isConfirmed', False)
        stop_type = sched_info.get('stopTypeName')
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

        operating_date = train.get("operatingDate")
        arr_day = sched_info.get("arrivalDay") or 0
        dep_day = sched_info.get("departureDay") or 0

        arrival_delay = calculate_delay(
            planned_arr, actual_arr,
            operating_date=operating_date, day_offset=arr_day, allow_early=True
        )
        departure_delay = calculate_delay(
            planned_dep, actual_dep,
            operating_date=operating_date, day_offset=dep_day, allow_early=False
        )

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

            "stop_type": stop_type,
            "is_first": idx == 0,
            "is_last": idx == total_stations - 1,
            "is_confirmed": is_confirmed
        }

        parsed["timeLine"].append(station_info)

        if is_confirmed:
            parsed["lastStation"] = st_name
            # Jeśli stacja ma rozkładowy i rzeczywisty odjazd, odjazd odzwierciedla ewentualne nadrobienie postoju
            if planned_dep is not None and actual_dep is not None:
                parsed["currentDelay"] = departure_delay
            elif planned_arr is not None and actual_arr is not None:
                parsed["currentDelay"] = arrival_delay
        elif parsed["nextStation"] is None and parsed["lastStation"] is not None:
            parsed["nextStation"] = st_name

    return parsed
