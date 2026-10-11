from algorithm import dijkstra
from db import get_all_routes, init_db, save_actual, save_route
from map import EDGES, LOCATIONS, generate_map

city_map = generate_map()
MIN_TRIPS = 5


def main():
    init_db()
    print("Точки:", ", ".join(f"{code} {name}" for code, name in LOCATIONS.items()))

    while True:
        try:
            menu = int(input(
                "===== AI NAVIGATOR =====\n"
                "1. Знайти маршрут\n"
                "2. Додати результат проходження\n"
                "3. Історія маршрутів\n"
                "4. Статистика\n"
                "5. AI-рекомендація\n"
                "6. Мапа міста\n"
                "0. Вихід\n"
            ))
        except ValueError:
            print("Введіть номер пункту.")
            continue

        match menu:
            case 0:
                break
            case 1:
                find_and_save()
            case 2:
                add_actual()
            case 3:
                show_history()
            case 4:
                show_statistics()
            case 5:
                show_ai()
            case 6:
                show_map()
            case _:
                print("Немає такого пункту.")

        input("Press Enter to continue: ")


def find_and_save():
    start = input("Початкова точка: ").strip().upper()
    finish = input("Кінцева точка: ").strip().upper()
    return calculate(start, finish)


def calculate(start, finish):
    if start not in LOCATIONS or finish not in LOCATIONS:
        print("Такі місця не знайдені")
        return None
    if start == finish:
        print("Початкова і кінцева точки мають відрізнятися.")
        return None

    result = dijkstra(city_map, start, finish)
    if result is None:
        return None

    print_route(result)
    save_route(
        start,
        finish,
        result["path"],
        result["total_distance"],
        result["total_time"],
        int(round(result["avg_traffic"])),
    )
    return result


def print_route(result):
    print(" - ".join(result["path"]))
    print(" - ".join(result["path_names"]))
    print(f"Відстань: {result['total_distance']} км")
    print(f"Час: {result['total_time']} хв.")
    print(f"Середні затори: {result['avg_traffic']}")


def add_actual():
    routes = get_all_routes()
    if not routes:
        print("Ще немає маршрутів. Спочатку знайдіть маршрут.")
        return

    for row in routes:
        path = " - ".join(row["route"])
        if row["actual_time"] is None:
            fact = "факт ще не вказано"
        else:
            fact = f"факт {row['actual_time']} хв."
        print(f"#{row['id']}  {path}  прогноз {row['time']} хв., {fact}")

    raw = input("Номер запису: ").strip()
    if not raw.isdigit():
        print("Потрібен номер запису.")
        return

    try:
        actual_time = float(input("Фактичний час, хв.: ").replace(",", "."))
        actual_distance = float(input("Фактична відстань, км: ").replace(",", "."))
    except ValueError:
        print("Потрібне число.")
        return
    if actual_time <= 0 or actual_distance <= 0:
        print("Потрібне додатне число.")
        return

    save_actual(int(raw), actual_time, actual_distance)


def show_history():
    routes = get_all_routes()
    if not routes:
        print("Історія ще порожня.")
        return

    for row in routes:
        path = " - ".join(row["route"])
        if row["actual_time"] is None:
            fact = "факт не вказано"
        else:
            fact = f"факт {row['actual_time']} хв., {row['actual_distance']} км"
        print(
            f"#{row['id']}  {row['created_at']}  {row['start_point']} - {row['finish_point']}  "
            f"{path}  {row['distance']} км, прогноз {row['time']} хв., {fact}"
        )


def show_statistics():
    routes = get_all_routes()
    if not routes:
        print("Історія ще порожня.")
        return

    print(f"Записів у базі: {len(routes)}")
    groups = {}
    for row in routes:
        key = (row["start_point"], row["finish_point"], tuple(row["route"]))
        groups.setdefault(key, []).append(row)

    finished = []
    popular_path = None
    popular_count = 0
    for (start, finish, path), items in groups.items():
        count = len(items)
        avg_time = sum(item["time"] for item in items) / count
        avg_distance = sum(item["distance"] for item in items) / count
        actuals = [item for item in items if item["actual_time"] is not None]

        print(f"Маршрут {start} - {finish}")
        print(" - ".join(path))
        print(f"Використано: {count} разів")
        print(f"Середній час: {round(avg_time, 1)} хв.")
        print(f"Середня відстань: {round(avg_distance, 1)} км")
        if actuals:
            avg_actual = sum(item["actual_time"] for item in actuals) / len(actuals)
            avg_delay = sum(item["actual_time"] - item["time"] for item in actuals) / len(actuals)
            print(f"Середній фактичний час: {round(avg_actual, 1)} хв.")
            print(f"Різниця прогноз/факт: {round(avg_delay, 1)} хв.")
            finished.append((path, avg_actual))
        print()

        if count > popular_count:
            popular_count = count
            popular_path = path

    print(f"Найпопулярніший маршрут: {' - '.join(popular_path)} ({popular_count} разів)")
    if not finished:
        print("Фактичних проходжень ще немає, тож найшвидший і найповільніший шлях порахувати не можна.")
        return

    fastest = min(finished, key=lambda item: item[1])
    slowest = max(finished, key=lambda item: item[1])
    print(f"Найшвидший маршрут: {' - '.join(fastest[0])} ({round(fastest[1], 1)} хв.)")
    print(f"Найповільніший маршрут: {' - '.join(slowest[0])} ({round(slowest[1], 1)} хв.)")


