import datetime

from api_client import api_get
from cache_utils import read_json_cache, write_json_cache
from config import PROJECT_ROOT


def _cleanup_old_schedule_caches(reference_date_str, keep_days=2):
    """Usuwa pliki schedules_cache_*.json starsze niż keep_days względem podanej daty."""
    cutoff = datetime.date.fromisoformat(reference_date_str) - datetime.timedelta(days=keep_days)
    for path in PROJECT_ROOT.glob("schedules_cache_*.json"):
        date_part = path.stem.removeprefix("schedules_cache_")
        try:
            file_date = datetime.date.fromisoformat(date_part)
        except ValueError:
            continue
        if file_date < cutoff:
            path.unlink(missing_ok=True)


def get_schedules_for_day(headers, date_str):
    """
    Pobiera pełny rozkład tras na podany dzień (z numerami nationalNumber, nazwami i stacjami).
    Korzysta z lokalnego pliku cache, aby oszczędzać limit zapytań API.
    """
    cache_file = PROJECT_ROOT / f"schedules_cache_{date_str}.json"

    cached = read_json_cache(cache_file)
    if isinstance(cached, list):
        return cached

    print(f"Pobieram pełny rozkład na dzień {date_str} (może to zająć kilka sekund)...")
    url = f"https://pdp-api.plk-sa.pl/api/v1/schedules?dateFrom={date_str}&dateTo={date_str}&dictionaries=false"
    data = api_get(url, headers=headers, timeout=30)
    if not data:
        return []

    routes = data.get("routes", [])
    # Zapis bez wcięć (indent), żeby plik cache zajmował mniej miejsca i szybciej się ładował
    write_json_cache(cache_file, routes)
    _cleanup_old_schedule_caches(date_str)

    return routes
