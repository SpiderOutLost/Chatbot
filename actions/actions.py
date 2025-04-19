from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime
import re
from textblob import TextBlob
import spacy

nlp = spacy.load("ru_core_news_sm")


class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.now().strftime("%H:%M:%S")
        dispatcher.utter_message(text=f"Сейчас {current_time}")
        return []


class ActionGetDate(Action):
    def name(self) -> Text:
        return "action_get_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_date = datetime.now().strftime("%Y-%m-%d")
        dispatcher.utter_message(text=f"Сегодня {current_date}")
        return []


class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        latest_message = tracker.latest_message.get('text')

        # Извлечение чисел и оператора
        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', latest_message)
        if match:
            num1 = int(match.group(1))
            operator = match.group(2)
            num2 = int(match.group(3))

            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                result = num1 / num2 if num2 != 0 else "Ошибка: деление на ноль!"

            dispatcher.utter_message(text=f"Результат: {result}")
        else:
            dispatcher.utter_message(text="Не могу распознать математическое выражение.")

        return []


class ActionAnalyzeText(Action):
    def name(self) -> Text:
        return "action_analyze_text"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        latest_message = tracker.latest_message.get('text')
        text_entity = next(tracker.get_latest_entity_values("text"), None)

        if not text_entity:
            dispatcher.utter_message(text="Не нашел текст для анализа.")
            return []

        # Определение языка
        if "определи язык" in latest_message:
            lang = self.detect_language(text_entity)
            dispatcher.utter_message(text=f"Язык текста: {lang}")

        # Анализ тональности
        elif "какая тональность" in latest_message:
            sentiment = self.analyze_sentiment(text_entity)
            dispatcher.utter_message(text=f"Тональность текста: {sentiment}")

        # Коррекция текста
        elif "исправь ошибки" in latest_message:
            corrected = self.correct_text(text_entity)
            dispatcher.utter_message(text=f"Исправленный текст: {corrected}")

        # Распознавание сущностей
        elif "кто в тексте" in latest_message:
            entities = self.extract_entities(text_entity)
            formatted = self.format_entities(entities)
            dispatcher.utter_message(text=formatted)

        return []

    def detect_language(self, text: Text) -> Text:
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

    def analyze_sentiment(self, text: Text) -> Text:
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity

        if sentiment > 0.1:
            return "positive"
        elif sentiment < -0.1:
            return "negative"

        # Дополнительная проверка по ключевым словам
        negative_words = ["грустно", "плохо", "ненавижу", "злой"]
        positive_words = ["рад", "счастлив", "хорошо", "отлично"]
        text_lower = text.lower()

        if any(word in text_lower for word in negative_words):
            return "negative"
        elif any(word in text_lower for word in positive_words):
            return "positive"
        return "neutral"

    def correct_text(self, text: Text) -> Text:
        blob = TextBlob(text)
        return str(blob.correct())

    def extract_entities(self, text: Text) -> Dict:
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

    def format_entities(self, entities: Dict) -> Text:
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


class ActionEcho(Action):
    def name(self) -> Text:
        return "action_echo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        text_entity = next(tracker.get_latest_entity_values("text"), None)
        if text_entity:
            dispatcher.utter_message(text=text_entity)
        else:
            dispatcher.utter_message(text="Не понял, что повторить.")

        return []