import csv
import os


def find_population_extremes(
    input_filename="population_ua.csv", output_filename="population_extremes.csv"
):
  try:
    if not os.path.exists(input_filename):
      raise FileNotFoundError(f"Файл {input_filename} не знайдено!")

    with open(input_filename, mode="r", encoding="utf-8") as file:
      reader = csv.DictReader(file)
      rows = list(reader)
      valid_rows = []
      for row in rows:
        try:
          val_str = row.get("Value")
          if val_str and val_str != "None":
            row["Value_num"] = float(val_str)
            valid_rows.append(row)
        except ValueError:
          continue

      if not valid_rows:
        print("У файлі немає числових даних.")
        return

      min_record = min(valid_rows, key=lambda x: x["Value_num"])
      max_record = max(valid_rows, key=lambda x: x["Value_num"])

      print(f"Найнижчий: рік {min_record['Year']} — {min_record['Value']}")
      print(f"Найвищий: рік {max_record['Year']} — {max_record['Value']}")

      with open(
          output_filename, mode="w", newline="", encoding="utf-8"
      ) as out_file:
        fieldnames = [
            "Country",
            "Country Code",
            "Indicator",
            "Indicator Code",
            "Year",
            "Value",
        ]
        writer = csv.DictWriter(
            out_file, fieldnames=fieldnames, delimiter=";"
        )
        writer.writeheader()
        for record in [min_record, max_record]:
          writer.writerow({k: record.get(k) for k in fieldnames})
      print(f"Результати збережено у {output_filename}")

  except FileNotFoundError as e:
    print(f"Помилка: {e}")
  except Exception as e:
    print(f"Непередбачена помилка: {e}")


if __name__ == "__main__":
  find_population_extremes()