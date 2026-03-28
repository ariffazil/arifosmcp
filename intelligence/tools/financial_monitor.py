import random


async def financial_cost(
    service: str,
    action: str,
    resource_id: str = "",
    period_days: int = 1,
) -> dict:
    """
    MOCK TOOL: Estimates the financial cost of an action from a cloud provider.

    This is a mock implementation. A real implementation would integrate
    with actual cloud billing APIs (e.g., AWS Cost Explorer, GCP Billing API)
    and require proper authentication and permissions.

    Args:
        service (str): Cloud service (e.g., "AWS_EC2", "GCP_Cloud_Run").
        action (str): Resource type (e.g., "compute_hours", "storage_gb").
        resource_id (str): Optional. Specific resource ID to query cost for.
        period_days (int): Days to look back for cost estimation.

    Returns:
        dict: A dictionary containing estimated cost data.
    """
    # Simulate different costs based on inputs
    base_cost = 0.0

    if "compute" in action.lower():
        base_cost = 0.05 * period_days  # $0.05 per day per generic compute unit
    elif "storage" in action.lower():
        base_cost = 0.01 * period_days  # $0.01 per day per generic storage unit
    elif "data_transfer" in action.lower():
        base_cost = 0.002 * period_days  # $0.002 per day per generic data unit
    elif "api_calls" in action.lower():
        base_cost = 0.0001 * period_days  # $0.0001 per day per generic API call

    estimated_amount = round(base_cost * random.uniform(0.8, 1.2), 4)
    currency = "USD"

    mock_response = {
        "service": service,
        "action": action,
        "resource_id": resource_id if resource_id else "generic",
        "period_days": period_days,
        "estimated_cost": f"{estimated_amount} {currency}",
        "raw_amount": estimated_amount,
        "currency": currency,
        "disclaimer": "Mock estimation. Real version requires cloud API integration.",
    }

    return mock_response
