import os
from google import genai
from dotenv import load_dotenv
from weather_tool import get_weather

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Ask the user for multiple cities
cities = input(
    "Enter cities separated by comma: "
).split(",")

all_weather = {}

# Get weather for each city
for city in cities:
    city = city.strip()

    if city:
        all_weather[city] = get_weather(city)

# Create prompt for Gemini
prompt = f"""
You are a travel planning assistant.

Here is the current weather information
for multiple cities:

{all_weather}

Compare the cities.

Provide:

1. Weather summary for each city
2. Best city for a weekend trip
3. Reason for your recommendation
4. Clothing recommendation
5. Umbrella recommendation
6. Overall travel rating

Give a clear final recommendation.
"""

# Send information to Gemini
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)

print("\nWeather Agent Response:\n")
print(response.text)