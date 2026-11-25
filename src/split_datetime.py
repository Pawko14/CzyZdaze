

def split_datetime(dt_str):
    """Bezpiecznie rozdziela czas ISO (np. '2026-11-24T14:35:00') na ('2026-11-24', '14:35')."""
    if not dt_str or "T" not in dt_str:
        return None, None
    date_part, time_part = dt_str.split("T", 1)
    return date_part, time_part[:5]
