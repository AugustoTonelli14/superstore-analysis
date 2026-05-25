-- profitability_mart.sql
-- Profit and margin by category, sub-category, and product.
-- Purpose: Identify the most and least profitable areas of the portfolio.

SELECT
    "Category",
    "Sub-Category",
    "Product Name",
    ROUND(SUM("Sales"), 2)                      AS total_sales,
    ROUND(SUM("Profit"), 2)                     AS total_profit,
    SUM("Quantity")                             AS total_units,
    COUNT(DISTINCT "Order ID")                  AS orders,
    SUM(CASE WHEN "Profit" < 0 THEN 1 ELSE 0 END)
                                                AS loss_orders,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)
                                                AS profit_margin_pct,
    ROUND(
        SUM(CASE WHEN "Profit" < 0 THEN 1 ELSE 0 END) * 100.0
        / COUNT(DISTINCT "Order ID"), 2
    )                                           AS loss_rate_pct
FROM superstore
GROUP BY "Category", "Sub-Category", "Product Name"
ORDER BY total_profit DESC;
