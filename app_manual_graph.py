from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from weather_tool import get_weather
from places_tool import get_places


# ============================================
# 1. Load environment variables
# ============================================

load_dotenv()


# ============================================
# 2. Create Gemini model
# ============================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# ============================================
# 3. Register tools
# ============================================

tools = [
    get_weather,
    get_places
]


# ============================================
# 4. Bind tools to Gemini
# ============================================

llm_with_tools = llm.bind_tools(tools)


# ============================================
# 5. System Prompt
# ============================================

SYSTEM_PROMPT = """
You are a Weather and Travel Planning Agent.

You have access to two tools:

1. get_weather(city)
   - Gets current weather information for a city.

2. get_places(city)
   - Gets popular sightseeing places for a city.

Rules:

1. If the user asks about current weather,
   ALWAYS use get_weather before answering.

2. If the user asks about sightseeing places,
   ALWAYS use get_places before answering.

3. If the user asks to compare cities for a trip,
   use BOTH get_weather and get_places for every city
   mentioned in the request.

4. Never invent current weather information.

5. Never invent sightseeing information when the
   places tool does not provide data.

6. When comparing cities, consider:
   - Temperature
   - Humidity
   - Wind speed
   - Weather condition
   - Outdoor suitability
   - Number and quality of sightseeing options

7. Give each city a score from 1 to 10 when a comparison
   is requested.

8. Rank the cities from best to worst.

9. Clearly explain why the recommended city was selected.

10. If a tool returns an error, clearly mention that
    information could not be retrieved.

11. Keep the final answer clear and easy to understand.
"""

# ============================================
# 6. Create Agent Node
# ============================================

def agent_node(state: MessagesState):

    print("\n[AGENT] Analyzing request...")

    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        )
    ] + state["messages"]

    response = llm_with_tools.invoke(
        messages
    )

    # Show requested tools
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

        print("[AGENT] No tool required.")

    return {
        "messages": [response]
    }


# ============================================
# 7. Create Tool Node
# ============================================

tool_node = ToolNode(tools)


# ============================================
# 8. Create Graph
# ============================================

graph_builder = StateGraph(
    MessagesState
)


# ============================================
# 9. Add Nodes
# ============================================

graph_builder.add_node(
    "agent",
    agent_node
)

graph_builder.add_node(
    "tools",
    tool_node
)


# ============================================
# 10. START → Agent
# ============================================

graph_builder.add_edge(
    START,
    "agent"
)


# ============================================
# 11. Agent → Tool or END
# ============================================

graph_builder.add_conditional_edges(
    "agent",
    tools_condition
)


# ============================================
# 12. Tool → Agent
# ============================================

graph_builder.add_edge(
    "tools",
    "agent"
)


# ============================================
# 13. Compile Graph
# ============================================

graph = graph_builder.compile()


# ============================================
# 14. Get User Input
# ============================================

user_request = input(
    "What would you like to know? "
)


# ============================================
# 15. Run Graph
# ============================================

print("\n[GRAPH] Starting LangGraph...\n")

result = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content=user_request
            )
        ]
    }
)


# ============================================
# 16. Get Final Response
# ============================================

final_message = result["messages"][-1]


print("\n==============================")
print("FINAL WEATHER AGENT RESPONSE")
print("==============================\n")


content = final_message.content


if isinstance(content, list):

    for item in content:

        if (
            isinstance(item, dict)
            and item.get("type") == "text"
        ):
            print(item["text"])

else:

    print(content)