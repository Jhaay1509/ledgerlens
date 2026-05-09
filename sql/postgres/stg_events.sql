CREATE TABLE stg_events(
-- Surrogate Key
stg_event_keY       BIGSERIAL PRIMARY KEY,

-- Raw fields as VARCHAR
event_id            VARCHAR(255),
session_id          VARCHAR(255),
order_id            VARCHAR(255),
timestamp           VARCHAR(255),
utm_source          VARCHAR(255),
referrer           VARCHAR(255),
utm_medium          VARCHAR(255),
utm_campaign        VARCHAR(255),

-- Audit
ingested_at         timestamptz NOT NULL DEFAULT NOW()
);