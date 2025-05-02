import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = self._extract_city(tracker)
        if not city:
            dispatcher.utter_message(text="Пожалуйста, укажите город, например: 'погода в Москве'")
            return []

        try:
            temp = self._get_weather_data(city)
            dispatcher.utter_message(text=f"Сейчас в {city} {temp}°C")
        except Exception as e:
            error_msg = self._handle_weather_error(e, city)
            dispatcher.utter_message(text=error_msg)

        return []

    def _extract_city(self, tracker) -> Text:
        """Извлекаем город из entities или slots"""
        city = next(tracker.get_latest_entity_values("city"), None)
        return city or tracker.get_slot("city")

    def _get_weather_data(self, city: Text) -> float:
        """Основной метод получения данных о погоде"""
        api_key = "ваш_api_ключ"  # Замените на реальный ключ!
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") != 200:
            raise ValueError(data.get("message", "Ошибка API"))

        return round(data["main"]["temp"])

    def _handle_weather_error(self, error: Exception, city: Text) -> Text:
        """Обработка различных ошибок"""
        error_messages = {
            "city not found": f"Город '{city}' не найден",
            "timed out": "Сервер погоды не отвечает",
            "401": "Ошибка авторизации API",
            "404": "Сервис погоды недоступен"
        }

        if isinstance(error, requests.exceptions.RequestException):
            return "Ошибка соединения с сервером погоды"

        err_msg = str(error).lower()
        for key, msg in error_messages.items():
            if key in err_msg:
                return msg

        return f"Не удалось получить погоду для {city}"