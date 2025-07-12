{{ config(
    materialized='view'
) }}

SELECT
    -- Use jsonb_array_elements to unnest the array
    (message_data ->> 'id')::bigint as message_id,
    (message_data ->> 'channel_id') as channel_id,
    message_data ->> 'message' as message_text,
    (message_data ->> 'date')::timestamp with time zone as message_date,
    (message_data ->> 'sender_id')::bigint as sender_id,
    (message_data ->> 'views')::int as views,
    (message_data ->> 'forwards')::int as forwards,
    (message_data ->> 'replies')::int as replies,
    (message_data ->> 'media_present')::boolean as media_present,
    message_data ->> 'media_type' as media_type,
    message_data ->> 'media_path' as media_path,
    message_data ->> 'channel_name' as channel_name,
    t.scraped_at -- Keep the original scraped_at from the raw table
FROM
    {{ source('telegram_source', 'telegram_messages') }} as t,
    jsonb_array_elements(t.raw_data) as message_data -- Unnest the JSON array
