import stripe
from datetime import datetime, timedelta

def get_recent_payouts(limit=10, days=30):
    """
    Retrieve recent Stripe payouts for the last `days` days.
    """
    # Calculate Unix timestamp for start_date
    start_date = datetime.utcnow() - timedelta(days=days)
    start_unix = int(start_date.timestamp())

    # Stripe API call
    payouts = stripe.Payout.list(
        limit=limit,
        arrival_date={
            "gte": start_unix
        }
    )
    return payouts.data  # This is a list of Payout objects


def get_charges_revenue(days=30):
    """
    Retrieve total revenue of Stripe charges in the last `days` days (in cents).
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    start_unix = int(start_date.timestamp())

    charges = stripe.Charge.list(
        created={"gte": start_unix},
        limit=100
    )

    total_revenue = 0
    has_more = charges.has_more

    # Loop over pages if needed
    while True:
        for charge in charges.data:
            if charge.paid and not charge.refunded:
                total_revenue += charge.amount  # 'amount' is in cents

        if not has_more:
            break

        # Paginate if has_more == True
        charges = stripe.Charge.list(
            created={"gte": start_unix},
            limit=100,
            starting_after=charges.data[-1].id
        )
        has_more = charges.has_more

    return total_revenue  # in cents

def format_currency(cents, currency="usd"):
    """
    Convert an integer in cents to a float in dollars (for USD).
    """
    if currency.lower() == "usd":
        return cents / 100.0
    return cents / 100.0  # Adjust for other currencies if needed
