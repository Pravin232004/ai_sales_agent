import asyncio
import os
import re
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.sales_agent import run_sales_agent
from app.tools.calendar_tools import check_demo_availability


# ============================================================
# Configuration
# ============================================================

# IMPORTANT:
# Keep this False while Gemini quota/API is unavailable.
#
# Later, when Gemini is working again, change this to:
#
# ENABLE_LIVE_GEMINI=true
#
# in your .env file.
#
ENABLE_LIVE_GEMINI = (
    os.getenv("ENABLE_LIVE_GEMINI", "false").lower()
    == "true"
)

# Maximum time allowed for Gemini when live mode is enabled.
GEMINI_TIMEOUT_SECONDS = 5


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="AI Sales Workforce Agent",
    version="1.0.0"
)


# ============================================================
# CORS Configuration
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request Model
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Sales Workforce Agent API is running"
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# Detect Demo Booking Intent
# ============================================================

def is_demo_request(message: str) -> bool:

    text = message.lower()

    demo_keywords = [
        "book a demo",
        "book demo",
        "schedule a demo",
        "schedule demo",
        "check demo",
        "demo availability",
        "product demonstration",
        "demonstration",
        "book a demonstration",
        "schedule a demonstration",
    ]

    return any(
        keyword in text
        for keyword in demo_keywords
    )


# ============================================================
# Extract Date and Time
# ============================================================

def extract_demo_datetime(message: str):

    text = message.strip()

    # --------------------------------------------------------
    # ISO date
    # Example: 2026-10-10
    # --------------------------------------------------------

    date_match = re.search(
        r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b",
        text
    )

    date_value = None

    if date_match:

        year = int(date_match.group(1))
        month = int(date_match.group(2))
        day = int(date_match.group(3))

        try:
            parsed_date = datetime(
                year,
                month,
                day
            )

            date_value = parsed_date.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            date_value = None

    # --------------------------------------------------------
    # Month-name date
    # Example:
    # October 10, 2026
    # October 10 2026
    # --------------------------------------------------------

    if date_value is None:

        month_pattern = (
            r"\b("
            r"January|February|March|April|May|June|"
            r"July|August|September|October|November|December"
            r")"
            r"\s+(\d{1,2})"
            r"(?:st|nd|rd|th)?"
            r"(?:,\s*|\s+)"
            r"(20\d{2})\b"
        )

        month_match = re.search(
            month_pattern,
            text,
            re.IGNORECASE
        )

        if month_match:

            month_name = month_match.group(1)
            day = int(month_match.group(2))
            year = int(month_match.group(3))

            try:

                parsed_date = datetime.strptime(
                    f"{month_name} {day} {year}",
                    "%B %d %Y"
                )

                date_value = parsed_date.strftime(
                    "%Y-%m-%d"
                )

            except ValueError:

                date_value = None

    # --------------------------------------------------------
    # Time
    # Examples:
    # 3 PM
    # 3:00 PM
    # --------------------------------------------------------

    time_value = None

    time_match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)\b",
        text
    )

    if time_match:

        hour = int(time_match.group(1))

        minute = int(
            time_match.group(2) or "00"
        )

        meridiem = time_match.group(3).upper()

        if meridiem == "PM" and hour != 12:
            hour += 12

        if meridiem == "AM" and hour == 12:
            hour = 0

        if 0 <= hour <= 23 and 0 <= minute <= 59:

            time_value = (
                f"{hour:02d}:{minute:02d}"
            )

    # --------------------------------------------------------
    # 24-hour time
    # Example:
    # 15:00
    # 09:30
    # --------------------------------------------------------

    if time_value is None:

        time_24_match = re.search(
            r"\b([01]?\d|2[0-3]):([0-5]\d)\b",
            text
        )

        if time_24_match:

            hour = int(
                time_24_match.group(1)
            )

            minute = int(
                time_24_match.group(2)
            )

            time_value = (
                f"{hour:02d}:{minute:02d}"
            )

    return date_value, time_value


# ============================================================
# Handle Demo Booking
# ============================================================

def handle_demo_request(message: str) -> dict:

    date_value, time_value = (
        extract_demo_datetime(message)
    )

    # --------------------------------------------------------
    # Date/time not provided
    # --------------------------------------------------------

    if not date_value or not time_value:

        return {
            "response": (
                "I'd be happy to help schedule a "
                "product demonstration.\n\n"
                "Please provide your preferred date "
                "and time.\n\n"
                "For example:\n"
                "October 10, 2026 at 3:00 PM"
            ),
            "lead_captured": None,
            "mode": "demo_booking"
        }

    # --------------------------------------------------------
    # Check calendar tool
    # --------------------------------------------------------

    result = check_demo_availability(
        date=date_value,
        time=time_value
    )

    # --------------------------------------------------------
    # Slot unavailable
    # --------------------------------------------------------

    if not result.get("available"):

        return {
            "response": (
                f"Sorry, the demo slot on "
                f"{date_value} at {time_value} "
                f"is currently unavailable.\n\n"
                "Please choose another date or time."
            ),
            "lead_captured": None,
            "mode": "demo_booking",
            "calendar_result": result
        }

    # --------------------------------------------------------
    # Slot available
    # --------------------------------------------------------

    return {
        "response": (
            f"Great! The demo slot on "
            f"{date_value} at {time_value} "
            f"is available. ✅\n\n"
            "To complete the demo booking, please "
            "provide your full name, email address, "
            "and company name."
        ),
        "lead_captured": None,
        "mode": "demo_booking",
        "calendar_result": result
    }


