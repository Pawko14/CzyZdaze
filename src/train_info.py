
def format_delay(minutes, in_header=False):
    """Formatuje różnicę czasu (opóźnienie / o czasie / przed czasem) na czytelny tekst."""
    if minutes > 0:
        text = f"+{minutes} min"
    elif minutes < 0:
        text = f"-{abs(minutes)} min"
    else:
        text = "0 min (o czasie)" if in_header else "o czasie"
    return text if in_header else f"({text})"


def _format_stop_event(label, planned_time, delay, is_terminal, terminal_text, stop_type):
    """Formatuje przyjazd lub odjazd z rozróżnieniem stacji krańcowych i typów postoju."""
    if planned_time:
        return f"{label}: {planned_time} {format_delay(delay)}"
    if is_terminal:
        return terminal_text
    if stop_type:
        return stop_type.capitalize()
    return "Brak danych"


def train_information(train_info):
    last_station = train_info["lastStation"] or "Brak (przed odjazdem)"
    next_station = train_info["nextStation"] or "Brak (koniec trasy lub przed odjazdem)"

    print("=" * 60)
    print(f" Pociąg ID: {train_info['orderId']} | Status: {train_info['trainStatus']}")
    print(f" Obecne opóźnienie: {format_delay(train_info['currentDelay'], in_header=True)}")
    print(f" Ostatnia stacja: {last_station}")
    print(f" Następna stacja: {next_station}")
    print("=" * 60)
    print("Trasa:")
    timeline = train_info["timeLine"]
    total = len(timeline)
    for idx, s in enumerate(timeline):
        ikona = "✔️" if s["is_confirmed"] else "⚪"
        stop_type = s.get("stop_type")
        is_first = s.get("is_first", idx == 0)
        is_last = s.get("is_last", idx == total - 1)

        arr_str = _format_stop_event(
            "Przyjazd", s["planned_arrival_time"], s["arrival_delay"],
            is_first, "Stacja początkowa", stop_type
        )
        dep_str = _format_stop_event(
            "Odjazd", s["planned_departure_time"], s["departure_delay"],
            is_last, "Stacja końcowa", stop_type
        )
        print(f"  {ikona} {s['name']:<28} | {arr_str:<35} | {dep_str}")

    return 