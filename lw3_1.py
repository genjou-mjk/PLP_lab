students_heights = {
    "Шевченко": 188,
    "Коваленко": 184,
    "Бондаренко": 181,
    "Ткаченко": 178,
    "Кравченко": 175,
    "Олійник": 172,
    "Шевчук": 169,
    "Поліщук": 166,
    "Лисенко": 163,
    "Захарченко": 160
}


def print_all_students(data: dict) -> None:
    if not data:
        print("Словник порожній.")
        return
    print("\n--- Список учнів класу та їх зріст ---")
    for surname, height in data.items():
        print(f"Прізвище: {surname:<12} | Зріст: {height} см")


def add_student(data: dict) -> None:
    surname = input("Введіть прізвище нового учня: ").strip().capitalize()
    if not surname:
        print("Помилка: Прізвище не може бути порожнім.")
        return
    if surname in data:
        print(f"Запис для учня '{surname}' вже існує!")
        return

    try:
        height = int(input("Введіть зріст учня (см): "))
        if height <= 0:
            raise ValueError("Зріст повинен бути додатним числом.")
        data[surname] = height
        print(f"Учня {surname} успішно додано.")
    except ValueError as e:
        print(f"Помилка введення даних: {e}")


def delete_student(data: dict) -> None:
    surname = input("Введіть прізвище учня для видалення: ").strip().capitalize()
    try:
        del data[surname]
        print(f"Учня '{surname}' успішно видалено.")
    except KeyError:
        print(f"Помилка: Учня з прізвищем '{surname}' не знайдено у словнику!")


def print_sorted_by_keys(data: dict) -> None:
    if not data:
        print("Словник порожній.")
        return
    print("\n--- Список учнів (відсортовано за прізвищем) ---")
    for surname in sorted(data.keys()):
        print(f"Прізвище: {surname:<12} | Зріст: {data[surname]} см")


def solve_variant_tasks(data: dict) -> None:
    if not data:
        print("Словник порожній.")
        return

    try:
        new_name = input("Введіть прізвище 'новенького': ").strip().capitalize()
        new_height = int(input("Введіть зріст 'новенького' (см): "))
    except ValueError:
        print("Помилка: Зріст має бути цілим числом!")
        return

    sorted_students = sorted(data.items(), key=lambda x: x[1], reverse=True)

    shorter_students = [name for name, h in sorted_students if h < new_height]

    after_student = None
    for name, h in sorted_students:
        if h > new_height:
            after_student = name
        else:
            break

    closest_student = min(sorted_students, key=lambda x: abs(x[1] - new_height))[0]

    print("\nРезультати:")
    print(f"а) Учні, зріст яких менший за {new_height} см:")
    if shorter_students:
        print("   " + ", ".join(shorter_students))
    else:
        print("   Немає таких учнів.")

    print("б) Запис для збереження впорядкованості за спаданням:")
    if after_student:
        print(f"   Новенького ({new_name}) потрібно записати після: {after_student}")
    else:
        print(f"   Новенького ({new_name}) потрібно записати першим у списку.")

    print("в) Учень, зріст якого найменше відрізняється від росту новенького:")
    print(f"   {closest_student} (зріст: {data[closest_student]} см)")


def main():
    while True:
        print("\n================ МЕНЮ =============")
        print("1. Вивести весь словник")
        print("2. Додати нового учня")
        print("3. Видалити учня")
        print("4. Переглянути словник, відсортований за прізвищами")
        print("5. Розв'язати завдання за варіантом")
        print("0. Вихід")
        print("===================================")

        choice = input("Оберіть пункт меню (0-5): ").strip()

        if choice == "1":
            print_all_students(students_heights)
        elif choice == "2":
            add_student(students_heights)
        elif choice == "3":
            delete_student(students_heights)
        elif choice == "4":
            print_sorted_by_keys(students_heights)
        elif choice == "5":
            solve_variant_tasks(students_heights)
        elif choice == "0":
            break
        else:
            print("Некоректний вибір.")


if __name__ == "__main__":
    main()