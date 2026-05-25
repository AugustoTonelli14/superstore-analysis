-- regional_performance_mart.sql
-- Sales, profit, and margin by region and state.
-- Purpose: Identify geographic strengths, weaknesses, and inefficiencies.

SELECT
    "Region",
    "State",
    ROUND(SUM("Sales"), 2)                      AS total_sales,
    ROUND(SUM("Profit"), 2)                     AS total_profit,
    COUNT(DISTINCT "Order ID")                  AS total_orders,
    ROUND(AVG("Discount"), 4)                   AS avg_discount,
    SUM(CASE WHEN "Profit" < 0 THEN 1 ELSE 0 END)
                                                AS loss_orders,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)
                                                AS profit_margin_pct,
    ROUND(
        SUM(CASE WHEN "Profit" < 0 THEN 1 ELSE 0 END) * 100.0
        / COUNT(DISTINCT "Order ID"), 2
    )                                           AS loss_rate_pct
FROM superstore
GROUP BY "Region", "State"
ORDER BY total_profit DESC;
