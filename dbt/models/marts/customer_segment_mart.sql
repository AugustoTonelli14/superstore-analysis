{{
    config(
        materialized='table'
    )
}}

/*
    Customer Segment Mart
    Segment-level KPIs: revenue, profit, customer count, and margins.
*/

select
    segment,
    round(sum(sales), 2)                                    as total_sales,
    round(sum(profit), 2)                                   as total_profit,
    count(distinct customer_id)                             as total_customers,
    count(distinct order_id)                                as total_orders,
    sum(quantity)                                            as total_units,
    round(sum(sales) / nullif(count(distinct order_id), 0), 2) as avg_order_value,
    round(sum(profit) / nullif(sum(sales), 0) * 100, 2)    as profit_margin_pct,
    round(sum(loss_flag) * 100.0 / nullif(count(*), 0), 2) as loss_rate_pct

from {{ ref('stg_superstore') }}
group by segment
order by total_sales desc
