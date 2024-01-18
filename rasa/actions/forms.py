from typing import Any, Text, Dict, List

import requests
import datetime
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
    FORECAST = 'forecast'
    RAIN = 'rain'
    SNOW = 'snow'
    RAIN_FORECAST = 'rain_forecast'
    SNOW_FORECAST = 'snow_forecast'

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

        request_forecast(self, location: Dict[Text, Any]) -> Dict[Text, Any]:
            Retrieves weather forecast information for the mapped location with an API call.

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
            # Check for rain
            mapped_location = location[Slots.MAPPED_LOCATION]
            main_category = data['weather'][0]['main']
            if main_category == 'Rain':
                rain_description = data['weather'][0]['description']
                rain = f"There is {rain_description} in {mapped_location}."
            else:
                rain = f"There is no rain in {mapped_location}."
            # Check for snow
            if main_category == 'Snow':
                snow_description = data['weather'][0]['description']
                snow = f"There is {snow_description} in {mapped_location}."
            else:
                snow = f"There is no snow in {mapped_location}."
            results = {
                Slots.WEATHER: data['weather'][0]['description'],
                Slots.TEMPERATURE: data['main']['temp'],
                Slots.CLOUDINESS: data['clouds']['all'],
                Slots.WIND_SPEED: data['wind']['speed'],
                Slots.HUMIDITY: data['main']['humidity'],
                Slots.RAIN: rain,
                Slots.SNOW: snow,
                Slots.TEMPERATURE_UNIT: const.TEMPERATURE_UNIT,
            }
        else:
            raise RuntimeError(f"""Unfortunately, my call to the weather API failed
                               with the response code {response.status_code}: '{response.json()['message']}'.""")
        return results

    def request_forecast(self, location: Dict[Text, Any]) -> Dict[Text, Any]:
        """
        Retrieves weather forecast information for the mapped location with an API call.

        Args:
            location (Dict[Text, Any]): A dictionary containing the mapped location, latitude, and longitude.

        Returns:
            Dict[Text, Any]: A dictionary containing weather information such as description, temperature, cloudiness, etc.
        """
        params = {
            'lat': location[Slots.MAPPED_LATITUDE],
            'lon': location[Slots.MAPPED_LONGITUDE],
            'cnt': 18,
            'units': const.UNITS,
            'appid': config.OPEN_WEATHER_API_KEY
        }
        response = requests.get(
            const.FORECAST_API,
            params=params
        )
        results = {}
        if response.status_code == 200:
            data = response.json()
            # Get the forecast for tomorrow noon
            current_date = datetime.date.today()
            tomorrow_noon = datetime.datetime.combine(current_date + datetime.timedelta(days=1), datetime.time(12, 0))
            tomorrow_noon_str = tomorrow_noon.strftime("%Y-%m-%d %H:%M:%S")
            tomorrow_noon_weather = [e for e in data['list'] if e['dt_txt'] == tomorrow_noon_str][0]
            if tomorrow_noon_weather:
                # Create the forecast string
                mapped_location = location[Slots.MAPPED_LOCATION]
                weather = tomorrow_noon_weather['weather'][0]['description']
                temperature = tomorrow_noon_weather['main']['temp']
                temperature_unit = const.TEMPERATURE_UNIT
                wind_speed = tomorrow_noon_weather['wind']['speed']
                # Rain forecast
                main_category = tomorrow_noon_weather['weather'][0]['main']
                if main_category == 'Rain':
                    rain_description = tomorrow_noon_weather['weather'][0]['description']
                    rain_forecast = f"Tomorrow noon, there will be {rain_description} in {mapped_location}."
                else:
                    rain_forecast = f"Tomorrow noon, there will be no rain in {mapped_location}."
                # Snow forecast
                if main_category == 'Snow':
                    snow_description = tomorrow_noon_weather['weather'][0]['description']
                    snow_forecast = f"Tomorrow noon, there will be {snow_description} in {mapped_location}."
                else:
                    snow_forecast = f"Tomorrow noon, there will be no snow in {mapped_location}."
                forecast = (
                    f"Tomorrow noon, the weather in {mapped_location} will be {weather} at "
                    f"{temperature:.0f} {temperature_unit} and {wind_speed:.0f} m/s wind speed."
                )
                results = {
                    Slots.FORECAST: forecast,
                    Slots.RAIN_FORECAST: rain_forecast,
                    Slots.SNOW_FORECAST: snow_forecast
                }
            else:
                raise RuntimeError(f"""Unfortunately, I could not find the forecast for tomorrow noon.""")
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
            forecast_results = self.request_forecast(location_results)
            slots = location_results | weather_results | forecast_results
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