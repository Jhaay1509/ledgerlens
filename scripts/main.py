from generate_data import generate_payments, generate_orders, generate_refunds, generate_events, save_csv, save_json

def main():
    payments = generate_payments()
    save_csv(payments, "raw_payments")      # ← raw_ prefix

    orders = generate_orders(payments)
    save_json(orders, "raw_orders")         # ← raw_ prefix

    refunds = generate_refunds(payments=payments)
    save_csv(refunds, "raw_refunds")        # ← raw_ prefix

    events = generate_events(orders)
    save_json(events, "raw_events")         # ← raw_ prefix

if __name__ == "__main__":
    main()