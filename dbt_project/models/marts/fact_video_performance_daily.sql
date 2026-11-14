select
    {{ surrogate_key(['v.video_id', 'v.snapshot_date']) }} as video_performance_key,
    d.video_key,
    d.channel_key,
    to_number(to_char(v.snapshot_date, 'YYYYMMDD')) as date_key,
    v.snapshot_date,
    v.view_count,
    v.like_count,
    v.comment_count,
    (coalesce(v.like_count, 0) + coalesce(v.comment_count, 0)) / nullif(v.view_count, 0) as engagement_rate,
    v.view_count - lag(v.view_count) over (
        partition by v.video_id order by v.snapshot_date
    ) as views_gained_since_prior_snapshot,
    datediff(day, v.published_at, v.snapshot_date) as days_since_publish,
    v.view_count / nullif(datediff(day, v.published_at, v.snapshot_date), 0) as views_per_day
from {{ ref('stg_videos') }} as v
inner join {{ ref('dim_video') }} as d
    on v.video_id = d.video_id