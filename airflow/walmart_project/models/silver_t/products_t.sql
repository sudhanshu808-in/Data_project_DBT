{{
    config (
        materialized = 'incremental',
        unique_key = 'product_id'
    )
}}

select 
*,
current_timestamp() as processed_at
from {{source('walmart_databricks','products')}}


{% if is_incremental() %}
WHERE updated_timestamp > (select COALESCE(max(updated_timestamp),'1994-01-01' )from {{this}})
{% endif %}