CREATE TABLE stg_refunds(
-- Surrogate Key
stg_refund_key      BIGSERIAL PRIMARY KEY,

-- Raw fields as VARCHAR
refund_id           VARCHAR(255),
payment_id          VARCHAR(255),
refund_amount       VARCHAR(50),
refund_type         VARCHAR(50),
reason              VARCHAR(255),
refund_date         VARCHAR(255),

--Audit
ingested_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);