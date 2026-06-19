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