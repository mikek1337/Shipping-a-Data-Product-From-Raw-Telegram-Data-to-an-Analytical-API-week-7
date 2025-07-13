{{ config(
    materialized='table'
) }}

SELECT DISTINCT
    -- Extract channel details from the raw data
    channel_id,
    channel_name
FROM {{ ref('stg_telegram_messages') }}
