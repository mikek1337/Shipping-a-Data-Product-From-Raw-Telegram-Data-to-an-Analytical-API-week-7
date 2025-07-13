{{ config(
    materialized='table'
) }}

SELECT DISTINCT
    message_date::date as date_day,
    EXTRACT(YEAR FROM message_date) as year,
    EXTRACT(MONTH FROM message_date) as month,
    EXTRACT(DAY FROM message_date) as day_of_month,
    EXTRACT(WEEK FROM message_date) as week_of_year,
    EXTRACT(QUARTER FROM message_date) as quarter
FROM {{ ref('stg_telegram_messages') }}
