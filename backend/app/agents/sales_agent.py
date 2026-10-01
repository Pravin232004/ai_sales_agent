import os
import json

from dotenv import load_dotenv
from google import genai

from app.rag.retriever import search_knowledge
from app.tools.calendar_tools import check_demo_availability
from app.tools.lead_tools import capture_lead


# ---------------------------------------------------------
# Environment and Gemini client
# ---------------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

client = genai.Client(api_key=api_key)


# ---------------------------------------------------------
# RAG context
# ---------------------------------------------------------

def get_rag_context(user_message: str) -> str:
    """
    Retrieve relevant information from the knowledge base.
    """

    results = search_knowledge(user_message, top_k=3)

    if not results:
        return "No relevant information was found in the knowledge base."

    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"{result['text']}"
        )

    return "\n\n---\n\n".join(context_parts)


# ---------------------------------------------------------
# Tool declarations
# ---------------------------------------------------------

calendar_tool = {
    "type": "function",
    "name": "check_demo_availability",
    "description": (
        "Check whether a product demonstration is available "
        "at a requested date and time."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Requested date in YYYY-MM-DD format."
            },
            "time": {
                "type": "string",
                "description": "Requested time in HH:MM 24-hour format."
            }
        },
        "required": ["date", "time"]
    }
}


lead_capture_tool = {
    "type": "function",
    "name": "capture_lead",
    "description": (
        "Save information about a potential customer as a new lead."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Full name of the customer."
            },
            "email": {
                "type": "string",
                "description": "Email address of the customer."
            },
            "company": {
                "type": "string",
                "description": "Company where the customer works."
            },
            "interest": {
                "type": "string",
                "description": "Product, service, or solution the customer is interested in."
            }
        },
        "required": ["name", "email", "company", "interest"]
    }
}


TOOLS = [
    calendar_tool,
    lead_capture_tool
]


# ---------------------------------------------------------
# Tool execution
# ---------------------------------------------------------

def execute_tool(function_name: str, arguments: dict) -> dict:
    """
    Execute the tool selected by Gemini.
    """

    if function_name == "check_demo_availability":
        return check_demo_availability(
            date=arguments["date"],
            time=arguments["time"]
        )

    if function_name == "capture_lead":
        return capture_lead(
            name=arguments["name"],
            email=arguments["email"],
            company=arguments["company"],
            interest=arguments["interest"]
        )

    return {
        "success": False,
        "error": f"Unknown tool: {function_name}"
    }


# ---------------------------------------------------------
# AI Sales Agent
# ---------------------------------------------------------

def run_sales_agent(user_message: str) -> str:
    """
    Run the AI Sales Agent using Gemini Interactions API,
    RAG, and custom function tools.
    """

    # Retrieve relevant company information
    rag_context = get_rag_context(user_message)

    system_instruction = f"""
You are an AI Sales Agent for an AI Sales Workforce Platform.

Your responsibilities:

1. Answer customer questions using the provided knowledge base.
2. Use the check_demo_availability tool when the customer
   asks about product demonstration availability.
3. Use the capture_lead tool when the customer provides
   lead information and asks to save or register it.
4. Do not invent company information, products, pricing,
   or capabilities.
5. If the knowledge base does not contain the answer,
   clearly say that you do not have enough information.
6. Be professional, helpful, and concise.

KNOWLEDGE BASE:
----------------
{rag_context}
----------------
"""

    # -----------------------------------------------------
    # First interaction
    # -----------------------------------------------------

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=f"""
{system_instruction}

CUSTOMER MESSAGE:
{user_message}
""",
        tools=TOOLS
    )

    # -----------------------------------------------------
    # Check whether Gemini requested any tools
    # -----------------------------------------------------

    function_calls = [
        step
        for step in interaction.steps
        if step.type == "function_call"
    ]

    # -----------------------------------------------------
    # No tool required
    # -----------------------------------------------------

    if not function_calls:
        return interaction.output_text

    # -----------------------------------------------------
    # Execute requested tools
    # -----------------------------------------------------

    function_results = []

    for function_call in function_calls:

        print(
            f"\nTool requested: {function_call.name}"
        )

        print(
            f"Arguments: {function_call.arguments}"
        )

        result = execute_tool(
            function_call.name,
            function_call.arguments
        )

        print(
            f"Tool result: {result}"
        )

        function_results.append(
            {
                "type": "function_result",
                "name": function_call.name,
                "call_id": function_call.id,
                "result": [
                    {
                        "type": "text",
                        "text": json.dumps(result)
                    }
                ]
            }
        )

    # -----------------------------------------------------
    # Send tool results back to Gemini
    # -----------------------------------------------------

    final_interaction = client.interactions.create(
        model="gemini-3.6-flash",
        previous_interaction_id=interaction.id,
        input=function_results,
        tools=TOOLS
    )

    return final_interaction.output_text


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    message = (
    "Hi, my name is Pravin Kumar. "
    "My email is pravin@example.com. "
    "I work at ABC Technologies. "
    "I am interested in your AI automation solution. "
    "Please save my details as a new lead."
)

    result = run_sales_agent(message)

    print("\nCustomer:")
    print(message)

    print("\nAI Sales Agent:")
    print(result)