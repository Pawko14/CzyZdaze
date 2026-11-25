import requests


def api_get(url, headers, timeout=15, not_found_ok=False):
    """Wysyła bezpieczne zapytanie GET z timeoutem, obsługą sieci, HTTP 429 i JSON."""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.Timeout:
        print("Błąd sieci: przekroczono czas oczekiwania na odpowiedź serwera PKP PLK.")
        return None
    except requests.RequestException as err:
        print(f"Błąd połączenia z API: {err}")
        return None

    if response.status_code == 429:
        print("Przekroczono limit zapytań API (HTTP 429). Spróbuj ponownie później.")
        return None

    if response.status_code == 404 and not_found_ok:
        return None

    if response.status_code != 200:
        print(f"Błąd API (HTTP {response.status_code}) dla {url}")
        return None

    try:
        return response.json()
    except ValueError:
        print("Błąd: serwer zwrócił niepoprawny format JSON.")
        return None
