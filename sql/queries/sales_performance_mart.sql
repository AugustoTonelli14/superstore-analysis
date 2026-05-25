-- sales_performance_mart.sql
-- Monthly and yearly sales and order volume trends.
-- Purpose: Understand revenue trajectory and seasonal patterns.

SELECT
    YEAR("Order Date")                          AS order_year,
    MONTH("Order Date")                         AS order_month,
    STRFTIME("Order Date", '%Y-%m')             AS year_month,
    ROUND(SUM("Sales"), 2)                      AS total_sales,
    ROUND(SUM("Profit"), 2)                     AS total_profit,
    COUNT(DISTINCT "Order ID")                  AS total_orders,
    SUM("Quantity")                             AS total_units,
    ROUND(SUM("Sales") / COUNT(DISTINCT "Order ID"), 2)
                                                AS avg_order_value,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)
                                                AS profit_margin_pct
FROM superstore
GROUP BY order_year, order_month, year_month
ORDER BY order_year, order_month;
