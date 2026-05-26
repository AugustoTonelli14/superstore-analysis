{{
    config(
        materialized='table'
    )
}}

/*
    Sales Performance Mart
    Monthly aggregation of revenue, profit, orders, and units sold.
*/

select
    order_year,
    order_month,
    year_month,
    round(sum(sales), 2)                                        as total_sales,
    round(sum(profit), 2)                                       as total_profit,
    count(distinct order_id)                                    as total_orders,
    sum(quantity)                                                as total_units,
    round(sum(sales) / nullif(count(distinct order_id), 0), 2)  as avg_order_value,
    round(sum(profit) / nullif(sum(sales), 0) * 100, 2)        as profit_margin_pct

from {{ ref('stg_superstore') }}
group by order_year, order_month, year_month
order by order_year, order_month
