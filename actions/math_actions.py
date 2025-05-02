import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        latest_message = tracker.latest_message.get('text')
        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', latest_message)

        if match:
            num1, operator, num2 = match.groups()
            result = self._calculate(int(num1), operator, int(num2))
            dispatcher.utter_message(text=f"Результат: {result}")
        else:
            dispatcher.utter_message(text="Не могу распознать математическое выражение.")
        return []

    def _calculate(self, num1: int, operator: str, num2: int) -> float:
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y if y != 0 else float('inf')
        }
        return operations[operator](num1, num2)