# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Text
from .forms import LocationDependentForm


class ValidateWeatherForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the weather form.

    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_weather_form"


class ValidateTemperatureForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the temperature form.
    
    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_temperature_form"
    

class ValidateCloudinessForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the cloudiness form.
    
    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_cloudiness_form"
    

class ValidateWindSpeedForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the wind speed form.

    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_wind_speed_form"
    

class ValidateHumidityForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the humidity form.

    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_humidity_form"


class ValidateForecastForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the forecast form.

    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_forecast_form"


class ValidateRainForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the rain form.

    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_rain_form"
    

class ValidateSnowForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the snow form.
    
    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_snow_form"
    

class ValidateRainForecastForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the rain forecast form.
    
    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_rain_forecast_form"


class ValidateSnowForecastForm(LocationDependentForm):
    """
    Child class of LocationDependentForm for validating the snow forecast form.
    
    The methods for validating location data are inherited from the parent class.
    """
    def name(self) -> Text:
        """Returns the name of the form for identification of Rasa Core."""
        return "validate_snow_forecast_form"
