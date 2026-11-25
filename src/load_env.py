import os


env_path = os.path.abspath('.env')


def load_env(filepath= env_path):
    if not os.path.exists(filepath):
        raise FileNotFoundError("Nie znaleziono .env")

    with open(filepath) as f:
         for line in f:
             line = line.strip()
             key, val = line.split("=", 1)
             os.environ[key.strip()] = val.strip()
