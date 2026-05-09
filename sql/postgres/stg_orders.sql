CREATE TABLE stg_orders (
-- Surrogate Key
stg_order_key       BIGSERIAL PRIMARY KEY, 

-- Raw fields as VARCHAR
order_id            VARCHAR(255),
customer_id         VARCHAR(255),
product_id          VARCHAR(255),
product_name        VARCHAR(255),
payment_reference   VARCHAR(255),
currency            VARCHAR(10),
status              VARCHAR(50),
number_of_items     VARCHAR(10),
amount_charged      VARCHAR(10),
timestamp           VARCHAR(255),

-- Audit
ingested_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);