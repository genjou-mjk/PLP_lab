import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 5)

file_path = 'comptagevelo2011.csv'

try:
    df = pd.read_csv(
        file_path,
        sep=',', 
        parse_dates=['Date'], 
        dayfirst=True,
        index_col='Date'
    )
    print("Дані велодоріжок успішно завантажено.\n")
except Exception as e:
    print(f"Помилка завантаження файлу: {e}")
    exit()

df_2011 = df[df.index.year == 2011]

print("--- Перші 5 рядків DataFrame (head) ---")
print(df_2011.head())

print("\n--- Інформація про DataFrame (info) ---")
print(df_2011.info())

print("\n--- Описова статистика (describe) ---")
print(df_2011.describe())

total_cyclists_2011 = df_2011.sum(numeric_only=True)
print("\n--- Загальна кількість велосипедистів за 2011 рік по доріжках ---")
print(total_cyclists_2011)
print(f"\nЗагалом за рік на всіх доріжках зафіксовано: {total_cyclists_2011.sum():,.0f} поїздок.")

selected_tracks = ['Maisonneuve_1', 'Brébeuf', 'PierDup']
existing_tracks = [t for t in selected_tracks if t in df_2011.columns]

if len(existing_tracks) < 3:
    existing_tracks = df_2011.select_dtypes(include=['number']).columns[:3].tolist()

print(f"\n--- Найбільш популярні місяці для обраних доріжок: {existing_tracks} ---")

try:
    monthly_data = df_2011[existing_tracks].resample('ME').sum()
except ValueError:
    monthly_data = df_2011[existing_tracks].resample('M').sum()

for track in existing_tracks:
    max_month_idx = monthly_data[track].idxmax()
    max_month_name = max_month_idx.strftime('%B %Y')
    max_val = monthly_data[track].max()
    print(f"Доріжка '{track}': найпопулярніший місяць — {max_month_name} ({max_val:,.0f} велосипедистів)")

target_track = existing_tracks[0] 
monthly_trend = monthly_data[target_track]

print(f"\n--- Динаміка використання велодоріжки {target_track} за місяцями 2011 року ---")
print(monthly_trend)

plt.figure()
monthly_trend.plot(marker='o', color='b', linewidth=2)
plt.title(f"Динаміка використання велодоріжки {target_track} у 2011 році", fontsize=14)
plt.xlabel("Місяць", fontsize=12)
plt.ylabel("Кількість велосипедистів", fontsize=12)
plt.grid(True)
plt.tight_layout()

plt.savefig("bike_trend_2011.png")
plt.show()

print("\nГрафік успішно побудовано та збережено у файл 'bike_trend_2011.png'.")