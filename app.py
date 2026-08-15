import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

from weather_tool import get_weather


# ============================================
# 1. Load environment variables
# ============================================

load_dotenv()


# ============================================
# 2. Create Gemini client
# ============================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================
# 3. Define weather tool for Gemini
# ============================================

weather_tool = {
    "name": "get_weather",
    "description": "Get the current weather information for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Name of the city"
            }
        },
        "required": ["city"]
    }
}


# ============================================
# 4. Agent function
# ============================================

def run_agent(user_request):

    # Conversation history
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=user_request)
            ]
        )
    ]

    # First Gemini request
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    function_declarations=[weather_tool]
                )
            ]
        )
    )

    # ========================================
    # 5. Check whether Gemini requested tools
    # ========================================

    if response.function_calls:

        print("\nGemini requested weather information.\n")

        # Add Gemini's response to conversation
        contents.append(
            response.candidates[0].content
        )

        function_response_parts = []

        # ====================================
        # 6. Execute tool calls
        # ====================================

        for function_call in response.function_calls:

            if function_call.name == "get_weather":

                city = function_call.args["city"]

                print(f"Getting weather for: {city}")

                weather_result = get_weather(city)

                print(f"Weather for {city}:")
                print(weather_result)
                print()

                # Create function response
                function_response_part = (
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={
                            "result": weather_result
                        }
                    )
                )

                function_response_parts.append(
                    function_response_part
                )

        # ====================================
        # 7. Send tool results back to Gemini
        # ====================================

        contents.append(
            types.Content(
                role="user",
                parts=function_response_parts
            )
        )

        # ====================================
        # 8. Ask Gemini for final reasoning
        # ====================================

        decision_instruction = """
You are the final decision-maker for this travel request.

Analyze the weather information collected for all
requested cities.

Evaluate each city using:

1. Temperature comfort
2. Humidity
3. Rain conditions
4. Wind conditions
5. Suitability for outdoor activities

Give each city a travel score from 1 to 10.

Then provide:

1. Weather summary for each city
2. Score for each city
3. Ranking from best to worst
4. ONE clear best city
5. Short explanation for the choice
6. Clothing recommendation
7. Umbrella recommendation

You must select ONE best city based primarily
on the current weather data.

Give the answer in a clear and easy-to-understand format.
"""

        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=decision_instruction
                    )
                ]
            )
        )

        # Final Gemini request
        final_response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        function_declarations=[weather_tool]
                    )
                ]
            )
        )

        return final_response.text

    else:

        return response.text


# ============================================
# 9. Main program
# ============================================

if __name__ == "__main__":

    user_request = input(
        "What would you like to know? "
    )

    result = run_agent(user_request)

    print("\n==============================")
    print("FINAL WEATHER AGENT RESPONSE")
    print("==============================\n")

    print(result)