select *
from {{ ref('fact_video_performance_daily') }}
where view_count < 0