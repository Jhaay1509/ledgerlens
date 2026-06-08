CREATE TABLE IF NOT EXISTS `my-project-altschool.ledgerlens.dim_date`(
    date_key DATE NOT NULL,
    year INT64 NOT NULL,
    quarter INT64 NOT NULL,
    month_num INT64 NOT NULL,
    month_name STRING NOT NULL,
    week_num INT64 NOT NULL,
    day_of_month INT64 NOT NULL,
    day_of_week_num INT64 NOT NULL,
    day_of_week_name STRING NOT NULL,
    is_weekend BOOLEAN NOT NULL
);