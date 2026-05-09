CREATE TYPE refund_type AS ENUM (
    'chargeback',
    'refund'
);

CREATE TABLE refund_events (
    -- Surrogate key
    refund_key          BIGSERIAL PRIMARY KEY,

    -- Natural identity
    refund_id           VARCHAR(255) NOT NULL UNIQUE,

    -- Link to payment
    payment_key         BIGINT NOT NULL REFERENCES canonical_payments(payment_key),

    -- Refund details
    refund_amount       NUMERIC(18,4) NOT NULL,
    refund_type         refund_type NOT NULL,
    refund_reason       VARCHAR(255),

    -- Timing
    refunded_at         TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

