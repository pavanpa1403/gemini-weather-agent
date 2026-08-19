import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from weather_tool import get_weather


# ============================================
# 1. Load environment variables
# ============================================

load_dotenv()


# ============================================
# 2. Create Gemini LLM
# ============================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
  
)


# ============================================
# 3. Give the tool to Gemini
# ============================================

llm_with_tools = llm.bind_tools(
    [get_weather]
)


# ============================================
# 4. Test Gemini + Tool
# ============================================

user_request = input(
    "What would you like to know? "
)


response = llm_with_tools.invoke(
    user_request
)


print("\n==============================")
print("GEMINI RESPONSE")
print("==============================\n")

print(response.content)


# ============================================
# 5. Check whether Gemini requested a tool
# ============================================

if response.tool_calls:

    print("\n==============================")
    print("TOOL CALL REQUESTED")
    print("==============================\n")

    for tool_call in response.tool_calls:

        print("Tool:", tool_call["name"])
        print("Arguments:", tool_call["args"])