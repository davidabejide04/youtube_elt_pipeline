with ranked as (

    select
        *,
        row_number() over (partition by video_id order by snapshot_date desc) as rn
    from {{ ref('stg_videos') }}

),

latest as (

    select * from ranked where rn = 1

)

select
    row_number() over (order by l.video_id) as video_key,
    l.video_id,
    c.channel_key,
    l.video_title,
    l.published_at,
    l.duration_seconds,
    case
        when l.duration_seconds < 60 then 'Under 1 min'
        when l.duration_seconds < 300 then '1 to 5 min'
        when l.duration_seconds < 600 then '5 to 10 min'
        when l.duration_seconds < 1200 then '10 to 20 min'
        else 'Over 20 min'
    end as duration_bucket,
    case when l.is_short then 'Short' else 'Long-form' end as format_type,
    l.category_name
from latest as l
inner join {{ ref('dim_channel') }} as c
    on l.channel_id = c.channel_id