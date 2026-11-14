{# Converts an ISO 8601 duration such as PT1H2M30S into seconds. #}
{% macro iso_duration_to_seconds(col) -%}
(
    coalesce(regexp_substr({{ col }}, '(\\d+)D', 1, 1, 'e', 1)::int, 0) * 86400
  + coalesce(regexp_substr({{ col }}, '(\\d+)H', 1, 1, 'e', 1)::int, 0) * 3600
  + coalesce(regexp_substr({{ col }}, '(\\d+)M', 1, 1, 'e', 1)::int, 0) * 60
  + coalesce(regexp_substr({{ col }}, '(\\d+)S', 1, 1, 'e', 1)::int, 0)
)
{%- endmacro %}