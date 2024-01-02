from typing import Any, Text, Dict, List

import requests
from . import const
from . import config
from abc import ABC, abstractmethod
from enum import Enum
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


from enum import Enum
from typing import Dict, Text, Any


class Slots(str, Enum):
    """
    Enum class representing location dependent slots of the chatbot.
    """

    USER_LOCATION = 'user_location'
    MAPPED_LOCATION = 'mapped_location'
    MAPPED_LATITUDE = 'mapped_latitude'
    MAPPED_LONGITUDE = 'mapped_longitude'
    WEATHER = 'weather'
    TEMPERATURE = 'temperature'
    CLOUDINESS = 'cloudiness'
    WIND_SPEED = 'wind_speed'
    HUMIDITY = 'humidity'
    TEMPERATURE_UNIT = 'temperature_unit'

    def reset_slots() -> Dict[Text, Any]:
        """
        Reset all the slots to None.

        Returns:
            A dictionary with all the slots set to None.
        """
        return {slot: None for slot in Slots}


class LocationDependentForm(FormValidationAction, ABC):
    """
    A base class for location-dependent forms in the Rasa weather chatbot.

    This class provides methods for mapping user input location to a unique geo location
    and retrieving weather information for the mapped location.

    Attributes:
        None

    Methods:
        name(self) -> Text:
            Returns the name of the form for identification of Rasa Core.

        request_location(self, tracker: Tracker) -> Dict[Text, Any]:
            Maps the user's input location to a unique geo location with an API call.

        request_weather(self, location: Dict[Text, Any]) -> Dict[Text, Any]:
            Retrieves weather information for the mapped location with an API call.

        run_queries(self, dispatcher: CollectingDispatcher, tracker: Tracker) -> List[Dict[Text, Any]]:
            Runs the location and weather API queries and returns joined results.

        validate_user_location(self, slot_value: Any, dispatcher: CollectingDispatcher,
                               tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
            Validates the user location slot and triggers the queries if necessary. Overrides Rasa's default validation method.

        validate_mapped_location(self, slot_value: Any, dispatcher: CollectingDispatcher,
                                 tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
            Validates the mapped location slot and resets all slots if mapping fails. Overrides Rasa's default validation method.
    """

    @abstractmethod
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        pass

    def request_location(self, tracker: Tracker) -> Dict[Text, Any]:
        """
        Maps the user's input location to a unique geo location with an API call.

        Args:
            tracker (Tracker): The tracker object containing the conversation history.

        Returns:
            Dict[Text, Any]: A dictionary containing the mapped location, latitude, and longitude.
        """
        user_location = tracker.get_slot(Slots.USER_LOCATION)
        params = {
            'q': user_location,
            'limit': 1,
            'appid': config.OPEN_WEATHER_API_KEY
        }
        response = requests.get(
            const.GEOCODING_API,
            params=params
        )
        results = {}
        if response.status_code == 200:
            if len(response.json()) > 0:
                data = response.json()[0]
                state = f", {data['state']}" if 'state' in data else ''
                mapped_location = f"{data['name']} ({data['country']}{state})"
                results = {
                    Slots.MAPPED_LOCATION: mapped_location,
                    Slots.MAPPED_LATITUDE: data['lat'],
                    Slots.MAPPED_LONGITUDE: data['lon']
                }
            else:
                raise RuntimeError(f"I could not map {user_location} to an existing city.")
        else:
            raise RuntimeError(f"""Unfortunately, my call to the geocoding API failed with the
                               response code {response.status_code}: '{response.json()['message']}'.""")
        return results

    def request_weather(self, location: Dict[Text, Any]) -> Dict[Text, Any]:
        """
        Retrieves weather information for the mapped location with an API call.

        Args:
            location (Dict[Text, Any]): A dictionary containing the mapped location, latitude, and longitude.

        Returns:
            Dict[Text, Any]: A dictionary containing weather information such as description, temperature, cloudiness, etc.
        """
        params = {
            'lat': location[Slots.MAPPED_LATITUDE],
            'lon': location[Slots.MAPPED_LONGITUDE],
            'units': const.UNITS,
            'appid': config.OPEN_WEATHER_API_KEY
        }
        response = requests.get(
            const.CURRENT_WEATHER_API,
            params=params
        )
        results = {}
        if response.status_code == 200:
            data = response.json()
            results = {
                Slots.WEATHER: data['weather'][0]['description'],
                Slots.TEMPERATURE: data['main']['temp'],
                Slots.CLOUDINESS: data['clouds']['all'],
                Slots.WIND_SPEED: data['wind']['speed'],
                Slots.HUMIDITY: data['main']['humidity'],
                Slots.TEMPERATURE_UNIT: const.TEMPERATURE_UNIT,
            }
        else:
            raise RuntimeError(f"""Unfortunately, my call to the weather API failed
                               with the response code {response.status_code}: '{response.json()['message']}'.""")
        return results

    def run_queries(self, 
                    dispatcher: CollectingDispatcher,
                    tracker: Tracker
                    ) -> List[Dict[Text, Any]]:
        """
        Runs the location and weather API queries and returns joined results.

        Args:
            dispatcher (CollectingDispatcher): The dispatcher object for sending messages to the user.
            tracker (Tracker): The tracker object containing the conversation history.

        Returns:
            List[Dict[Text, Any]]: A list of dictionaries containing the location and weather results.
        """
        try:
            user_location = tracker.get_slot(Slots.USER_LOCATION)
            location_results = self.request_location(tracker)
            weather_results = self.request_weather(location_results)
            slots = location_results | weather_results
            dispatcher.utter_message(
                text=f"Your requested location {user_location} was mapped to {slots[Slots.MAPPED_LOCATION]}."
            )
        except RuntimeError as e:
            slots = Slots.reset_slots()
            dispatcher.utter_message(text=str(e))
        return slots

    def validate_user_location(self,
                               slot_value: Any,
                               dispatcher: CollectingDispatcher,
                               tracker: Tracker,
                               domain: DomainDict
                               ) -> Dict[Text, Any]:
        """
        Validates the user location slot and triggers the queries if necessary. Overrides Rasa's default validation method.

        Args:
            slot_value (Any): The value of the user location slot.
            dispatcher (CollectingDispatcher): The dispatcher object for sending messages to the user.
            tracker (Tracker): The tracker object containing the conversation history.
            domain (DomainDict): The domain dictionary containing the bot's domain.

        Returns:
            Dict[Text, Any]: A dictionary containing the updated slots.
        """
        prev_location = tracker.get_slot(Slots.MAPPED_LOCATION)
        if slot_value is None:
            dispatcher.utter_message("No location identified. Please retry.")
            slots = Slots.reset_slots()
        elif prev_location is None or slot_value.lower() not in prev_location.lower():
            slots = self.run_queries(dispatcher, tracker)
        else:
            slots = {}
        return slots
    
    def validate_mapped_location(self,
                                 slot_value: Any,
                                 dispatcher: CollectingDispatcher,
                                 tracker: Tracker,
                                 domain: DomainDict
                                 ) -> Dict[Text, Any]:
        """
        Validates the mapped location slot and resets all slots if mapping fails. Overrides Rasa's default validation method.

        Args:
            slot_value (Any): The value of the mapped location slot.
            dispatcher (CollectingDispatcher): The dispatcher object for sending messages to the user.
            tracker (Tracker): The tracker object containing the conversation history.
            domain (DomainDict): The domain dictionary containing the bot's domain.

        Returns:
            Dict[Text, Any]: A dictionary containing the updated slots.
        """
        if slot_value is None:
            dispatcher.utter_message("Please enter a new location.")
            slots = Slots.reset_slots()
        else:
            slots = {}
        return slots