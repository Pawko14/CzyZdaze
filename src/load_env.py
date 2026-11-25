import os

from config import PROJECT_ROOT


def load_env(filepath=None):
    """Wczytuje zmienne środowiskowe z pliku .env (pomija puste linie i komentarze #)."""
    env_file = filepath if filepath is not None else PROJECT_ROOT / ".env"
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Nie znaleziono pliku {env_file}")

    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")