def show_ai():
    start = input("Початкова точка: ").strip().upper()
    finish = input("Кінцева точка: ").strip().upper()
    result = calculate(start, finish)
    if result is None:
        return
    print()
    print_advice(start, finish, result)


def print_advice(start, finish, result):
    groups = {}
    for row in get_all_routes():
        if row["actual_time"] is None:
            continue
        if row["start_point"] != start or row["finish_point"] != finish:
            continue
        groups.setdefault(tuple(row["route"]), []).append(row)

    print("Аналіз історії:")
    if not groups:
        print("Завершених проходжень ще немає, залишаю маршрут Дейкстри.")
        return

    best_key = None
    best_avg = None
    for key, items in groups.items():
        avg_actual = sum(item["actual_time"] for item in items) / len(items)
        avg_plan = sum(item["time"] for item in items) / len(items)
        print(" - ".join(key))
        print(f"len(items) проходжень")
        print(f"Середній фактичний час: {round(avg_actual, 1)} хв.")
        print(f"Очікуваний час: {round(avg_plan, 1)} хв.")
        print()
        if len(items) >= MIN_TRIPS and (best_avg is None or avg_actual < best_avg):
            best_avg = avg_actual
            best_key = key

    dijkstra_key = tuple(result["path"])
    own = groups.get(dijkstra_key)
    if own and len(own) >= MIN_TRIPS:
        avg_actual = sum(item["actual_time"] for item in own) / len(own)
        avg_plan = sum(item["time"] for item in own) / len(own)
        if avg_plan and avg_actual > avg_plan * 1.15:
            percent = round((avg_actual / avg_plan - 1) * 100)
            if 20 <= percent <= 25:
                extra = "додаткові 20-25% часу"
            else:
                extra = f"додаткові близько {percent}% часу"
            names = " - ".join(dijkstra_key)
            print(f"Маршрут {names} часто займає більше часу, ніж прогнозує алгоритм. Рекомендується враховувати {extra}.")
            print()

    print("AI:")
    print("Рекомендований маршрут:")
    if best_key is None:
        print(" - ".join(dijkstra_key))
        print("Причина:")
        print("історії ще замало. Потрібно хоча б 5 проходжень одного шляху.")
        return
    if best_key == dijkstra_key:
        print(" - ".join(dijkstra_key))
        print("Причина:")
        print("історія не показує швидшого варіанту, залишаю маршрут Дейкстри.")
        return

    own_avg = result["total_time"]
    if own and len(own) >= MIN_TRIPS:
        own_avg = sum(item["actual_time"] for item in own) / len(own)
    saved_min = own_avg - best_avg
    if saved_min < 1:
        print(" - ".join(dijkstra_key))
        print("Причина:")
        print("історія не показує швидшого варіанту, залишаю маршрут Дейкстри.")
        return

    diff_km = round(path_distance(best_key) - result["total_distance"], 1)
    print(" - ".join(best_key))
    print("Причина:")
    if diff_km > 0:
        print(f"цей маршрут на {diff_km} км довший,")
        print("але за історичними даними в середньому")
        print(f"дозволяє дістатися швидше на {round(saved_min, 1)} хв.")
    elif diff_km < 0:
        print(f"цей маршрут на {abs(diff_km)} км коротший")
        print(f"і за історичними даними в середньому швидший на {round(saved_min, 1)} хв.")
    else:
        print(f"відстань та сама, а за історією він швидший на {round(saved_min, 1)} хв.")


def path_distance(path):
    total = 0
    for i in range(len(path) - 1):
        total += city_map[path[i]][path[i + 1]]["distance"]
    return total


def show_map():
    for code, name in LOCATIONS.items():
        print(f"{code} - {name}")
    print("Дороги:")
    for src, dst, attrs in EDGES:
        print(
            f"{src} - {dst}: {attrs['distance']} км, {attrs['time']} хв., "
            f"затори {attrs['traffic']}, складність {attrs['difficulty']}"
        )


if __name__ == "__main__":
    main()