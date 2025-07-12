SELECT
    message_id
FROM {{ ref('fct_messages') }}
WHERE media_present = TRUE AND media_path IS NULL