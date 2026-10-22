import nltk
import string
from nltk.corpus import gutenberg, stopwords
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer
import matplotlib.pyplot as plt
import os

print("Перевірка та завантаження ресурсів NLTK...")
for resource in ['gutenberg', 'punkt', 'stopwords', 'wordnet']:
    try:
        nltk.data.find(f'corpora/{resource}')
    except LookupError:
        print(f"Завантаження ресурсу: {resource}...")
        nltk.download(resource)

file_id = 'chesterton-ball.txt'
try:
    raw_words = gutenberg.words(file_id)
    text_words = list(raw_words)
    print(f"Текст '{file_id}' успішно завантажено з NLTK! Кількість слів: {len(text_words):,}")
    
    local_filename = "chesterton_ball.txt"
    with open(local_filename, "w", encoding="utf-8") as f:
        f.write(" ".join(text_words))
    print(f"Текст також успішно збережено у локальний файл '{local_filename}' у вашу паку!\n")
    
except Exception as e:
    print(f"Помилка завантаження тексту: {e}")
    print("Спробуйте виконати у терміналі: python -m nltk.downloader gutenberg punkt stopwords wordnet")
    exit()

plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)

total_words = len(text_words)
unique_words = len(set(text_words))

print("ПУНКТ 1: АНАЛІЗ КІЛЬКОСТІ СЛІВ")
print(f"Загальна кількість слів у тексті: {total_words:,}")
print(f"Кількість унікальних слів у тексті: {unique_words:,}")
print(f"Порівняння: Унікальні слова становлять приблизно {(unique_words / total_words) * 100:.2f}% від загальної кількості.\n")

fdist_original = FreqDist(text_words)
top_ten_original = fdist_original.most_common(10)

print("ПУНКТ 2: 10 НАЙБІЛЬШ УЖИВАНИХ СЛІВ (ПОЧАТКОВИЙ ТЕКСТ)")
for word, freq in top_ten_original:
    print(f"  {word}: {freq}")

words_orig, freqs_orig = zip(*top_ten_original)
plt.figure()
plt.bar(words_orig, freqs_orig, color='skyblue', edgecolor='black')
plt.title("10 найбільш уживаних слів (початковий текст)", fontsize=14)
plt.xlabel("Слова", fontsize=12)
plt.ylabel("Частота", fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("top_words_original.png")
plt.show()

stop_words = set(stopwords.words("english"))
punctuation_table = str.maketrans('', '', string.punctuation)

cleaned_words = []
for word in text_words:
    stripped_word = word.translate(punctuation_table).lower()
    if stripped_word.isalpha() and stripped_word not in stop_words:
        cleaned_words.append(stripped_word)

fdist_cleaned = FreqDist(cleaned_words)
top_ten_cleaned = fdist_cleaned.most_common(10)

print("ПУНКТ 3: 10 НАЙБІЛЬШ УЖИВАНИХ СЛІВ (БЕЗ СТОП-СЛІВ ТА ПУНКТУАЦІЇ)")
for word, freq in top_ten_cleaned:
    print(f"  {word}: {freq}")

words_clean, freqs_clean = zip(*top_ten_cleaned)
plt.figure()
plt.bar(words_clean, freqs_clean, color='lightgreen', edgecolor='black')
plt.title("10 найбільш уживаних слів (без стоп-слів та пунктуації)", fontsize=14)
plt.xlabel("Слова", fontsize=12)
plt.ylabel("Частота", fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("top_words_cleaned.png")
plt.show()

lemmatizer = WordNetLemmatizer()
lemmatized_words = [lemmatizer.lemmatize(word) for word in cleaned_words]

fdist_lemmatized = FreqDist(lemmatized_words)
top_ten_lemmatized = fdist_lemmatized.most_common(10)

print("ПУНКТ 4: 10 НАЙБІЛЬШ УЖИВАНИХ СЛІВ ПІСЛЯ ЛЕМАТИЗАЦІЇ")
for word, freq in top_ten_lemmatized:
    print(f"  {word}: {freq}")