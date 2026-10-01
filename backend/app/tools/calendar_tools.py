def check_demo_availability(date: str, time: str) -> dict:
    """
    Check whether a demo is available at the requested date and time.

    Args:
        date: Requested date in YYYY-MM-DD format.
        time: Requested time in HH:MM format.

    Returns:
        Dictionary containing availability information.
    """

    # Temporary mock calendar.
    # Later, we will replace this with a real calendar API.

    unavailable_slots = {
        ("2026-10-02", "15:00"),
        ("2026-10-03", "11:00"),
    }

    if (date, time) in unavailable_slots:
        return {
            "available": False,
            "date": date,
            "time": time,
            "message": "The requested demo slot is unavailable."
        }

    return {
        "available": True,
        "date": date,
        "time": time,
        "message": "The requested demo slot is available."
    }