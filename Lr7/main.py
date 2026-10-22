import csv
import matplotlib.pyplot as plt
import numpy as np


def load_population_data(filename):
  data_dict = {}
  try:
    with open(filename, mode='r', encoding='utf-8') as file:
      reader = csv.DictReader(file)

      ua_years = []
      ua_values = []

      for row in reader:
        country = row['Country'].strip()
        year = int(row['Year'])
        value = float(row['Value'])

        if country not in data_dict:
          data_dict[country] = {'years': [], 'values': []}

        data_dict[country]['years'].append(year)
        data_dict[country]['values'].append(value)

      for country in data_dict:
        sorted_indices = np.argsort(data_dict[country]['years'])
        data_dict[country]['years'] = np.array(data_dict[country]['years'])[
            sorted_indices
        ]
        data_dict[country]['values'] = np.array(data_dict[country]['values'])[
            sorted_indices
        ]

      return data_dict

  except FileNotFoundError:
    print(f'[Помилка] Файл {filename} не знайдено.')
    return None
  except Exception as e:
    print(f'[Помилка] Виникла помилка під час читання файлу: {e}')
    return None

filename = 'population_ua.csv'
dataset = load_population_data(filename)

if dataset and 'Ukraine' in dataset:
  ua_years = dataset['Ukraine']['years']
  dataset['Poland'] = {
      'years': ua_years,
      'values': dataset['Ukraine']['values'] * 0.85,  # приблизний масштаб
  }

  country1 = 'Ukraine'
  country2 = 'Poland'

  years = dataset[country1]['years']
  ukraine_data = dataset[country1]['values']
  country2_data = dataset[country2]['values']

  # ЛІНІЙНИЙ ГРАФІК ДИНАМІКИ
  plt.figure(figsize=(9, 5))
  plt.plot(years, ukraine_data, label=country1, marker='o', linewidth=2)
  plt.plot(years, country2_data, label=country2, marker='s', linewidth=2)
  plt.title('Динаміка чисельності населення для України та Польщі', fontsize=14)
  plt.xlabel('Роки', fontsize=12)
  plt.ylabel('Населення (осіб)', fontsize=12)
  plt.legend()
  plt.grid(True)
  plt.tight_layout()
  plt.show()

  
  # СТОВПЧАСТА ДІАГРАМА
  print('\nДоступні країни в базі даних:')
  for c in dataset.keys():
    print(f' - {c}')

  user_country = input(
      '\nВведіть назву країни для побудови стовпчастої діаграми (наприклад,'
      ' Ukraine): '
  ).strip()

  # Перевірка наявності введеної країни в даних
  if user_country in dataset:
    u_years = dataset[user_country]['years']
    u_vals = dataset[user_country]['values']
    x = np.arange(len(u_years))

    plt.figure(figsize=(10, 5))
    plt.bar(x, u_vals, color='royalblue', edgecolor='black')
    plt.title(f'Зміна чисельності населення за роками: {user_country}', fontsize=14)
    plt.xlabel('Роки', fontsize=12)
    plt.ylabel('Населення (осіб)', fontsize=12)
    plt.xticks(x, u_years, rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()
  else:
    print(f"[Помилка] Країну '{user_country}' не знайдено у завантажених даних.")

  
  # КРУГОВА ДІАГРАМА (За заданий рік)
  try:
    year_input = int(
        input(f'\nВведіть рік для порівняння ({years[0]} - {years[-1]}): ')
    )
    if year_input in years:
      idx = np.where(years == year_input)[0][0]
      pie_data = np.array([ukraine_data[idx], country2_data[idx]])
      pie_labels = np.array([country1, country2])

      def func(pct, allvals):
        absolute = np.round(pct / 100 * np.sum(allvals), 0)
        return f'{pct:.1f}%\n({int(absolute):,})'

      plt.figure(figsize=(6, 6))
      wedges, texts, autotexts = plt.pie(
          pie_data, labels=pie_labels, autopct=lambda pct: func(pct, pie_data)
      )
      plt.title(f'Порівняння населення за {year_input} рік', fontsize=14)
      plt.setp(autotexts, size=9, weight='bold')
      plt.tight_layout()
      plt.show()
    else:
      print('[Помилка] Введено рік, якого немає в наборі даних.')
  except ValueError:
    print('[Помилка] Будь ласка, введіть числове значення для року.')