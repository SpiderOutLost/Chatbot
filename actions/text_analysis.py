from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import spacy
import re

nlp = spacy.load("ru_core_news_sm")


class ActionAnalyzeText(Action):
    def name(self) -> Text:
        return "action_analyze_text"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Получаем текст из сущности
        text_entity = next(tracker.get_latest_entity_values("text"), None)

        # Если сущности нет, пытаемся извлечь из сообщения
        if not text_entity:
            user_message = tracker.latest_message.get('text', '')
            text_entity = self._extract_text_from_message(user_message)

        if not text_entity:
            dispatcher.utter_message(response="utter_analyze_text_prompt")
            return []

        # Анализ сущностей
        doc = nlp(text_entity)
        entities = {
            "PER": [ent.text for ent in doc.ents if ent.label_ == "PER"],
            "LOC": [ent.text for ent in doc.ents if ent.label_ == "LOC"],
            "ORG": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
            "FOOD": [ent.text for ent in doc.ents if ent.label_ == "FOOD"]
        }

        # Формируем ответ
        response_parts = []
        if entities["PER"]:
            response_parts.append(f"👤 Люди: {', '.join(entities['PER'])}")
        if entities["LOC"]:
            response_parts.append(f"📍 Места: {', '.join(entities['LOC'])}")
        if entities["ORG"]:
            response_parts.append(f"🏢 Организации: {', '.join(entities['ORG'])}")
        if entities["FOOD"]:
            response_parts.append(f"🍕 Еда: {', '.join(entities['FOOD'])}")

        if response_parts:
            dispatcher.utter_message(text="\n".join(response_parts))
        else:
            dispatcher.utter_message(text="Не найдено распознаваемых сущностей")

        return []

    def _extract_text_from_message(self, message: Text) -> Text:
        """Извлекает текст из сообщения (если нет сущности)"""
        # Ищем текст в квадратных скобках
        bracket_match = re.search(r'\[(.*?)\]', message)
        if bracket_match:
            return bracket_match.group(1).strip()

        # Ищем после ключевых фраз
        triggers = ["кто в тексте", "сущности в тексте", "найди в тексте"]
        for trigger in triggers:
            if trigger in message.lower():
                return message[message.lower().find(trigger) + len(trigger):].strip()

        return None