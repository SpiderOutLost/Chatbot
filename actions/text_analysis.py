from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import spacy

# Загрузка модели для русского языка
nlp = spacy.load("ru_core_news_sm")


class ActionAnalyzeText(Action):
    def name(self) -> Text:
        return "action_analyze_text"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Получаем текст из последнего сообщения пользователя
        user_message = tracker.latest_message.get('text', '')

        # Ищем триггерные фразы
        if any(trigger in user_message.lower() for trigger in
               ["кто в тексте", "найди в тексте", "упоминается в тексте"]):
            # Извлекаем текст для анализа (после триггерной фразы)
            text_to_analyze = self._extract_text_to_analyze(user_message)

            if not text_to_analyze:
                dispatcher.utter_message(text="Не нашел текст для анализа. Пример: 'кто в тексте Илья съел пиццу'")
                return []

            # Анализ сущностей
            entities = self._extract_entities(text_to_analyze)
            response = self._format_entities_response(entities)

            dispatcher.utter_message(text=response)

        return []

    def _extract_text_to_analyze(self, message: Text) -> Text:
        """Извлекает текст для анализа после триггерной фразы"""
        triggers = ["кто в тексте", "найди в тексте", "упоминается в тексте"]
        for trigger in triggers:
            if trigger in message.lower():
                return message[message.lower().find(trigger) + len(trigger):].strip()
        return message.strip()

    def _extract_entities(self, text: Text) -> Dict[Text, List[Text]]:
        """Извлекает сущности из текста"""
        doc = nlp(text)
        return {
            "PER": [ent.text for ent in doc.ents if ent.label_ == "PER"],
            "ORG": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
            "LOC": [ent.text for ent in doc.ents if ent.label_ == "LOC"],
            "FOOD": [ent.text for ent in doc.ents if ent.label_ == "FOOD"]
        }

    def _format_entities_response(self, entities: Dict[Text, List[Text]]) -> Text:
        """Форматирует ответ с найденными сущностями"""
        parts = []
        if entities["PER"]:
            parts.append(f" Люди: {', '.join(entities['PER'])}")
        if entities["ORG"]:
            parts.append(f" Организации: {', '.join(entities['ORG'])}")
        if entities["LOC"]:
            parts.append(f" Места: {', '.join(entities['LOC'])}")
        if entities["FOOD"]:
            parts.append(f" Еда: {', '.join(entities['FOOD'])}")

        return "\n".join(parts) if parts else "Не удалось распознать сущности в тексте"