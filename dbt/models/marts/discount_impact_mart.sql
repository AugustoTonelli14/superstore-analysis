{{
    config(
        materialized='table'
    )
}}

/*
    Discount Impact Mart
    Measures how discount levels affect profitability across categories.
*/

select
    discount_band,
    category,
    round(sum(sales), 2)                                        as total_sales,
    round(sum(profit), 2)                                       as total_profit,
    count(distinct order_id)                                    as total_orders,
    sum(quantity)                                                as total_units,
    round(avg(discount) * 100, 2)                               as avg_discount_pct,
    round(sum(profit) / nullif(sum(sales), 0) * 100, 2)        as profit_margin_pct,
    round(sum(loss_flag) * 100.0 / nullif(count(*), 0), 2)     as loss_rate_pct,
    sum(high_discount_flag)                                     as high_discount_orders

from {{ ref('stg_superstore') }}
group by discount_band, category
order by discount_band, category
