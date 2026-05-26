{{
    config(
        materialized='view'
    )
}}

/*
    Staging model: clean and standardize raw Superstore data.
    Parses dates, trims strings, and adds derived time dimensions.
*/

with source as (
    select * from {{ source('raw', 'raw_superstore') }}
),

cleaned as (
    select
        "Row ID"                                        as row_id,
        "Order ID"                                      as order_id,
        cast("Order Date" as date)                      as order_date,
        cast("Ship Date" as date)                       as ship_date,
        trim("Ship Mode")                               as ship_mode,
        "Customer ID"                                   as customer_id,
        trim("Customer Name")                           as customer_name,
        trim("Segment")                                 as segment,
        trim("Country")                                 as country,
        trim("City")                                    as city,
        trim("State")                                   as state,
        cast("Postal Code" as varchar)                  as postal_code,
        trim("Region")                                  as region,
        "Product ID"                                    as product_id,
        trim("Category")                                as category,
        trim("Sub-Category")                            as sub_category,
        trim("Product Name")                            as product_name,
        round(cast("Sales" as double), 2)               as sales,
        cast("Quantity" as integer)                      as quantity,
        round(cast("Discount" as double), 2)            as discount,
        round(cast("Profit" as double), 2)              as profit,

        -- time dimensions
        year(cast("Order Date" as date))                as order_year,
        month(cast("Order Date" as date))               as order_month,
        quarter(cast("Order Date" as date))             as order_quarter,
        strftime(cast("Order Date" as date), '%Y-%m')   as year_month,

        -- shipping
        datediff('day',
            cast("Order Date" as date),
            cast("Ship Date" as date)
        )                                               as shipping_lead_time,

        -- profitability metrics
        case
            when "Sales" = 0 then 0.0
            else round(("Profit" / "Sales") * 100, 2)
        end                                             as profit_margin_pct,

        case
            when "Profit" < 0 then 1
            else 0
        end                                             as loss_flag,

        case
            when "Discount" = 0   then 'No Discount'
            when "Discount" < 0.2 then 'Low (1-19%)'
            when "Discount" < 0.3 then 'Medium (20-29%)'
            else 'High (30%+)'
        end                                             as discount_band,

        case
            when "Discount" >= 0.3 then 1
            else 0
        end                                             as high_discount_flag,

        case
            when "Quantity" = 0 then 0.0
            else round("Sales" / "Quantity", 2)
        end                                             as revenue_per_unit,

        case
            when "Quantity" = 0 then 0.0
            else round("Profit" / "Quantity", 2)
        end                                             as profit_per_unit

    from source
)

select * from cleaned
