{{ config(severity='warn') }}

select *
from {{ ref('fact_video_performance_daily') }}
where engagement_rate < 0 or engagement_rate > 1