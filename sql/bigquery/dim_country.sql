CREATE TABLE IF NOT EXISTS `my-project-altschool.ledgerlens.dim_country` (
    -- Surrogate key
    country_key     INT64 NOT NULL,

    -- Country details
    country_name    STRING NOT NULL,
    country_code    STRING NOT NULL,  -- ISO 3166-1 alpha-2 e.g. GB, US, EU
    state           STRING,
    region          STRING
);