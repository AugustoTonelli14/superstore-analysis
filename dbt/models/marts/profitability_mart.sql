{{
    config(
        materialized='table'
    )
}}

/*
    Profitability Mart
    Product-level profitability analysis by Category and Sub-Category.
*/

select
    category,
    sub_category,
    product_name,
    round(sum(sales), 2)                                    as total_sales,
    round(sum(profit), 2)                                   as total_profit,
    sum(quantity)                                            as total_units,
    count(distinct order_id)                                as total_orders,
    round(sum(profit) / nullif(sum(sales), 0) * 100, 2)    as profit_margin_pct,
    round(sum(loss_flag) * 100.0 / nullif(count(*), 0), 2) as loss_rate_pct

from {{ ref('stg_superstore') }}
group by category, sub_category, product_name
order by total_profit desc
