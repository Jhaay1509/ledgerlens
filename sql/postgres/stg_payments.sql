CREATE TABLE stg_payments (
    -- Surrogate key
    stg_payment_key     BIGSERIAL PRIMARY KEY,

    -- Raw fields as VARCHAR
    payment_id          VARCHAR(255),
    provider            VARCHAR(255),
    amount              VARCHAR(50),
    currency            VARCHAR(10),
    status              VARCHAR(50),
    order_id            VARCHAR(255),
    timestamp           VARCHAR(255),

    -- Audit
    ingested_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);