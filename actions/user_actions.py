
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from .use_db import save_user, get_last_user
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionSaveUserInfo(Action):
    def name(self) -> Text:
        return "action_save_user_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Получаем данные из слотов
        user_id = tracker.sender_id
        name = tracker.get_slot("name") or "Неизвестный"
        city = tracker.get_slot("city") or "Не указан"
        hobby = tracker.get_slot("hobby") or "Не указано"


        logger.info(f"User ID: {user_id}")
        logger.info(f"Extracted entities: name={name}, city={city}, hobby={hobby}")
        logger.info(f"Latest message: {tracker.latest_message.get('text')}")
        logger.info(f"Entities: {list(tracker.get_latest_entity_values('name'))}, "
                    f"{list(tracker.get_latest_entity_values('city'))}, "
                    f"{list(tracker.get_latest_entity_values('hobby'))}")

        # Проверяем, все ли данные предоставлены
        missing_data = []
        if name == "Неизвестный":
            missing_data.append("имя")
        if city == "Не указан":
            missing_data.append("город")
        if hobby == "Не указано":
            missing_data.append("хобби")

        if missing_data:
            dispatcher.utter_message(text=f"Пожалуйста, укажи {' и '.join(missing_data)}.")
            return []

        # Сохраняем данные в SQLite
        save_user(user_id, name, city, hobby)

        # Подтверждаем сохранение
        dispatcher.utter_message(text=f"Спасибо, {name}! Я сохранил твои данные: город - {city}, хобби - {hobby}.")

        return [
            SlotSet("name", name),
            SlotSet("city", city),
            SlotSet("hobby", hobby)
        ]


class ActionGreetLastUser(Action):
    def name(self) -> Text:
        return "action_greet_last_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Получаем данные последнего пользователя
        last_user = get_last_user()

        if last_user:
            last_user_name = last_user["name"]
            if last_user["user_id"] == tracker.sender_id:
                # Если текущий пользователь совпадает с последним
                dispatcher.utter_message(response="utter_greet", name=last_user_name)
                return [
                    SlotSet("name", last_user_name),
                    SlotSet("city", last_user["city"]),
                    SlotSet("hobby", last_user["hobby"])
                ]
            else:
                # Если текущий пользователь новый, упоминаем имя последнего
                dispatcher.utter_message(response="utter_greet", name=last_user_name)
                return []
        else:
            # Если в базе нет пользователей
            dispatcher.utter_message(response="utter_greet")
            return []