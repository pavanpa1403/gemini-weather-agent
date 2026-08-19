import json

from scoring import (
    calculate_weather_score,
    calculate_places_score,
    calculate_total_score
)


# ============================================================
# 1. Collect tool results
# ============================================================

def collect_data_node(state):

    print("\n[COLLECT] Collecting tool results...")

    weather_data = []
    places_data = []

    messages = state.get(
        "messages",
        []
    )

    for message in messages:

        # --------------------------------------------
        # Weather tool result
        # --------------------------------------------

        if getattr(message, "name", None) == "get_weather":

            content = message.content

            if isinstance(content, str):

                try:
                    content = json.loads(content)

                except json.JSONDecodeError:

                    print(
                        "[COLLECT] Could not parse weather result:"
                    )

                    print(content)

                    continue

            if isinstance(content, dict):

                weather_data.append(content)


        # --------------------------------------------
        # Places tool result
        # --------------------------------------------

        elif getattr(message, "name", None) == "get_places":

            content = message.content

            if isinstance(content, str):

                try:
                    content = json.loads(content)

                except json.JSONDecodeError:

                    print(
                        "[COLLECT] Could not parse places result:"
                    )

                    print(content)

                    continue

            if isinstance(content, dict):

                places_data.append(content)


    print(
        f"[COLLECT] Weather results collected: "
        f"{len(weather_data)}"
    )

    print(
        f"[COLLECT] Places results collected: "
        f"{len(places_data)}"
    )

    return {
        "weather_data": weather_data,
        "places_data": places_data
    }


# ============================================================
# 2. Calculate scores
# ============================================================

def scoring_node(state):

    print("\n[SCORING] Calculating city scores...")

    weather_data = state.get(
        "weather_data",
        []
    )

    places_data = state.get(
        "places_data",
        []
    )

    places_by_city = {
        item["city"]: item
        for item in places_data
        if "city" in item
    }

    scores = {}

    for weather in weather_data:

        city = weather.get("city")

        if not city:
            continue

        # --------------------------------------------
        # Weather score
        # --------------------------------------------

        weather_score = calculate_weather_score(
            weather
        )

        # --------------------------------------------
        # Places score
        # --------------------------------------------

        places = places_by_city.get(
            city,
            {
                "city": city,
                "places": []
            }
        )

        places_score = calculate_places_score(
            places
        )

        # --------------------------------------------
        # Combined score
        # --------------------------------------------

        total_score = calculate_total_score(
            weather_score,
            places_score
        )

        scores[city] = {
            "weather_score": weather_score,
            "places_score": places_score,
            "total_score": total_score
        }

        print(
            f"[SCORING] {city}: "
            f"Weather={weather_score}, "
            f"Places={places_score}, "
            f"Total={total_score}"
        )

    return {
        "scores": scores
    }


# ============================================================
# 3. Rank cities
# ============================================================

def ranking_node(state):

    print("\n[RANKING] Ranking cities...")

    scores = state.get(
        "scores",
        {}
    )

    if not scores:

        print(
            "[RANKING] No scores available."
        )

        return {
            "ranking": []
        }

    # --------------------------------------------
    # Sort cities by total score
    # --------------------------------------------

    ranking = sorted(
        scores.keys(),

        key=lambda city:
            scores[city]["total_score"],

        reverse=True
    )

    print("\n[RANKING] Result:")

    for index, city in enumerate(
        ranking,
        start=1
    ):

        score = scores[city]["total_score"]

        print(
            f"{index}. "
            f"{city} - "
            f"{score}/10"
        )


    # --------------------------------------------
    # Detect highest-score ties
    # --------------------------------------------

    highest_score = scores[
        ranking[0]
    ]["total_score"]

    top_cities = [
        city
        for city in ranking
        if scores[city]["total_score"] == highest_score
    ]


    if len(top_cities) > 1:

        print(
            "\n[RANKING] Tie detected:"
        )

        print(
            ", ".join(top_cities)
        )

    else:

        print(
            f"\n[RANKING] Winner: "
            f"{top_cities[0]}"
        )


    return {
        "ranking": ranking
    }


# ============================================================
# 4. Generate final travel recommendation
# ============================================================

