with ranked as (

    select
        *,
        row_number() over (partition by channel_id order by snapshot_date desc) as rn
    from {{ ref('stg_channels') }}

),

latest as (

    select * from ranked where rn = 1

)

select
    row_number() over (order by channel_id) as channel_key,
    channel_id,
    channel_name,
    country_name,
    channel_created_at,
    round(datediff(day, channel_created_at, current_date()) / 365.25, 1) as channel_age_years,
    case
        when is_subscriber_count_hidden then 'Hidden'
        when subscriber_count < 10000 then 'Micro'
        when subscriber_count < 100000 then 'Small'
        when subscriber_count < 1000000 then 'Medium'
        when subscriber_count < 10000000 then 'Large'
        else 'Mega'
    end as size_tier
from latest