import requests

def get_train_live(headers, schedule_id, order_id, date_str):
    """Pobiera dane na żywo o konkretnym pociągu."""
    url = f"https://pdp-api.plk-sa.pl/api/v1/operations/train/{schedule_id}/{order_id}/{date_str}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Błąd pobierania pociągu: {response.status_code}")
        return None
    return response.json()