with dates as (

    select
        dateadd(day, row_number() over (order by seq4()) - 1, '2020-01-01'::date) as full_date
    from table(generator(rowcount => 3653))

)

select
    to_number(to_char(full_date, 'YYYYMMDD')) as date_key,
    full_date,
    dayname(full_date) as day_of_week,
    weekiso(full_date) as week_of_year,
    monthname(full_date) as month_name,
    quarter(full_date) as quarter,
    year(full_date) as year,
    dayofweekiso(full_date) in (6, 7) as is_weekend
from dates