{{ config(
    materialized='view'
) }}

SELECT  
    raw_data ->> 'id' as message_id,
    raw_data ->> 'channel_id' as channel_id,
    raw_data ->> 'message' as message_text,
    (raw_data ->> 'date')::timestamp with time zone as message_date,
    raw_data ->> 'sender_id' as sender_id,
    (raw_data ->> 'views')::int as views,
    (raw_data ->> 'forwards')::int as forwards,
    (raw_data ->> 'replies')::int as replies,
    (raw_data ->> 'media_present')::boolean as media_present,
    raw_data ->> 'media_type' as media_type,
    raw_data ->> 'media_path' as media_path,
    scraped_at
FROM {{ source('telegram_source', 'telegram_messages') }}