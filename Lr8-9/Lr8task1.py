import pandas as pd

file_name = "population_ua.csv"
try:
    df = pd.read_csv(file_name)
    print(f"Файл '{file_name}' успішно завантажено!\n")
except FileNotFoundError:
    print(f"Помилка: файл '{file_name}' не знайдено в директорії.")
    exit()

print("Початкові дані (вміст DataFrame):")
print(df)

print("\nПерші 3 рядки DataFrame (df.head(3)):")
print(df.head(3))

print("\nТипи даних у стовпцях (df.dtypes):")
print(df.dtypes)

print("\nКількість рядків і стовпців (df.shape):")
print(df.shape)

print("\nОписова статистика для числових даних (df.describe()):")
print(df.describe())

df["Value_in_millions"] = df["Value"] / 1_000_000

print("\nDataFrame після додавання нового розрахункового стовпця ('Value_in_millions'):")
print(df.head())

if "Year" in df.columns:
    filtered_df = df[df["Year"] > 2016]
    print("\nРезультат фільтрації (писи з роком > 2016):")
    print(filtered_df)
else:
    filtered_df = df.head(3)

sort_column = "Year" if "Year" in df.columns else df.columns[0]
sorted_df = df.sort_values(by=sort_column, ascending=False)
print(f"\nРезультат сортування за стовпцем '{sort_column}' (спадання):")
print(sorted_df.head())

group_column = "Indicator" if "Indicator" in df.columns else df.columns[0]
grouped_df = df.groupby(group_column)["Value"].agg(['mean', 'max', 'min', 'count']).reset_index()
print("\nРезультат групування та агрегації:")
print(grouped_df)

output_file = "analyzed_population_result.csv"
df.to_csv(output_file, index=False)
print(f"\nРезультати успішно збережено у новий файл '{output_file}'.")