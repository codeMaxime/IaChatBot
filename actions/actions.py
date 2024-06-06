import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionMeteo(Action):

    def name(self) -> Text:
        return "action_meteo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        lieu = tracker.get_slot('lieu')
        if lieu:
            # Remplacez 'YOUR_API_KEY' par votre clé API de météo
            response = requests.get(f"http://api.weatherapi.com/v1/current.json?key=6fdbc8c03d7041ffa15150036240606&q={lieu}")
            if response.status_code == 200:
                weather_data = response.json()
                temperature = weather_data['current']['temp_c']
                condition = weather_data['current']['condition']['text']
                dispatcher.utter
