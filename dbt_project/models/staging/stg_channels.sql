with source as (

    select * from {{ source('raw', 'raw_channels') }}

),

ranked as (

       select  *,
        row_number() over (
            partition by channel_id, snapshot_date
            order by loaded_at desc
        ) as rn
    from source

),

latest as (

    select * from ranked where rn = 1

),

countries as (

    select * from {{ ref('country_codes') }}

)

select
    {{ surrogate_key(['l.channel_id', 'l.snapshot_date']) }} as channel_snapshot_key,
    l.channel_id,
    trim(l.title) as channel_name,
    coalesce(c.country_name, 'UNKNOWN') as country_name,
    try_to_timestamp_tz(l.published_at)::timestamp_ntz as channel_created_at,
    case when l.hidden_subscriber_count then null else l.subscriber_count end as subscriber_count,
    coalesce(l.hidden_subscriber_count, false) as is_subscriber_count_hidden,
    l.view_count as total_views,
    l.video_count as total_videos,
    l.snapshot_date
from latest as l
left join countries as c
    on upper(trim(l.country)) = c.country_code
