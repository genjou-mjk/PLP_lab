import csv
import json
import os
import requests


def fetch_world_bank_data(country_code, indicator, start_date, end_date):
  url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?date={start_date}:{end_date}&format=json"
  print(f"Виконується запит до URL: {url}")
  try:
    # Додано таймаут 10 секунд, щоб програма не зависала
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    print("Запит успішно виконано!")
    return response.json()
  except requests.exceptions.Timeout:
    print("Помилка: Перевищено час очікування (таймаут) запиту до сервера.")
    return None
  except requests.exceptions.RequestException as e:
    print(f"Помилка HTTP-запиту: {e}")
    return None


def save_json_file(data, filename="population_ua.json"):
  try:
    with open(filename, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Дані успішно збережено у JSON-файл: {filename}")
  except IOError as e:
    print(f"Помилка збереження файлу {filename}: {e}")


def convert_json_to_csv(json_filename, csv_filename="population_ua.csv"):
  try:
    if not os.path.exists(json_filename):
      print(f"Файл {json_filename} не знайдено.")
      return
    with open(json_filename, "r", encoding="utf-8") as f:
      data = json.load(f)
    if not isinstance(data, list) or len(data) < 2:
      print("Некоректна структура даних у JSON-файлі.")
      return
    records = data[1]
    with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
      writer = csv.writer(csv_file)
      writer.writerow([
          "Country",
          "Country Code",
          "Indicator",
          "Indicator Code",
          "Year",
          "Value",
      ])
      for item in records:
        country = item.get("country", {}).get("value")
        country_code = item.get("countryiso3code")
        indicator = item.get("indicator", {}).get("value")
        indicator_code = item.get("id")
        year = item.get("date")
        value = item.get("value")
        writer.writerow(
            [country, country_code, indicator, indicator_code, year, value]
        )
    print(f"Дані успішно перетворено та збережено у CSV-файл: {csv_filename}")
  except IOError as e:
    print(f"Помилка роботи з файлами: {e}")


def print_file_contents(filename, max_lines=15):
  print(f"\n--- Вміст файлу {filename} ---")
  try:
    with open(filename, "r", encoding="utf-8") as f:
      for i, line in enumerate(f):
        if i < max_lines:
          print(line, end="")
        else:
          print("... (виведено перші рядки)")
          break
  except IOError as e:
    print(f"Не вдалося прочитати файл {filename}: {e}")


if __name__ == "__main__":
  raw_data = fetch_world_bank_data("ua", "SP.POP.TOTL", 1991, 2019)
  if raw_data:
    save_json_file(raw_data, "population_ua.json")
    convert_json_to_csv("population_ua.json", "population_ua.csv")
    print_file_contents("population_ua.json", 10)
    print_file_contents("population_ua.csv", 10)
  else:
    print("Не вдалося отримати дані від API Світового банку.")