-- discount_impact_mart.sql
-- Profitability breakdown by discount band and category.
-- Purpose: Quantify the financial damage caused by aggressive discounting.

SELECT
    CASE
        WHEN "Discount" = 0            THEN 'No Discount'
        WHEN "Discount" < 0.20         THEN 'Low (1-19%)'
        WHEN "Discount" < 0.30         THEN 'Medium (20-29%)'
        ELSE                                'High (30%+)'
    END                                         AS discount_band,
    "Category",
    ROUND(SUM("Sales"), 2)                      AS total_sales,
    ROUND(SUM("Profit"), 2)                     AS total_profit,
    COUNT(DISTINCT "Order ID")                  AS orders,
    SUM(CASE WHEN "Profit" < 0 THEN 1 ELSE 0 END)
                                                AS loss_orders,
    ROUND(AVG("Discount"), 4)                   AS avg_discount,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)
                                                AS profit_margin_pct,
    ROUND(
        SUM(CASE WHEN "Profit" < 0 THEN 1 ELSE 0 END) * 100.0
        / COUNT(DISTINCT "Order ID"), 2
    )                                           AS loss_rate_pct
FROM superstore
GROUP BY discount_band, "Category"
ORDER BY discount_band, "Category";
