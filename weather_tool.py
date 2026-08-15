import requests


def get_weather(city):
    """
    Get current weather information for a city.

    Args:
        city (str): Name of the city.

    Returns:
        dict: Weather information.
    """

    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()

        current = data["current_condition"][0]

        weather = {
            "city": city,
            "temperature": current["temp_C"],
            "humidity": current["humidity"],
            "wind_speed": current["windspeedKmph"],
            "condition": current["weatherDesc"][0]["value"]
        }

        return weather

    except requests.exceptions.RequestException as e:
        return {
            "city": city,
            "error": f"Weather API request failed: {str(e)}"
        }

    except (KeyError, IndexError, ValueError) as e:
        return {
            "city": city,
            "error": f"Invalid weather data received: {str(e)}"
        }