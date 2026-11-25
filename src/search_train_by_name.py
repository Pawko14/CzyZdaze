import datetime
import requests

from stations import get_route_details


def search_train_by_name(headers, train_name, date_str, stations_dict):
    """
    Pobiera katalog tras na podany dzień oraz dzień poprzedni.
    Z dnia poprzedniego zostawia wyłącznie pociągi przechodzące przez północ
    (crosses_midnight == True). Do każdego wyniku dopisuje operatingDate i details.
    """
    target_date = datetime.date.fromisoformat(date_str)
    yesterday_str = (target_date - datetime.timedelta(days=1)).isoformat()

    matches = []

    for day in [yesterday_str, date_str]:
        url = f"https://pdp-api.plk-sa.pl/api/v1/schedules/routes/{day}"
        print(f"Pobieram katalog tras na dzień {day}...")

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Błąd pobierania katalogu ({day}): {response.status_code}")
            continue

        all_routes = response.json().get("routes", [])

        for r in all_routes:
            if r.get("name") and train_name.lower() in r["name"].lower():
                details = get_route_details(
                    headers=headers,
                    schedule_id=r.get("scheduleId"),
                    order_id=r.get("orderId"),
                    stations_dict=stations_dict
                )
                if not details:
                    continue

                # Wczorajsze pociągi kończące bieg przed północą nie jadą już w podanym dniu
                if day == yesterday_str and not details["crosses_midnight"]:
                    continue

                r["operatingDate"] = day
                r["details"] = details
                matches.append(r)

    return matches