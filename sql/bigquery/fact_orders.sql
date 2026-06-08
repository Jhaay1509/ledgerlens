CREATE TABLE IF NOT EXISTS `my-project-altschool.ledgerlens.fact_orders`(
    -- Traceabilty
    order_key       INT64 NOT NULL,
    order_id        STRING NOT NULL,
    customer_id     STRING NOT NULL,

    -- Foreign keys to dimensions
    date_key        DATE NOT NULL,
    product_key     INT64 NOT NULL,
    country_key     INT64 NOT NULL,
    attribution_key INT64,          -- nullabe - not all orders have attribution

    -- Measures
    amount_charged  NUMERIC NOT NULL,
    number_of_items INT64   NOT NULL,
    total_paid      NUMERIC NOT NULL,  -- 0 for unmatched orders

    -- Analytical Flags
    order_status   STRING NOT NULL,
    is_paid        BOOLEAN NOT NULL
);