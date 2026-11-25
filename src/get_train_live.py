from api_client import api_get


def get_train_live(headers, schedule_id, order_id, date_str):
    """Pobiera dane na żywo o konkretnym pociągu."""
    url = f"https://pdp-api.plk-sa.pl/api/v1/operations/train/{schedule_id}/{order_id}/{date_str}"
    return api_get(url, headers=headers, not_found_ok=True)