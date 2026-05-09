CREATE TYPE order_status AS ENUM (
    'processing',
    'shipped',
    'completed',
    'cancelled'
);

CREATE TABLE canonical_orders (
    -- Surrogate key
    order_key               BIGSERIAL PRIMARY KEY,

    -- Natural identity
    order_id                VARCHAR(255) NOT NULL UNIQUE,
    customer_id             VARCHAR(100) NOT NULL,
    product_id              VARCHAR(255) NOT NULL,

    -- Order details
    number_of_items         INT NOT NULL DEFAULT 1,
    amount_charged          NUMERIC(18,4) NOT NULL,
    currency                CHAR(3) NOT NULL,
    status                  order_status NOT NULL,

    -- Reconciliation outcome
    successful_payment_key  BIGINT REFERENCES canonical_payments(payment_key),
    is_paid                 BOOLEAN NOT NULL DEFAULT FALSE,
    total_paid              NUMERIC(18,4),

    -- Timing
    order_date              TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);












