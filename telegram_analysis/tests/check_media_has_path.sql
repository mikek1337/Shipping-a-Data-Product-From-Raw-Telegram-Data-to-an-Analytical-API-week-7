SELECT
    message_id
FROM {{ ref('fct_messages') }}
WHERE media_present = FALSE AND media_path IS NOT NULL