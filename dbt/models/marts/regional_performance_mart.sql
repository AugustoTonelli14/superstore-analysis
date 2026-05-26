{{
    config(
        materialized='table'
    )
}}

/*
    Regional Performance Mart
    Geographic breakdown of sales and profitability by Region and State.
*/

select
    region,
    state,
    round(sum(sales), 2)                                    as total_sales,
    round(sum(profit), 2)                                   as total_profit,
    count(distinct order_id)                                as total_orders,
    count(distinct customer_id)                             as total_customers,
    round(sum(profit) / nullif(sum(sales), 0) * 100, 2)    as profit_margin_pct,
    round(sum(loss_flag) * 100.0 / nullif(count(*), 0), 2) as loss_rate_pct

from {{ ref('stg_superstore') }}
group by region, state
order by region, total_profit desc
