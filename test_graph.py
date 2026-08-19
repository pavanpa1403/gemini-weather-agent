from travel_nodes import (
    scoring_node,
    ranking_node
)


# ============================================================
# Sample weather data
# ============================================================

weather_data = [

    {
        "city": "Hyderabad",
        "temperature": "26",
        "humidity": "71",
        "wind_speed": "13",
        "condition": "Overcast"
    },

    {
        "city": "Chennai",
        "temperature": "30",
        "humidity": "72",
        "wind_speed": "20",
        "condition": "Overcast"
    },

    {
        "city": "Mumbai",
        "temperature": "28",
        "humidity": "80",
        "wind_speed": "25",
        "condition": "Patchy rain nearby"
    }
]


# ============================================================
# Sample sightseeing data
# ============================================================

places_data = [

    {
        "city": "Hyderabad",
        "places": [
            "Charminar",
            "Golconda Fort",
            "Chowmahalla Palace",
            "Salar Jung Museum",
            "Hussain Sagar Lake"
        ]
    },

    {
        "city": "Chennai",
        "places": [
            "Marina Beach",
            "Kapaleeshwarar Temple",
            "Fort St. George",
            "San Thome Basilica",
            "Elliot's Beach"
        ]
    },

    {
        "city": "Mumbai",
        "places": [
            "Gateway of India",
            "Marine Drive",
            "Colaba Causeway",
            "Elephanta Caves",
            "Chhatrapati Shivaji Maharaj Terminus"
        ]
    }
]


# ============================================================
# Create initial state
# ============================================================

state = {

    "weather_data": weather_data,

    "places_data": places_data
}


# ============================================================
# 1. Run scoring node
# ============================================================

print("\n==============================")
print("OFFLINE LANGGRAPH TEST")
print("==============================")

print(
    "\n[TEST] Running scoring node..."
)


scoring_result = scoring_node(
    state
)


# Add scores to state

state.update(
    scoring_result
)


# ============================================================
# 2. Run ranking node
# ============================================================

print(
    "\n[TEST] Running ranking node..."
)


ranking_result = ranking_node(
    state
)


# Add ranking to state

state.update(
    ranking_result
)


# ============================================================
# 3. Display final results
# ============================================================

print("\n==============================")
print("OFFLINE TEST RESULTS")
print("==============================\n")


print("Scores:")


for city, score in state[
    "scores"
].items():

    print(
        f"{city}: "
        f"Weather={score['weather_score']}, "
        f"Places={score['places_score']}, "
        f"Total={score['total_score']}"
    )


print("\nRanking:")


for index, city in enumerate(
    state["ranking"],
    start=1
):

    print(
        f"{index}. {city}"
    )


# ============================================================
# 4. Detect winner / tie
# ============================================================

ranking = state["ranking"]

scores = state["scores"]


if ranking:

    highest_score = scores[
        ranking[0]
    ]["total_score"]


    top_cities = [

        city

        for city in ranking

        if scores[city]["total_score"]
        == highest_score
    ]


    print(
        "\n=============================="
    )

    print(
        "FINAL DECISION"
    )

    print(
        "==============================\n"
    )


    if len(top_cities) > 1:

        print(
            "Tie detected between:"
        )

        print(
            ", ".join(top_cities)
        )

        print(
            f"\nScore: {highest_score}/10"
        )

    else:

        print(
            f"Winner: {top_cities[0]}"
        )

        print(
            f"Score: {highest_score}/10"
        )