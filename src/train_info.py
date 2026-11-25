
def train_information(train_info):
    print("=" * 60)
    print(f" Pociąg ID: {train_info['orderId']} | Status: {train_info['trainStatus']}")
    print(f" Obecne opóźnienie: {train_info['currentDelay']} min")
    print(f" Ostatnia stacja: {train_info['lastStation']}")
    print(f" Następna stacja: {train_info['nextStation']}")
    print("=" * 60)
    print("Trasa:")
    for s in train_info["timeLine"]:
        ikona = "✔️" if s["is_confirmed"] else "⚪"
        arr_delay_str = f"(+{s['arrival_delay']} min)" if s["arrival_delay"] > 0 else "(o czasie)"
        dep_delay_str = f"(+{s['departure_delay']} min)" if s["departure_delay"] > 0 else "(o czasie)"
        arr_str = f"Przyjazd: {s['planned_arrival_time']} {arr_delay_str}" if s['planned_arrival_time'] else "Stacja początkowa"
        dep_str = f"Odjazd: {s['planned_departure_time']} {dep_delay_str}" if s['planned_departure_time'] else "Stacja końcowa"
        print(f"  {ikona} {s['name']:<28} | {arr_str:<30} | {dep_str}")

    return 