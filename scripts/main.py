from generate_data import generate_payments, generate_orders, generate_refunds, generate_events, save_csv, save_json

def main():
    payments= generate_payments()
    save_csv(payments, "payments")

    orders= generate_orders()
    save_json(orders, "orders")

    refunds = generate_refunds(payments= payments)
    save_csv(refunds, "refunds")

    events= generate_events(orders)
    save_json(events, "events")

if __name__ == "__main__":
    main()