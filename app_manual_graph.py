from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    HumanMessage,
    SystemMessage
)

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from weather_tool import get_weather
from places_tool import get_places

from travel_state import TravelState

from travel_nodes import (
    collect_data_node,
    scoring_node,
    ranking_node,
    create_final_response_node
)


# ============================================================
# 1. Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# 2. Create Gemini model
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# ============================================================
# 3. Register tools
# ============================================================

tools = [
    get_weather,
    get_places
]


# ============================================================
# 4. Bind tools to Gemini
# ============================================================

llm_with_tools = llm.bind_tools(
    tools
)


# ============================================================
# 5. System Prompt
# ============================================================

SYSTEM_PROMPT = """
You are a Weather and Travel Planning Agent.

You have access to two tools:

1. get_weather(city)
   - Gets current weather information.

2. get_places(city)
   - Gets popular sightseeing places.

Rules:

1. If the user asks for current weather,
   ALWAYS use get_weather.

2. If the user asks about sightseeing,
   ALWAYS use get_places.

3. If the user asks to compare multiple cities
   for a trip, use BOTH tools for EVERY city
   mentioned by the user.

4. Never invent weather information.

5. Never invent sightseeing information.

6. Treat tool results as the source of
   weather and sightseeing information.

7. Do not calculate travel scores yourself.
   The scoring node handles scoring.

8. Do not rank cities yourself.
   The ranking node handles ranking.

9. Do not claim that rain is absent unless
   the weather tool explicitly provides that
   information.

10. Request all required tools before allowing
    the workflow to continue.

Keep your tool requests precise.
"""


# ============================================================
# 6. Helper: Detect Gemini quota errors
# ============================================================

def is_quota_error(error):

    error_message = str(error)

    return (
        "429" in error_message
        or
        "RESOURCE_EXHAUSTED" in error_message
        or
        "quota" in error_message.lower()
    )


# ============================================================
# 7. Agent Node
# ============================================================

def agent_node(state: TravelState):

    print("\n[AGENT] Analyzing request...")

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        )
    ] + state["messages"]

    try:

        response = llm_with_tools.invoke(
            messages
        )

    except Exception as e:

        print(
            "\n[AGENT] Gemini API call failed."
        )

        print(
            f"[AGENT] Error: {e}"
        )

        if is_quota_error(e):

            print(
                "\n[AGENT] Gemini API quota exceeded."
            )

            print(
                "[AGENT] The graph cannot perform "
                "LLM tool selection until the quota "
                "is available again."
            )

            return {
                "agent_error": (
                    "Gemini API quota exceeded. "
                    "Please try again later."
                )
            }

        # For non-quota errors, raise the exception
        # because they indicate an unexpected problem.

        raise


    # ========================================================
    # Display tool calls
    # ========================================================

    if response.tool_calls:

        for tool_call in response.tool_calls:

            print(
                f"[AGENT] Requested tool: "
                f"{tool_call['name']}"
            )

            print(
                f"[AGENT] Arguments: "
                f"{tool_call['args']}"
            )

    else:

        print(
            "[AGENT] No tool required."
        )


    return {
        "messages": [response]
    }


# ============================================================
# 8. Tool Node
# ============================================================

tool_node = ToolNode(
    tools
)


# ============================================================
# 9. Final Response Node
# ============================================================

final_response_node = create_final_response_node(
    llm
)


# ============================================================
# 10. Create StateGraph
# ============================================================

graph_builder = StateGraph(
    TravelState
)


# ============================================================
# 11. Add Nodes
# ============================================================

graph_builder.add_node(
    "agent",
    agent_node
)

graph_builder.add_node(
    "tools",
    tool_node
)

graph_builder.add_node(
    "collect_data",
    collect_data_node
)

graph_builder.add_node(
    "scoring",
    scoring_node
)

graph_builder.add_node(
    "ranking",
    ranking_node
)

graph_builder.add_node(
    "final_response",
    final_response_node
)


# ============================================================
# 12. START → Agent
# ============================================================

graph_builder.add_edge(
    START,
    "agent"
)


# ============================================================
# 13. Agent → Tools OR END
# ============================================================

graph_builder.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)


# ============================================================
# 14. Tools → Collect Data
# ============================================================

graph_builder.add_edge(
    "tools",
    "collect_data"
)


# ============================================================
# 15. Collect Data → Scoring
# ============================================================

graph_builder.add_edge(
    "collect_data",
    "scoring"
)


# ============================================================
# 16. Scoring → Ranking
# ============================================================

graph_builder.add_edge(
    "scoring",
    "ranking"
)


# ============================================================
# 17. Ranking → Final Response
# ============================================================

graph_builder.add_edge(
    "ranking",
    "final_response"
)


# ============================================================
# 18. Final Response → END
# ============================================================

graph_builder.add_edge(
    "final_response",
    END
)


# ============================================================
# 19. Compile Graph
# ============================================================

graph = graph_builder.compile()


# ============================================================
# 20. Get User Input
# ============================================================

user_request = input(
    "What would you like to know? "
)


# ============================================================
# 21. Start Graph
# ============================================================

print(
    "\n[GRAPH] Starting LangGraph..."
)


try:

    result = graph.invoke(
        {
            "user_request": user_request,

            "messages": [
                HumanMessage(
                    content=user_request
                )
            ]
        }
    )


except Exception as e:

    print(
        "\n=============================="
    )

    print(
        "GRAPH EXECUTION ERROR"
    )

    print(
        "==============================\n"
    )

    print(e)

    print(
        "\nThe application could not complete "
        "the request."
    )

    raise SystemExit(1)


# ============================================================
# 22. Handle Agent Error
# ============================================================

if result.get("agent_error"):

    print(
        "\n=============================="
    )

    print(
        "WEATHER AGENT STATUS"
    )

    print(
        "==============================\n"
    )

    print(
        result["agent_error"]
    )

    print(
        "\nYour Gemini API quota needs to become "
        "available before the agent can make "
        "tool-selection requests."
    )

    raise SystemExit(0)


# ============================================================
# 23. Display Scores
# ============================================================

print(
    "\n=============================="
)

print(
    "TRAVEL AGENT RESULTS"
)

print(
    "==============================\n"
)


print("Scores:")


scores = result.get(
    "scores",
    {}
)


if scores:

    for city, score in scores.items():

        print(
            f"{city}: "
            f"Weather={score['weather_score']}, "
            f"Places={score['places_score']}, "
            f"Total={score['total_score']}"
        )

else:

    print(
        "No scores available."
    )


# ============================================================
# 24. Display Ranking
# ============================================================

print("\nRanking:")


ranking = result.get(
    "ranking",
    []
)


if ranking:

    for index, city in enumerate(
        ranking,
        start=1
    ):

        print(
            f"{index}. {city}"
        )

else:

    print(
        "No ranking available."
    )


# ============================================================
# 25. Display Final Response
# ============================================================

print(
    "\n=============================="
)

print(
    "FINAL TRAVEL AGENT RESPONSE"
)

print(
    "==============================\n"
)


print(
    result.get(
        "final_response",
        "No final response generated."
    )
)