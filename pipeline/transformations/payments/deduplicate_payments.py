import sys
import os
from pipeline.transformations.payments.normalise_payments import normalise_payment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

def deduplicate_payments(payments):
    seen = {}
    for payment in payments:
        unique_key = (payment["provider"], payment["payment_id"])
        seen[unique_key] = payment   
    return list(seen.values())

if __name__ == "__main__":
    payments = normalise_payment()
    result = deduplicate_payments(payments)
    print(f"{len(payments)} payments before deduplication")
    print(f"{len(result)} payments after deduplication")
    print(f"{len(payments) - len(result)} duplicates removed")
