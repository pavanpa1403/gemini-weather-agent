from langchain_core.tools import tool


@tool
def get_places(city: str) -> dict:
    """
    Get popular sightseeing places for a city.

    Args:
        city: Name of the city.

    Returns:
        Dictionary containing popular attractions.
    """

    places = {
        "Hyderabad": [
            "Charminar",
            "Golconda Fort",
            "Chowmahalla Palace",
            "Salar Jung Museum",
            "Hussain Sagar Lake"
        ],

        "Chennai": [
            "Marina Beach",
            "Kapaleeshwarar Temple",
            "Fort St. George",
            "San Thome Basilica",
            "Elliot's Beach"
        ],

        "Mumbai": [
            "Gateway of India",
            "Marine Drive",
            "Colaba Causeway",
            "Elephanta Caves",
            "Chhatrapati Shivaji Maharaj Terminus"
        ]
    }

    city_key = city.strip().title()

    if city_key not in places:
        return {
            "city": city,
            "error": "No sightseeing information available for this city."
        }

    return {
        "city": city_key,
        "places": places[city_key]
    }   