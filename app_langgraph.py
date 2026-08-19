import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from langchain.agents import create_agent

from weather_tool import get_weather


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
    get_weather
]


# ============================================
# 4. Create LangGraph agent
# ============================================

agent = create_agent(
    model=llm,
    tools=tools
)


# ============================================
# 5. Get user input
# ============================================

user_request = input(
    "What would you like to know? "
)


# ============================================
# 6. Run the LangGraph agent
# ============================================

result = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content=user_request
            )
        ]
    }
)


# ============================================
# 7. Get final AI message
# ============================================

final_message = result["messages"][-1]

print("\n==============================")
print("FINAL WEATHER AGENT RESPONSE")
print("==============================\n")


# ============================================
# 8. Extract clean text from Gemini response
# ============================================

content = final_message.content

if isinstance(content, list):

    for item in content:

        if isinstance(item, dict) and item.get("type") == "text":

            print(item["text"])

else:

    print(content)