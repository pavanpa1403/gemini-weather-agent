from typing import TypedDict, List, Dict, Any


class TravelState(TypedDict, total=False):

    # Original user request
    user_request: str

    # Messages exchanged between user, Gemini and tools
    messages: List[Any]

    # Extracted weather information
    weather_data: List[Dict[str, Any]]

    # Extracted sightseeing information
    places_data: List[Dict[str, Any]]

    # Calculated scores
    scores: Dict[str, Dict[str, float]]

    # Final city ranking
    ranking: List[str]

    # Final generated answer
    final_response: str