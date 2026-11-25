import json
import os
from pathlib import Path


def read_json_cache(filepath):
    """Bezpiecznie odczytuje plik cache JSON. Przy uszkodzeniu zwraca None zamiast błędu."""
    path = Path(filepath)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as err:
        print(f"Ostrzeżenie: uszkodzony plik cache ({path.name}): {err}. Pobieram dane ponownie.")
        return None


def write_json_cache(filepath, data, indent=None):
    """Zapisuje plik cache atomowo (przez plik .tmp), aby przerwanie zapisu go nie uszkodziło."""
    path = Path(filepath)
    tmp_path = path.with_name(f"{path.name}.tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        os.replace(tmp_path, path)
    except OSError as err:
        print(f"Ostrzeżenie: nie udało się zapisać cache ({path.name}): {err}")
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
