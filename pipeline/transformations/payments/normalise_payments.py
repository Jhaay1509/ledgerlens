from decimal import Decimal
from datetime import datetime, timezone
from pipeline.utils import get_data


STATUS_MAP = {
    "success":   "succeeded",
    "COMPLETED": "succeeded",
    "paid":      "succeeded",
    "failure":   "failed",
    "DENIED":    "failed",
    "declined":  "failed",
    "pending":   "pending",
}



sql= """
SELECT * FROM stg_payments
"""

def normalise_amount(row):
    amount = row["amount"]
    provider= row["provider"]

    if provider == "fastpay":
        return Decimal(str(amount))/ Decimal("100")

    else:
        return Decimal(str(amount))


    
def normalise_timestamp(ts):
    if isinstance(ts, str):
        # Check if it's an epoch integer stored as string
        if ts.strip().isdigit():
            return datetime.fromtimestamp(int(ts), tz=timezone.utc)
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return datetime.strptime(ts, "%d/%m/%Y %H:%M").replace(tzinfo=timezone.utc)
    elif isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    return ts

def normalise_status(raw_status):
    return STATUS_MAP.get(raw_status, "pending")

def normalise_payment():
    data= get_data(sql)
    normalised = []
    for row in data:
        payment= {
            "payment_id": row.get("payment_id"),
            "provider": row.get("provider"),
            "amount": normalise_amount(row),
            "currency": row.get("currency"),
            "status": normalise_status(row.get("status")),
            "order_id": row.get("order_id"),
            "timestamp": normalise_timestamp(row.get("timestamp"))
        }
        normalised.append(payment)
    return normalised

if __name__ == "__main__":
    result = normalise_payment()
    print(f"{len(result)} payments normalised")

