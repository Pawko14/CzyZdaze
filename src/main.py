import os
import datetime

from parse_train import parse_train
from load_env import load_env
from train_info import train_information
from search_train_by_name import search_train_by_name
from get_train_live import get_train_live
from stations import get_stations_dict


def main():
    load_env()
    PKL_API = os.getenv("PLK_API")

    if not PKL_API:
        print("PKL_API nie znalezione!")
        return

    PKL_API = PKL_API.strip().strip('"').strip("'")

    headers = {
        "Authorization": f"Bearer {PKL_API}",
        "Accept": "application/json"
    }

    stations_dict = get_stations_dict(headers=headers)

    user_query = input("Wpisz nazwę pociągu (np. Hetman, Malinowski): ").strip()
    if not user_query:
        print("Nie podano nazwy!")
        return

    date_str = datetime.date.today().isoformat()

    matches = search_train_by_name(
        headers=headers,
        train_name=user_query,
        date_str=date_str,
        stations_dict=stations_dict
    )

    if not matches:
        print("Nie znaleziono połączeń na ten dzień.")
        return

    print(f"\nZnaleziono {len(matches)} kurs(y):")
    for idx, m in enumerate(matches, 1):
        details = m["details"]
        print(f"[{idx}] {details['fullNumber']} {m.get('name')} | Wyjazd: {m['operatingDate']} | {details['relation']}")

    wybor = 1
    wybor_input = input(f"Wybierz numer kursu (1-{len(matches)}) [domyślnie 1]: ").strip()
    if wybor_input.isdigit() and 1 <= int(wybor_input) <= len(matches):
        wybor = int(wybor_input)

    selected = matches[wybor - 1]
    train_date = selected["operatingDate"]

    print(f"\nPobieram dane na żywo dla: {selected.get('name')} (kurs z {train_date})...")

    sched_stations = {s["stationId"]: s for s in selected["details"]["stations"]}

    # Pobieramy dane live dla WŁAŚCIWEJ daty wyjazdu tego pociągu!
    live_data = get_train_live(headers, selected["scheduleId"], selected["orderId"], date_str=train_date)

    if live_data:
        train_info = parse_train(live_data, sched_stations, stations_data=stations_dict)
        if train_info:
            train_information(train_info)
    else:
        print("Nie udalo sie pobrac danych")


if __name__ == "__main__":
    main()
