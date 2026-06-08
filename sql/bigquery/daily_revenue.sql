CREATE TABLE IF NOT EXISTS `my-project-altschool.ledgerlens.daily_revenue` (
    -- Surrogate key
    daily_revenue_key   INT64 NOT NULL,

    -- Dimension foreign keys
    date_key            DATE NOT NULL,
    country_key         INT64 NOT NULL,
    product_key         INT64 NOT NULL,
    attribution_key     INT64,            -- nullable — attribution not always available

    -- Measures
    gross_revenue       NUMERIC NOT NULL,
    refunds             NUMERIC NOT NULL,
    net_revenue         NUMERIC NOT NULL,
    order_count         INT64 NOT NULL,
    payment_count       INT64 NOT NULL
);