def calculate_weather_score(weather):
    """
    Calculate a simple weather score from 1 to 10.
    """

    score = 10

    temperature = float(weather.get("temperature", 25))
    humidity = float(weather.get("humidity", 50))
    wind_speed = float(weather.get("wind_speed", 10))

    condition = weather.get(
        "condition",
        ""
    ).lower()

    # Temperature
    if temperature > 35:
        score -= 3
    elif temperature > 32:
        score -= 2
    elif temperature < 15:
        score -= 2

    # Humidity
    if humidity > 80:
        score -= 2
    elif humidity > 70:
        score -= 1

    # Wind
    if wind_speed > 30:
        score -= 2
    elif wind_speed > 20:
        score -= 1

    # Weather condition
    if "rain" in condition:
        score -= 2
    elif "storm" in condition:
        score -= 3

    return max(1, min(score, 10))


def calculate_places_score(places):
    """
    Calculate a sightseeing score from 1 to 10.
    """

    number_of_places = len(
        places.get("places", [])
    )

    if number_of_places >= 5:
        return 10

    if number_of_places == 4:
        return 8

    if number_of_places == 3:
        return 7

    if number_of_places == 2:
        return 5

    if number_of_places == 1:
        return 3

    return 1


def calculate_total_score(
    weather_score,
    places_score
):
    """
    Combine weather and sightseeing scores.
    """

    return round(
        (weather_score * 0.6)
        + (places_score * 0.4),
        2
    )