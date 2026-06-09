CREATE TABLE IF NOT EXISTS `my-project-altschool.ledgerlens.dim_product` (
    -- Surrogate key (unique per version)
    product_key         INT64 NOT NULL,

    -- Natural key (repeats across versions)
    product_id          STRING NOT NULL,

    -- Product details
    product_name        STRING NOT NULL,
    product_category    STRING NOT NULL,
    price               NUMERIC NOT NULL,
    currency            STRING NOT NULL,

    -- SCD Type 2 tracking
    valid_from          DATE NOT NULL,
    valid_to            DATE,
    is_current          BOOLEAN NOT NULL
);