import re
import random
import datetime
from textblob import TextBlob
import spacy
nlp = spacy.load("ru_core_news_sm")
responses = {
    r".*привет.*": "Привет! Как я могу помочь?",
    r".*как тебя зовут\?.*": "Я бот-помощник!",
    r".*что ты умеешь\?.*": "Я умею отвечать на простые вопросы, считать, анализировать текст и многое другое. Напишите /help для списка команд.",
    r".*сколько времени.*|.*текущее время.*|.*сейчас времени.*": lambda: f"Сейчас {datetime.datetime.now().strftime('%H:%M:%S')}.",
    r".*какая сегодня дата.*|.*текущая дата.*": lambda: f"Сегодня {datetime.datetime.now().strftime('%Y-%m-%d')}.",
    r".*какая сейчас погода.*": "Пока функция не работает.",
    r".*сколько будет (\d+) плюс (\d+)\??.*": lambda x, y: f"{x} + {y} = {int(x) + int(y)}",
    r".*сколько будет (\d+) минус (\d+)\??.*": lambda x, y: f"{x} - {y} = {int(x) - int(y)}",
    r".*сколько будет (\d+) умножить на (\d+)\??.*": lambda x, y: f"{x} * {y} = {int(x) * int(y)}",
    r".*сколько будет (\d+) разделить на (\d+)\??.*": lambda x,
                                                             y: f"{x} / {y} = {int(x) / int(y) if int(y) != 0 else 'Ошибка: деление на ноль!'}",
    r".*эхо (.*)":lambda x: x,  # Режим эхо
    r".*/help": "Доступные команды:\n"
                "- Приветствие (привет, здравствуй)\n"
                "- Вопросы (как тебя зовут, что ты умеешь)\n"
                "- Время и дата (сколько времени, какая сегодня дата)\n"
                "- Математика (сколько будет X + Y, посчитай X * Y)\n"
                "- Анализ текста (определи язык, какая тональность)\n"
                "- Коррекция текста (исправь ошибки в 'текст')\n"
                "- Распознавание сущностей (кто в тексте 'текст')\n"
                "- Эхо-режим (эхо ваш_текст)\n"
                "- Для выхода: выход"
}


def chatbot_response(text):
    text = text.lower().strip()

    # Обработка специальных команд анализа текста
    if text.startswith("определи язык"):
        lang = detect_language(text[13:])
        return f"Язык текста: {lang}"
    elif text.startswith("какая тональность"):
        sentiment = analyze_sentiment(text[18:])
        return f"Тональность текста: {sentiment}"
    elif text.startswith("исправь ошибки в"):
        corrected = correct_text(text[16:])
        return f"Исправленный текст: {corrected}"
    elif text.startswith("кто в тексте"):
        entities = extract_entities(text[13:])
        return format_entities(entities)

    # Проверка настроения пользователя
    sentiment = analyze_sentiment(text)
    if sentiment == "negative":
        return "Кажется, вы расстроены. Хотите об этом поговорить?"
    elif sentiment == "positive":
        return "Рад, что у вас хорошее настроение! Чем могу помочь?"

    # Извлечение имен для персонализированного ответа
    entities = extract_entities(text)
    if entities["PER"]:
        return f"Привет, {', '.join(entities['PER'])}! Как я могу вам помочь?"

    # Поиск совпадений с базой ответов
    for pattern, response in responses.items():
        match = re.match(pattern, text)
        if match:
            if callable(response):
                return response(*match.groups())
            else:
                return response

    return random.choice(["Я не понял вопрос.", "Попробуйте перефразировать.", "Напишите /help для списка команд."])


def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity

        if sentiment > 0.1:
            return "positive"
        elif sentiment < -0.1:
            return "negative"
    except:
        pass

    # Дополнительная проверка по ключевым словам (для русского)
    negative_words = ["грустно", "плохо", "ненавижу", "злой", "разозлися", "ужасно", "отвратительно"]
    positive_words = ["рад", "счастлив", "хорошо", "отлично", "прекрасно", "замечательно", "восхитительно"]
    text_lower = text.lower()

    if any(word in text_lower for word in negative_words):
        return "negative"
    elif any(word in text_lower for word in positive_words):
        return "positive"
    return "neutral"


def extract_entities(text):
    doc = nlp(text)
    entities = {
        "PER": [],  # Персоны
        "LOC": [],  # Локации
        "DATE": [],  # Даты
        "ORG": []  # Организации
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    return entities


def format_entities(entities):
    response = []
    if entities["PER"]:
        response.append(f"Люди: {', '.join(entities['PER'])}")
    if entities["LOC"]:
        response.append(f"Места: {', '.join(entities['LOC'])}")
    if entities["DATE"]:
        response.append(f"Даты: {', '.join(entities['DATE'])}")
    if entities["ORG"]:
        response.append(f"Организации: {', '.join(entities['ORG'])}")
    return "\n".join(response) if response else "Не удалось распознать сущности в тексте."


def detect_language(text):
    blob = TextBlob(text)
    try:
        lang = blob.detect_language()
        lang_names = {
            'en': 'английский',
            'ru': 'русский',
            'fr': 'французский',
            'de': 'немецкий',
            'es': 'испанский'
        }
        return lang_names.get(lang, lang)
    except:
        return "неизвестный"


def correct_text(text):
    blob = TextBlob(text)
    return str(blob.correct())


# Основной цикл работы бота
print("Бот: Привет! Я ваш помощник. Напишите 'выход' для завершения диалога.")
while True:
    user_input = input("Вы: ")
    if user_input.lower() == "выход":
        print("Бот: До свидания!")
        break
    response = chatbot_response(user_input)
    print("Бот:", response)