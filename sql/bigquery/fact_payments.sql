CREATE TABLE IF NOT EXISTS `my-project-altschool.ledgerlens.fact_payments` (
    -- Traceability
    payment_key     INT64 NOT NULL,
    payment_id      STRING NOT NULL,
    provider        STRING NOT NULL,

    -- Foreign keys to dimensions
    date_key        DATE NOT NULL,
    product_key     INT64 NOT NULL,
    country_key     INT64 NOT NULL,
    attribution_key INT64,          -- nullable — not all payments have attribution

    -- Measures
    amount          NUMERIC NOT NULL,
    net_amount      NUMERIC NOT NULL,
    refund_total    NUMERIC NOT NULL,
    currency        STRING NOT NULL,  -- EUR, USD, GBP

    -- Analytical flags
    payment_status  STRING NOT NULL,
    is_retry        BOOLEAN NOT NULL
);