# ============================================================
# Demo / Offline Fallback
# ============================================================

def demo_fallback(message: str) -> dict:

    text = message.lower().strip()

    # --------------------------------------------------------
    # Product question
    # --------------------------------------------------------

    if any(
        word in text
        for word in [
            "product",
            "products",
            "platform",
            "what do you offer",
            "what do you provide"
        ]
    ):

        return {
            "response": (
                "Our AI Sales Workforce Platform helps "
                "businesses automate repetitive sales and "
                "customer-engagement tasks using AI agents.\n\n"
                "The platform is designed around "
                "conversational AI, RAG-based knowledge "
                "retrieval, automated workflows, lead "
                "management, and sales automation."
            ),
            "lead_captured": None,
            "mode": "demo_fallback"
        }

    # --------------------------------------------------------
    # Pricing question
    # --------------------------------------------------------

    if any(
        word in text
        for word in [
            "price",
            "pricing",
            "cost",
            "plan",
            "plans"
        ]
    ):

        return {
            "response": (
                "I can help with pricing information. "
                "The live Gemini service is currently "
                "unavailable because the API quota has "
                "been reached, so I don't want to invent "
                "or provide incorrect pricing details.\n\n"
                "Please connect with the sales team for "
                "the latest pricing information."
            ),
            "lead_captured": None,
            "mode": "demo_fallback"
        }

    # --------------------------------------------------------
    # Sales contact
    # --------------------------------------------------------

    if any(
        word in text
        for word in [
            "talk to sales",
            "contact sales",
            "sales team",
            "speak to sales"
        ]
    ):

        return {
            "response": (
                "Sure. I can help connect you with "
                "the sales team.\n\n"
                "Please provide your name, email address, "
                "company name, and what solution you're "
                "interested in."
            ),
            "lead_captured": None,
            "mode": "demo_fallback"
        }

    # --------------------------------------------------------
    # Default fallback
    # --------------------------------------------------------

    return {
        "response": (
            "The AI service is temporarily unavailable "
            "because the Gemini API quota has been reached.\n\n"
            "Demo mode is active. You can still explore "
            "the sales assistant."
        ),
        "lead_captured": None,
        "mode": "demo_fallback"
    }


# ============================================================
# Chat Endpoint
# ============================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    message = request.message.strip()

    # --------------------------------------------------------
    # Empty message
    # --------------------------------------------------------

    if not message:

        return {
            "response": "Please enter a message.",
            "lead_captured": None,
            "mode": "validation"
        }

    # ========================================================
    # Handle demo requests BEFORE Gemini
    # ========================================================

    date_value, time_value = (
        extract_demo_datetime(message)
    )

    if (
        is_demo_request(message)
        or (date_value and time_value)
    ):

        print(
            f"Demo booking request detected: {message}"
        )

        return handle_demo_request(message)

    # ========================================================
    # SAFE OFFLINE MODE
    # ========================================================

    # Gemini is disabled by default.
    #
    # This prevents the application from hanging when
    # the Gemini API is unavailable or quota-limited.

    if not ENABLE_LIVE_GEMINI:

        print(
            "Gemini live mode disabled. "
            "Using demo fallback."
        )

        return demo_fallback(message)

    # ========================================================
    # Live Gemini Agent
    # ========================================================

    try:

        print(
            "Sending request to Gemini..."
        )

        result = await asyncio.wait_for(
            asyncio.to_thread(
                run_sales_agent,
                message
            ),
            timeout=GEMINI_TIMEOUT_SECONDS
        )

        if isinstance(result, dict):

            result.setdefault(
                "mode",
                "ai"
            )

        return result

    # ========================================================
    # Gemini Timeout
    # ========================================================

    except asyncio.TimeoutError:

        print(
            "Gemini request timed out. "
            "Using demo fallback."
        )

        return demo_fallback(message)

    # ========================================================
    # Gemini / Backend Error
    # ========================================================

    except Exception as e:

        error_message = str(e)

        print(
            "\n========================================"
        )

        print(
            "AI BACKEND ERROR"
        )

        print(
            "========================================"
        )

        print(
            error_message
        )

        print(
            "========================================\n"
        )

        return demo_fallback(message)