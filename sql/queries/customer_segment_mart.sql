-- customer_segment_mart.sql
-- Performance by customer segment (Consumer, Corporate, Home Office).
-- Purpose: Determine which segments drive value and which represent risk.

SELECT
    "Segment",
    ROUND(SUM("Sales"), 2)                      AS total_sales,
    ROUND(SUM("Profit"), 2)                     AS total_profit,
    COUNT(DISTINCT "Customer ID")               AS total_customers,
    COUNT(DISTINCT "Order ID")                  AS total_orders,
    ROUND(AVG("Discount"), 4)                   AS avg_discount,
    SUM(CASE WHEN "Profit" < 0 THEN 1 ELSE 0 END)
                                                AS loss_orders,
    ROUND(SUM("Profit") / SUM("Sales") * 100, 2)
                                                AS profit_margin_pct,
    ROUND(SUM("Sales") / COUNT(DISTINCT "Customer ID"), 2)
                                                AS avg_revenue_per_customer,
    ROUND(
        SUM(CASE WHEN "Profit" < 0 THEN 1 ELSE 0 END) * 100.0
        / COUNT(DISTINCT "Order ID"), 2
    )                                           AS loss_rate_pct
FROM superstore
GROUP BY "Segment"
ORDER BY total_profit DESC;
