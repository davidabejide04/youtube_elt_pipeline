select channel_id,
    snapshot_date,
    count(*) as videos_published_last_30d,
    avg(view_count) as avg_views_per_video_30d,
    avg(
        (coalesce(like_count, 0) + coalesce(comment_count, 0)) / nullif(view_count, 0)
    ) as avg_engagement_rate_30d
from {{ ref('stg_videos') }}
where published_at >= dateadd(day, -30, snapshot_date)
  and published_at <= dateadd(day, 1, snapshot_date)
group by channel_id, snapshot_date
