{{ config(
    materialized='table'
) }}

SELECT
    stg.message_id,
    stg.message_text,
    stg.sender_id,
    stg.views,
    stg.forwards,
    stg.replies,
    stg.media_present,
    stg.media_type,
    stg.media_path,
    LENGTH(stg.message_text) as message_length,
    CASE WHEN stg.media_type = 'photo' THEN TRUE ELSE FALSE END as has_image,
    -- Foreign Keys
    stg.channel_id,
    stg.message_date::date as date_id
FROM {{ ref('stg_telegram_messages') }} as stg