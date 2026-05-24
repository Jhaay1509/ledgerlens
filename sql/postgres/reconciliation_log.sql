CREATE TYPE reconciliation_status AS ENUM (
    'matched',
    'unmatched',
    'manual_review'
);

CREATE TABLE reconciliation_log (
    -- Surrogate key
    reconciliation_key      BIGSERIAL PRIMARY KEY,

    -- Natural identity
    reconciliation_id       VARCHAR(255) NOT NULL UNIQUE,

    -- Links to payment and order
    payment_key             BIGINT 
                            REFERENCES canonical_payments(payment_key),
    order_key               BIGINT 
                            REFERENCES canonical_orders(order_key),

    -- Reconciliation details
    match_method            match_method NOT NULL,
    match_confidence        NUMERIC(3,2) NOT NULL,
    reconciliation_status   reconciliation_status NOT NULL,
    failure_reason          VARCHAR(255),

    -- Timing
    reconciled_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);