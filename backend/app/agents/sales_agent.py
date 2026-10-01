import os

from dotenv import load_dotenv
from google import genai

from app.tools.calendar_tools import check_demo_availability
from app.tools.lead_tools import capture_lead


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=api_key)


def run_sales_agent(user_message: str) -> str:

    response = client.models.generate_content(
    model="gemini-3.7-flash",
    contents=user_message,
    config={
        "tools": [
            check_demo_availability,
            capture_lead
        ]
    },
)

    return response.text


if __name__ == "__main__":

    message = (
    "Hi, my name is Pravin Kumar. "
    "My email is pravin@example.com. "
    "I work at ABC Technologies. "
    "I am interested in your AI automation solution. "
    "Please save my details as a new lead."
)

    result = run_sales_agent(message)

    print("\nAgent response:")
    print(result)