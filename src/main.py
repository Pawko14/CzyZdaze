import os
import datetime

from parse_train import parse_train
from load_env import load_env
from train_info import train_information
from search_trains import search_trains
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

    print("Jak chcesz wyszukać pociąg?")
    print("[1] Po nazwie (np. Hetman, Malinowski)")
    print("[2] Po numerze (np. 23112, 49011)")
    print("[3] Nazwa lub numer [domyślnie]")
    mode_choice = input("Wybór (1-3): ").strip()

    mode_map = {"1": "name", "2": "number", "3": "auto"}
    mode = mode_map.get(mode_choice, "auto")

    prompt_map = {
        "name": "Wpisz nazwę pociągu (np. Hetman, Malinowski): ",
        "number": "Wpisz numer pociągu (np. 23112, 49011, IC 35170): ",
        "auto": "Wpisz nazwę lub numer pociągu (np. Hetman, 23112, 49011): ",
    }
    user_query = input(prompt_map[mode]).strip()
    if not user_query:
        print("Nie podano frazy wyszukiwania!")
        return

    date_str = datetime.date.today().isoformat()

    matches = search_trains(
        headers=headers,
        query=user_query,
        date_str=date_str,
        stations_dict=stations_dict,
        mode=mode
    )

    if not matches:
        print("Nie znaleziono połączeń na ten dzień.")
        return

    print(f"\nZnaleziono {len(matches)} kurs(y):")
    for idx, m in enumerate(matches, 1):
        details = m["details"]
        name_part = f" „{details['name']}”" if details["name"] else ""
        dep_part = f" ({details['departureTime']})" if details["departureTime"] else ""
        print(f"[{idx}] {details['fullNumber']}{name_part} | Wyjazd: {m['operatingDate']}{dep_part} | {details['relation']}")

    wybor = 1
    wybor_input = input(f"Wybierz numer kursu (1-{len(matches)}) [domyślnie 1]: ").strip()
    if wybor_input.isdigit() and 1 <= int(wybor_input) <= len(matches):
        wybor = int(wybor_input)

    selected = matches[wybor - 1]
    details = selected["details"]
    train_date = selected["operatingDate"]
    name_part = f" „{details['name']}”" if details["name"] else ""

    print(f"\nPobieram dane na żywo dla: {details['fullNumber']}{name_part} (kurs z {train_date})...")

    sched_stations = {str(s["stationId"]): s for s in details["stations"]}

    # Pobieramy dane live dla WŁAŚCIWEJ daty wyjazdu tego pociągu!
    live_data = get_train_live(headers, selected["scheduleId"], selected["orderId"], date_str=train_date)

    if live_data:
        train_info = parse_train(live_data, sched_stations, stations_data=stations_dict)
        if train_info:
            train_information(train_info)
    else:
        print("Nie udało się pobrać danych na żywo (pociąg mógł jeszcze nie wyruszyć lub wystąpił błąd połączenia).")


if __name__ == "__main__":
    main()
