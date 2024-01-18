# Rasa Weather Chatbot

This project implements a weather forecast chatbot with [Rasa Open Source](https://rasa.com/docs/rasa/).

Users can request location-based weather information with natural language. The chatbot handles requests about the current weather, temperature, cloudiness, wind speed, humidity, rainfall, snowfall, and the forecast for the next day, including rain and snow information. User requests are answered with live data from [OpenWeather](https://openweathermap.org/api)'s geocoding and weather APIs [(OpenWeather, 2023a; OpenWeather, 2023b; OpenWeather, 2023c)](#sources).

The following diagram illustrates the architecture and main components of the solution.

![Architecture](./images/architecture.png)

## Table of Contents
1. [Requirements](#requirements)
1. [Installation](#installation)
1. [Usage](#usage)
1. [Limitations](#limitations)
1. [Sources](#sources)
1. [License](#license)

## Requirements
This project requires **Python 3.9** or higher. Other dependencies are listed in [requirements.txt](./requirements.txt).

Moreover, an [OpenWeather](https://openweathermap.org/api) API key is required. The key can be obtained for free by creating an account on the website.

## Installation
To install the project, clone the repository and install the dependencies using pip.
```bash
git clone <this-repository>
cd rasa-weather-chatbot
pip install -r requirements.txt
```

Within `/rasa/actions` create a file named `config.py` for your OpenWeather API key.
```bash
cd rasa/actions
touch config.py
```

Add the following line to `config.py` and replace `<your-api-key>` with your OpenWeather API key.
```python
OPEN_WEATHER_API_KEY = "<your-api-key>"
```

## Usage
The chatbot can be trained and used via the [Rasa CLI](https://rasa.com/docs/rasa/command-line-interface).

Therefore, navigate to the `/rasa` directory.
```bash
cd rasa
```

Now, train the chatbot.
```bash
rasa train
```

Afterwards, start the action server to enable the chatbot to retrieve weather data from external APIs.
```bash
rasa run actions
```

Finally, open another terminal window within the `/rasa` directory and start the chatbot.
```bash
rasa shell
```

You can now interact with the chatbot using the shell interface. You can ask the chatbot questions about the following details:
- Current weather
- Temperature
- Cloudiness
- Wind speed
- Humidity
- Rainfall
- Snowfall
- Forecast for the next day at noon
- If there will be rain the next day at noon
- If there will be snow the next day at noon

> **Note**
> The Natural Language Understanding (NLU) component uses a lookup table to identify city names in user messages. The lookup table is defined in [cities.yml](./rasa/data/cities.yml) and was created by parsing the basic database from [simplemaps.com](https://simplemaps.com/data/world-cities) [(SimpleMaps, 2023)](#sources).

## Limitations
The following limitations apply to this project:
- The application is not designed for production use. It is intended to demonstrate the operating principles of a conversational AI.
- A CI/CD pipeline is not set up.
- The chatbot can only be accessed locally via a command line interface.
- For demonstration purposes, the chatbot is connected to public APIs which require a personal API key.
- The chatbot supports only English language.
- The chatbot is limited to questions about the current weather, temperature,
cloudiness, wind speed, humidity, rainfall, snowfall, and the forecast for the next day, including rain and snow information.
- The weather forecast is restricted to the weather at noon of the next day.
- The chatbot uses only metric units.
- The training data of the NLU component is limited. The chatbot can only handle a
tailored set of wordings for specific requests.
- The interaction capabilities of the chatbot are limited. It is not able to deal with
complex requests or conversations.

## Sources
The following sources were used to create this project:
- OpenWeather. (2023a). *Geocoding API*. https://openweathermap.org/api/geocoding-api.
- OpenWeather. (2023b). *Current weather data*. https://openweathermap.org/current.
- OpenWeather. (2023c). *5 day weather forecast*. https://openweathermap.org/forecast5.
- SimpleMaps. (2023). *World Cities Database*. https://simplemaps.com/data/world-cities.

## License
This project is licensed under the terms of the [MIT license](./LICENSE).