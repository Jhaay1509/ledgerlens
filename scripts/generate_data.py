import json
import random
import uuid
from datetime import datetime, timedelta, timezone

import pandas as pd
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

#Output paths
RAW_DATA_PATH = "/Users/home/Documents/Altschool_reborn/ledgerlens_afresh/data/raw"

PROVIDERS = {
    "stripe": {
        "amount_format": "float",        # 9.99
        "timestamp_format": "iso",       # "2024-01-15T10:30:00Z"
        "status_map": {
            "success": "succeeded",
            "failure": "failed"
        }
    },
    "paypal": {
        "amount_format": "string",       # "9.99"
        "timestamp_format": "datetime",  # "15/01/2024 10:30"
        "status_map": {
            "COMPLETED": "succeeded",
            "DENIED": "failed"
        }
    },
    "fastpay": {
        "amount_format": "integer",      # 999 (pence)
        "timestamp_format": "epoch",     # 1705312200
        "status_map": {
            "paid": "succeeded",
            "declined": "failed"
        }
    }
}

PRODUCTS = [
    {"product_id": "PROD-001", "product_name": "LedgerLens Basic", "price": 9.99},
    {"product_id": "PROD-002", "product_name": "LedgerLens Pro", "price": 49.99},
    {"product_id": "PROD-003", "product_name": "LedgerLens Enterprise", "price": 199.99},
    {"product_id": "PROD-004", "product_name": "Analytics Add-on", "price": 19.99},
    {"product_id": "PROD-005", "product_name": "API Access", "price": 29.99},
]

refund_reasons = {
    "VAL01": "Not using it enough",
    "VAL02": "Service didn't meet expectations",
    "VAL03": "Achieved goals / Project completed",
    "TEC01": "Unresolved product bugs",
    "TEC02": "Technical difficulties during use",
    "TEC03": "Unfinished or outdated features",
    "BIL01": "Unclear billing or hidden fees",
    "BIL02": "Duplicate charge detected",
    "BIL03": "Payment failure / Involuntary churn",
    "EXT01": "Price sensitivity / Found cheaper option",
    "EXT02": "Switching to a competitor",
    "MISC01": "Accidental purchase / Wrong tier selected"
}

UTM_SOURCES = {
    "google": {
        "source":   "google",
        "referrer": "https://www.google.com",
        "mediums":  ["cpc", "organic"]
    },
    "facebook": {
        "source":   "facebook",
        "referrer": "https://www.facebook.com",
        "mediums":  ["social", "cpc"]
    },
    "newsletter": {
        "source":   "newsletter",
        "referrer": None,
        "mediums":  ["email"]
    },
    "direct": {
        "source":   "direct",
        "referrer": None,
        "mediums":  ["none"]
    }
}

def generate_payments(num_records=1000):
    payments = []
    
    # Generate base payment records
    for _ in range(num_records):
        provider_name = random.choice(list(PROVIDERS.keys()))
        provider = PROVIDERS[provider_name]
        
        # Generate amount based on provider format
        if provider["amount_format"] == "float":
            amount = round(random.uniform(1, 500), 2)
        elif provider["amount_format"] == "string":
            amount = str(round(random.uniform(1, 500), 2))
        elif provider["amount_format"] == "integer":
            amount = random.randint(100, 50000)  # pence
            
        # Generate timestamp based on provider format
        base_date = fake.date_time_between(
            start_date="-1y",
            end_date="now",
            tzinfo=timezone.utc
        )
        
        if provider["timestamp_format"] == "iso":
            timestamp = base_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif provider["timestamp_format"] == "datetime":
            timestamp = base_date.strftime("%d/%m/%Y %H:%M")
        elif provider["timestamp_format"] == "epoch":
            timestamp = int(base_date.timestamp())
            
        # Generate status using provider status map
        raw_status = random.choice(list(provider["status_map"].keys()))
        
        # Generate payment ID
        payment_id = f"{provider_name[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
        
        # Generate order ID (sometimes missing — orphan payments)
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}" \
            if random.random() > 0.1 else None
        
        payment = {
            "payment_id":   payment_id,
            "provider":     provider_name,
            "amount":       amount,
            "currency":     random.choice(["GBP", "USD", "EUR"]),
            "status":       raw_status,
            "order_id":     order_id,
            "timestamp":    timestamp
        }
        
        payments.append(payment)
    
    # Inject duplicates — 5% of records are duplicates
    duplicates = random.sample(payments, int(num_records * 0.05))
    payments.extend(duplicates)
    
    # Shuffle so duplicates aren't all at the end
    random.shuffle(payments)
    
    return payments



