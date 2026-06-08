-- CREATE TYPE primary_source AS ENUM (
--     'organic',
--     'paid',
--     'referral',
--     'direct',
--     'email'
-- );

-- CREATE TABLE dim_attribution (
--     -- Surrogate key
--     attribution_key     BIGSERIAL PRIMARY KEY,

--     -- Marketing context
--     primary_source      primary_source NOT NULL,
--     media_source        VARCHAR(100),
--     campaign_name       VARCHAR(255),
--     referral_code       VARCHAR(100),

--     -- UTM parameters
--     utm_source          VARCHAR(100),
--     utm_medium          VARCHAR(100),
--     utm_campaign        VARCHAR(255)
-- );

CREATE TABLE IF NOT EXISTS `my-project-altschool.ledgerlens.dim_attribution`(
    -- Surrogate Key
    attribution_key INT64      NOT NULL,

    -- Marketing context
    primary_source      STRING NOT NULL,
    media_source        STRING,
    campaign_name       STRING,
    referral_code       STRING,

    -- UTM parameters
    utm_source          STRING,
    utm_medium          STRING,
    utm_campaign        STRING
);