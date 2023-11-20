# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

import requests
from . import const
from . import config
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionRequestLocation(Action):

    def name(self) -> Text:
        return 'action_request_location'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_location = tracker.get_slot('user_location')
        params = {
            'q': user_location,
            'limit': 1,
            'appid': config.OPEN_WEATHER_API_KEY
        }
        response = requests.get(
            const.GEOCODING_API,
            params=params
        )
        actions = []
        if response.status_code == 200:
             if len(response.json()) > 0:
                data = response.json()[0]
                state = f", {data['state']}" if 'state' in data else ''
                mapped_location = f"{data['name']} ({data['country']}{state})"
                actions = [
                    SlotSet('mapped_location', mapped_location),
                    SlotSet('mapped_latitude', data['lat']),
                    SlotSet('mapped_longitude', data['lon'])
                ]
        # TODO: Handle errors and empty responses
        return actions
    

class ActionRequestWeather(Action):

    def name(self) -> Text:
        return 'action_request_weather'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        lat = tracker.get_slot('mapped_latitude')
        lon = tracker.get_slot('mapped_longitude')
        params = {
            'lat': lat,
            'lon': lon,
            'units': const.UNITS,
            'appid': config.OPEN_WEATHER_API_KEY
        }
        response = requests.get(
            const.CURRENT_WEATHER_API,
            params=params
        )
        actions = []
        if response.status_code == 200:
            data = response.json()
            actions = [
                SlotSet('weather', data['weather'][0]['description']),
                SlotSet('temperature', data['main']['temp']),
                SlotSet('temperature_unit', const.TEMPERATURE_UNIT)
            ]
        # TODO: Handle errors and empty responses
        return actions    
