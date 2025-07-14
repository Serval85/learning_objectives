# Заполнить рюкзак вещами с максимальной полезностью с максимальным весом n кг,
# часть веса должны занимать самые тяжелые вещи, но не более FN% (задавать например так: 0.7)
# Пример набора вещей с их характеристиками (вес и ценность)
items = {
    'зажигалка': {'weight': 20, 'value': 5},
    'компас': {'weight': 100, 'value': 7},
    'фрукты': {'weight': 500, 'value': 8},
    'рубашка': {'weight': 300, 'value': 6},
    'термос': {'weight': 1000, 'value': 9},
    'аптечка': {'weight': 200, 'value': 10},
    'куртка': {'weight': 600, 'value': 7},
    'бинокль': {'weight': 400, 'value': 8},
    'удочка': {'weight': 1200, 'value': 6},
    'салфетки': {'weight': 40, 'value': 3},
    'бутерброды': {'weight': 820, 'value': 9},
    'палатка': {'weight': 5500, 'value': 8},
    'спальный мешок': {'weight': 2250, 'value': 7},
    'жвачка': {'weight': 10, 'value': 2}
}


def pack_backpack(things: dict, max_kg: int = 10, fraction_heavy: float = 0.7) -> list:
    """
    Функция упаковывает рюкзак, выбирая наиболее ценные предметы с учётом ограничения по весу.
    Часть рюкзака должна заполняться самыми тяжелыми предметами.

    Args:
        things (dict): Словарь всех возможных предметов с параметрами ('weight', 'value').
        max_kg (int): Общий максимальный вес рюкзака в килограммах.
        fraction_heavy (float): Доля общего веса, зарезервированная под самые тяжелые предметы.

    Returns:
        list[tuple]: Список отобранных предметов с их названием, весом и ценностью.
    """
    # Перевод максимального веса рюкзака в граммы
    total_capacity = max_kg * 1000

    # Выделяем объем рюкзака под тяжелые предметы
    reserved_for_heavy = total_capacity * fraction_heavy
    print(f"Максимальный вес рюкзака в граммах: {total_capacity}\n"
          f"Доля, предназначенная исключительно для тяжелых предметов: {reserved_for_heavy:.2f}")

    # Составляем список всех предметов по параметру полезности (отношение value/weight)
    value_ratio_sorted = sorted(
        [(item_name, item['value'] / item['weight'], item['weight'], item['value'])
         for item_name, item in things.items()],
        key=lambda x: x[1],  # Сначала берем наиболее ценные предметы
        reverse=True
    )

    # Получаем список самых тяжелых предметов
    heavy_items = sorted(
        [(item_name, item['weight'], item['value'])
         for item_name, item in things.items() if item['weight'] > 0],
        key=lambda x: x[1],  # Самые тяжелые идут первыми
        reverse=True
    )

    # Берём тяжелые предметы в пределах выделенной доли веса
    selected_heavy_items = []
    remaining_weight = reserved_for_heavy
    for name, weight, value in heavy_items:
        if weight <= remaining_weight:
            selected_heavy_items.append((name, weight, value))  # Включили в список тяжелый предмет
            remaining_weight -= weight
        else:
            break

    # Высчитываем свободное место после загрузки тяжелых предметов
    free_space = total_capacity - sum(w for _, w, v in selected_heavy_items)

    # Теперь добавляем остальные предметы, руководствуясь принципом максимальной ценности
    final_selection = selected_heavy_items[:]
    for name, ratio, weight, value in value_ratio_sorted:
        if any(n == name for n, _, _ in final_selection):
            continue  # Этот предмет уже включен

        if weight <= free_space:
            final_selection.append((name, weight, value))  # Добавляем полезный легкий предмет
            free_space -= weight

    return final_selection


if __name__ == "__main__":
    result = pack_backpack(items, 10, 0.7)
    print("\nВыбранные предметы:")
    for item in result:
        print(f"{item[0]} | Вес: {item[1]} г | Ценность: {item[2]}")
