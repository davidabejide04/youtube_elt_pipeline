{# Builds a stable hash key from a list of columns. #}
{% macro surrogate_key(columns) -%}
md5(concat_ws('|'
    {%- for c in columns -%}
    , coalesce(cast({{ c }} as varchar), '')
    {%- endfor -%}
))
{%- endmacro %}