def create_final_response_node(llm):

    def final_response_node(state):

        print(
            "\n[FINAL] Generating final travel recommendation..."
        )

        weather_data = state.get(
            "weather_data",
            []
        )

        places_data = state.get(
            "places_data",
            []
        )

        scores = state.get(
            "scores",
            {}
        )

        ranking = state.get(
            "ranking",
            []
        )

        user_request = state.get(
            "user_request",
            ""
        )


        # ====================================================
        # Check whether ranking data exists
        # ====================================================

        if not ranking:

            return {
                "final_response":
                    "I could not generate a travel recommendation "
                    "because no city ranking was available."
            }


        # ====================================================
        # Identify top cities
        # ====================================================

        highest_score = scores[
            ranking[0]
        ]["total_score"]

        top_cities = [
            city
            for city in ranking
            if scores[city]["total_score"]
            == highest_score
        ]


        # ====================================================
        # Build prompt for Gemini
        # ====================================================

        final_prompt = f"""
You are a professional travel planning assistant.

The user asked:

{user_request}


VERIFIED WEATHER DATA:

{weather_data}


VERIFIED SIGHTSEEING DATA:

{places_data}


CALCULATED SCORES:

{scores}


CITY RANKING:

{ranking}


TOP CITY/CITIES:

{top_cities}


HIGHEST SCORE:

{highest_score}/10


Create the final travel recommendation.

IMPORTANT RULES:

1. Use the calculated scores exactly as provided.

2. Do not change the ranking.

3. Do not invent weather information.

4. Do not invent sightseeing places.

5. If multiple cities have the same highest score,
   clearly state that there is a tie.

6. Do not pretend that one city has a higher score
   when the scores are equal.

7. Explain the recommendation using the verified
   weather and sightseeing information.

8. Include:

   - Weather summary
   - Sightseeing summary
   - Weather score
   - Sightseeing score
   - Total score
   - City ranking
   - Final recommendation

9. Keep the response professional and easy to understand.

10. If there is a tie, explain that the cities are
    equally ranked according to the application's
    scoring system.
"""


        # ====================================================
        # Call Gemini
        # ====================================================

        try:

            response = llm.invoke(
                final_prompt
            )

        except Exception as e:

            error_message = str(e)

            print(
                "\n[FINAL] Gemini final-response call failed."
            )

            print(
                f"[FINAL] Error: {error_message}"
            )


            # ------------------------------------------------
            # API / quota fallback
            # ------------------------------------------------

            if (
                "429" in error_message
                or
                "RESOURCE_EXHAUSTED" in error_message
                or
                "quota" in error_message.lower()
            ):

                print(
                    "[FINAL] Gemini quota exceeded."
                )

                if len(top_cities) > 1:

                    city_names = ", ".join(
                        top_cities
                    )

                    final_response = (
                        f"The current scoring system results "
                        f"in a tie between {city_names}, "
                        f"with each city scoring "
                        f"{highest_score}/10."
                    )

                else:

                    winner = top_cities[0]

                    final_response = (
                        f"The best city for your weekend "
                        f"trip is {winner}, with a score "
                        f"of {highest_score}/10."
                    )

                return {
                    "final_response": final_response
                }


            # ------------------------------------------------
            # Generic fallback
            # ------------------------------------------------

            if len(top_cities) > 1:

                city_names = ", ".join(
                    top_cities
                )

                final_response = (
                    f"Based on the calculated scores, "
                    f"{city_names} are tied for first place "
                    f"with a score of "
                    f"{highest_score}/10."
                )

            else:

                winner = top_cities[0]

                final_response = (
                    f"Based on the calculated scores, "
                    f"{winner} is ranked first with a "
                    f"score of {highest_score}/10."
                )


            return {
                "final_response": final_response
            }


        # ====================================================
        # Extract Gemini response
        # ====================================================

        content = response.content


        if isinstance(content, list):

            text_parts = []

            for item in content:

                if (
                    isinstance(item, dict)
                    and item.get("type") == "text"
                ):

                    text_parts.append(
                        item["text"]
                    )

            final_response = "\n".join(
                text_parts
            )

        else:

            final_response = content


        print(
            "[FINAL] Final recommendation generated."
        )


        return {
            "final_response": final_response
        }


    return final_response_node