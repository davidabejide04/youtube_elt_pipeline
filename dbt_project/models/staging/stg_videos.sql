with source as (

    select * from {{ source('raw', 'raw_videos') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by video_id, snapshot_date
            order by loaded_at desc
        ) as rn
    from source

),

latest as (

    select * from ranked where rn = 1

),

categories as (

    select * from {{ ref('video_categories') }}

),

parsed as (

    select
        l.*,
        {{ iso_duration_to_seconds('l.duration') }} as duration_seconds
    from latest as l

)

select
    {{ surrogate_key(['p.video_id', 'p.snapshot_date']) }} as video_snapshot_key,
    p.video_id,
    p.channel_id,
    trim(p.title) as video_title,
    -- keep letters, numbers and common punctuation, then collapse repeated spaces
    trim(regexp_replace(
        regexp_replace(p.description, '[^a-zA-Z0-9 .,!?@#:;()/-]', ' '),
        '\\s+', ' '
    )) as video_description_clean,
    try_to_timestamp_tz(p.published_at)::timestamp_ntz as published_at,
    p.duration_seconds,
    p.duration_seconds <= {{ var('short_max_seconds') }} as is_short,
    coalesce(c.category_name, 'Other') as category_name,
    p.tags as tags_json,
    p.view_count,
    p.like_count,
    p.comment_count,
    p.snapshot_date
from parsed as p
left join categories as c
    on p.category_id = c.category_id