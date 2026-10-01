def capture_lead(
    name: str,
    email: str,
    company: str,
    interest: str
) -> dict:
    """
    Capture information about a potential customer.

    Args:
        name: Customer's name.
        email: Customer's email address.
        company: Customer's company.
        interest: Product or service the customer is interested in.

    Returns:
        Dictionary containing the captured lead information.
    """

    lead = {
        "name": name,
        "email": email,
        "company": company,
        "interest": interest,
        "status": "new"
    }

    return {
        "success": True,
        "message": "Lead information captured successfully.",
        "lead": lead
    }