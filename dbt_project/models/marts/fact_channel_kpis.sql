select
    {{ surrogate_key(['c.channel_id', 'c.snapshot_date']) }} as channel_kpi_key,
    d.channel_key,
    to_number(to_char(c.snapshot_date, 'YYYYMMDD')) as date_key,
    c.snapshot_date,
    c.subscriber_count,
    100.0 * (
        c.subscriber_count - lag(c.subscriber_count) over (
            partition by c.channel_id order by c.snapshot_date
        )
    ) / nullif(lag(c.subscriber_count) over (
            partition by c.channel_id order by c.snapshot_date
        ), 0) as subscriber_growth_pct,
    c.total_views,
    coalesce(r.videos_published_last_30d, 0) as videos_published_last_30d,
    r.avg_engagement_rate_30d,
    r.avg_views_per_video_30d,
    c.total_views / nullif(c.subscriber_count, 0) as views_per_subscriber
from {{ ref('stg_channels') }} as c
inner join {{ ref('dim_channel') }} as d
    on c.channel_id = d.channel_id
left join {{ ref('int_channel_recent_videos') }} as r
    on c.channel_id = r.channel_id
   and c.snapshot_date = r.snapshot_date