def generate_orders(payments, num_of_entries=1000):
    orders = []

    # Pre-assign unique payment references before the loop
    # Sample without replacement ensures no duplicates
    # Deduplicate payments by payment_id before sampling
    unique_payments = list({p["payment_id"]: p for p in payments}.values())

    num_with_reference = int(num_of_entries * 0.9)
    sampled_payments = random.sample(unique_payments, min(num_with_reference, len(unique_payments)))
    
    # Build reference list — 90% real, 10% None — then shuffle
    payment_references = [p["payment_id"] for p in sampled_payments]
    payment_references += [None] * (num_of_entries - len(payment_references))
    random.shuffle(payment_references)  # mix None values randomly

    for i in range(num_of_entries):
        order_id    = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        customer_id = f"CUS-{uuid.uuid4().hex[:8].upper()}"
        payment_reference = payment_references[i]

        # Select a random product from the product catalogue
        product      = random.choice(PRODUCTS)
        product_id   = product["product_id"]
        product_name = product["product_name"]

        currency        = random.choice(["GBP", "USD", "EUR"])
        status          = random.choice(["processing", "shipped", 
                                         "completed", "cancelled"])
        number_of_items = random.randint(1, 5)

        # Amount derived from product price — realistic pricing
        amount_charged = round((number_of_items * product["price"]), 2)

        # Order timestamp — random date within last year
        timestamp = fake.date_time_between(
            start_date="-1y",
            end_date="now",
            tzinfo=timezone.utc
        )

        order = {
            "order_id":          order_id,
            "customer_id":       customer_id,
            "product_id":        product_id,
            "product_name":      product_name,
            "payment_reference": payment_reference,  # links to canonical_payments
            "currency":          currency,
            "status":            status,
            "number_of_items":   number_of_items,
            "amount_charged":    amount_charged,
            "timestamp":         timestamp
        }
        orders.append(order)

    return orders


REFUND_REASONS = [
    "customer_request",
    "duplicate_charge",
    "product_not_received",
    "fraudulent_charge",
    "subscription_cancelled",
    None
]

def parse_timestamp(timestamp):
    if isinstance(timestamp, int):
        # FastPay epoch format
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    elif isinstance(timestamp, str):
        # Try ISO format first (Stripe)
        try:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            # PayPal format
            return datetime.strptime(timestamp, "%d/%m/%Y %H:%M").replace(tzinfo=timezone.utc)
    return timestamp  # already a datetime object

def generate_refunds(payments, number_of_entries=70):
    refunds = []
    
    # Only refund successful payments
    successful_payments = [p for p in payments 
                          if p["status"] in ["success", "COMPLETED", "paid"]]
    
    linked_payments = random.sample(successful_payments, 
                                   min(number_of_entries, len(successful_payments)))
    
    for payment in linked_payments:
        refund_id = f"REF-{uuid.uuid4().hex[:8].upper()}"
        payment_id = payment["payment_id"]

        # Refund arrives late — between 1 and 30 days after payment
        payment_date= parse_timestamp(payment["timestamp"])
        refund_date = payment_date + timedelta(hours=random.randint(24, 720))

        # Sometimes partial refund
        is_full_refund = random.random() > 0.35
        amount= float(payment["amount"])
        refund_amount = amount if is_full_refund \
            else round(amount * random.uniform(0.3, 0.9), 2)

        refund_type = random.choice(["refund", "chargeback"])
        reason = random.choice(REFUND_REASONS)

        refund = {
            "refund_id":     refund_id,
            "payment_id":    payment_id,
            "refund_amount": refund_amount,
            "refund_type":   refund_type,
            "reason":        reason,
            "refund_date":   refund_date
        }
        refunds.append(refund)

    return refunds


def generate_events(orders, number_of_entries=900):
    events = []
    linked_orders = random.sample(orders, number_of_entries)

    for order in linked_orders:
        # Select random source inside loop so each event gets own attribution
        source_key  = random.choice(list(UTM_SOURCES.keys()))
        source_data = UTM_SOURCES[source_key]

        event_id        = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        session_id      = f"SES-{uuid.uuid4().hex[:8].upper()}"
        order_id        = order["order_id"]
        event_timestamp = order["timestamp"] - timedelta(minutes=random.randint(5, 60))

        source   = source_data["source"]
        referrer = source_data["referrer"]
        medium   = random.choice(source_data["mediums"])
        campaign = random.choice([
            "summer_sale_2024",
            "christmas_sale_2024",
            "black_friday_2024",
            None   # some events have no campaign
        ])

        event = {
            "event_id":     event_id,
            "session_id":   session_id,
            "order_id":     order_id,
            "timestamp":    event_timestamp,
            "utm_source":   source,
            "referrer":     referrer,
            "utm_medium":   medium,
            "utm_campaign": campaign
        }
        events.append(event)

    return events


#Save data to a json file
def save_json(data, filename):
    with open(f"{RAW_DATA_PATH}/{filename}.json", "w") as f:
        json.dump(data, f, indent=4, default= str)
    print(f"Saved {len(data)} records to {RAW_DATA_PATH}/{filename}.json")
    
#Save data as csv
def save_csv(data, filename):
    df= pd.DataFrame(data)
    df.to_csv(f"{RAW_DATA_PATH}/{filename}.csv", index= False)
    print(f"Saved {len(data)}records to {RAW_DATA_PATH}/{filename}.csv")
              