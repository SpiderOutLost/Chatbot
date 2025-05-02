from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionEcho(Action):
    def name(self) -> Text:
        return "action_echo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Получаем полный текст сообщения пользователя
        user_message = tracker.latest_message.get('text', '').strip()

        # Проверяем наличие команды "эхо" и извлекаем текст после нее
        if user_message.lower().startswith('эхо'):
            text_to_echo = user_message[3:].strip()  # Удаляем "эхо" и лишние пробелы
            if text_to_echo:
                dispatcher.utter_message(text=text_to_echo)
                return []

        # Альтернативный вариант - ищем текст в любом месте сообщения
        if 'эхо' in user_message.lower():
            text_to_echo = user_message.lower().split('эхо', 1)[1].strip()
            if text_to_echo:
                dispatcher.utter_message(text=text_to_echo)
                return []

        dispatcher.utter_message(text="Пожалуйста, укажите текст после слова 'эхо'")
        return []