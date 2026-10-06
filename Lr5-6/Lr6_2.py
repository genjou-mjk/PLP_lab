import json
import os

students = [
    {
        "Name": "Vasiliy",
        "Surname": "Logvinov",
        "Patronymic": "Antonovich",
        "Adress": "Mira 5",
        "School": 9,
        "Class": 6,
    },
    {
        "Name": "Anton",
        "Surname": "Lipovyi",
        "Patronymic": "Andreevich",
        "Adress": "Naberezhnaya 10",
        "School": 10,
        "Class": 10,
    },
    {
        "Name": "Alina",
        "Surname": "Popovich",
        "Patronymic": "Viktorovna",
        "Adress": "Pushkina 5",
        "School": 10,
        "Class": 11,
    },
    {
        "Name": "Dmytro",
        "Surname": "Koval",
        "Patronymic": "Petrovych",
        "Adress": "Shevchenka 12",
        "School": 9,
        "Class": 7,
    },
    {
        "Name": "Sofia",
        "Surname": "Melnyk",
        "Patronymic": "Tarasivna",
        "Adress": "Kyivska 22",
        "School": 9,
        "Class": 7,
    },
    {
        "Name": "Maxim",
        "Surname": "Boyko",
        "Patronymic": "Sergiyovych",
        "Adress": "Haharina 3",
        "School": 9,
        "Class": 8,
    },
    {
        "Name": "Kateryna",
        "Surname": "Shevchenko",
        "Patronymic": "Petrivna",
        "Adress": "Sadova 15",
        "School": 10,
        "Class": 7,
    },
    {
        "Name": "Andriy",
        "Surname": "Bondarenko",
        "Patronymic": "Mykolayovych",
        "Adress": "Zarichna 8",
        "School": 9,
        "Class": 9,
    },
    {
        "Name": "Yuliia",
        "Surname": "Klymenko",
        "Patronymic": "Olexandrivna",
        "Adress": "Centralna 45",
        "School": 10,
        "Class": 8,
    },
    {
        "Name": "Oleh",
        "Surname": "Tkachenko",
        "Patronymic": "Ivanovych",
        "Adress": "Polova 11",
        "School": 9,
        "Class": 7,
    },
]

JSON_FILENAME = "data.json"
FILTERED_FILENAME = "filtered_students.json"


def save_initial_data():
  with open(JSON_FILENAME, "wt", encoding="utf-8") as file:
    json.dump(students, file, ensure_ascii=False, indent=4)
  print(f"Початкові дані (розширений список) успішно записано у файл '{JSON_FILENAME}'.")


def load_data():
  if not os.path.exists(JSON_FILENAME) or os.path.getsize(JSON_FILENAME) == 0:
    save_initial_data()

  try:
    with open(JSON_FILENAME, "rt", encoding="utf-8") as file:
      return json.load(file)
  except json.JSONDecodeError:
    print("Файл JSON пошкоджено або порожній. Відновлюємо початкові дані...")
    save_initial_data()
    with open(JSON_FILENAME, "rt", encoding="utf-8") as file:
      return json.load(file)


def search_and_save(data):
  try:
    target_school = int(
        input("Введіть номер школи для пошуку (наприклад, 9 або 10): ").strip()
    )
  except ValueError:
    print("Некоректний ввід. Потрібно ввести ціле число.")
    return

  result = [
      s
      for s in data
      if s["School"] == target_school and s["Class"] in [7, 8]
  ]

  if result:
    with open(FILTERED_FILENAME, "wt", encoding="utf-8") as file:
      json.dump(result, file, ensure_ascii=False, indent=4)
    print(f"Знайдено учнів: {len(result)}. Результати збережено у '{FILTERED_FILENAME}'.")
  else:
    print("Учнів за заданими критеріями (школа + класи 7, 8) не знайдено.")


if __name__ == "__main__":
  save_initial_data()
  data = load_data()
  search_and_save(data)