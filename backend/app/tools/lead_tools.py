import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def capture_lead(
    name: str,
    email: str,
    company: str,
    interest: str
) -> dict:
    """
    Capture a potential customer lead and save it to PostgreSQL.
    """

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not set in the .env file.")

    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO leads
                    (name, email, company, interest)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (name, email, company, interest)
                )

                lead_id = cursor.fetchone()[0]

        return {
            "success": True,
            "message": "Lead information saved successfully.",
            "lead_id": lead_id,
            "lead": {
                "name": name,
                "email": email,
                "company": company,
                "interest": interest,
                "status": "new"
            }
        }

    except Exception as error:
        return {
            "success": False,
            "message": "Failed to save lead information.",
            "error": str(error)
        }