CREATE TYPE payment_status AS ENUM (
    'succeeded',
    'failed',
    'pending',
    'reversed'
);

CREATE TYPE match_method AS ENUM (
    'direct_id_match',
    'order_id_match',
    'customer_amount_time',
    'amount_time_only',
    'unmatched'
);

CREATE TABLE canonical_payments (
    -- Surrogate key
    payment_key         BIGSERIAL PRIMARY KEY,

    -- Natural identity
    payment_id          VARCHAR(255) NOT NULL,
    provider            VARCHAR(100) NOT NULL,       -- comma was missing here

    -- Amounts
    amount              NUMERIC(18,4) NOT NULL,
    refund_total        NUMERIC(18,4) NOT NULL DEFAULT 0,
    net_amount          NUMERIC(18,4) NOT NULL,

    -- Currency
    currency            CHAR(3) NOT NULL,

    -- Reconciliation
    order_id            VARCHAR(255),
    match_method        match_method,
    match_confidence    NUMERIC(3,2),

    -- Status
    status              payment_status NOT NULL,
    is_retry            BOOLEAN NOT NULL DEFAULT FALSE,  -- comma was missing here

    -- Timestamps
    paid_at             TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Uniqueness constraint
    CONSTRAINT uq_provider_payment UNIQUE (provider, payment_id)
);