-- =====================================================================
-- FreshCart ELT Pipeline Edits (Part B)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Edit (a): SQL_10_ORDERS_CLEAN
-- Add validation reason 'unsupported_currency' for any currency != INR/USD
-- ---------------------------------------------------------------------
/*
DIFF REVIEW:
--- a/SQL_10_ORDERS_CLEAN
+++ b/SQL_10_ORDERS_CLEAN
@@ -10,6 +10,7 @@
     ARRAY_CONSTRUCT_COMPACT(
         IFF(order_id IS NULL, 'missing_order_id', NULL),
         IFF(amount IS NULL OR amount <= 0, 'invalid_amount', NULL),
+        IFF(currency NOT IN ('INR', 'USD'), 'unsupported_currency', NULL)
     ) AS reasons
*/

-- Full updated snippet for SQL_10_ORDERS_CLEAN:
CREATE OR REPLACE VIEW silver.orders_checked AS
SELECT
    raw:order_id::STRING AS order_id,
    raw:customer_id::STRING AS customer_id,
    raw:order_date::DATE AS order_date,
    raw:amount::NUMBER(10, 2) AS amount,
    raw:currency::STRING AS currency,
    raw:updated_at::TIMESTAMP_NTZ AS updated_at,
    ARRAY_CONSTRUCT_COMPACT(
        IFF(raw:order_id IS NULL, 'missing_order_id', NULL),
        IFF(raw:amount IS NULL OR raw:amount <= 0, 'invalid_amount', NULL),
        IFF(raw:currency NOT IN ('INR', 'USD'), 'unsupported_currency', NULL)
    ) AS reasons
FROM bronze.orders_raw;


-- ---------------------------------------------------------------------
-- Edit (b): Sixth quality check in quality_checks()
-- Must equal 0: gold orders with loyalty_points < 0
-- ---------------------------------------------------------------------
/*
DIFF REVIEW:
--- a/quality_checks()
+++ b/quality_checks()
@@ -20,6 +20,10 @@
+    SELECT 'gold_negative_loyalty_points' AS check_name,
+           COUNT(*) AS problem_count
+    FROM gold.orders
+    WHERE loyalty_points < 0
*/

-- Example addition to quality_checks procedure/query:
SELECT 'gold_negative_loyalty_points' AS check_name,
       COUNT(*) AS problem_count
FROM gold.orders
WHERE loyalty_points < 0;


-- ---------------------------------------------------------------------
-- Edit (c): Mock order to make check fail, plus removal statement
-- ---------------------------------------------------------------------

-- 1. Insert failing mock record (negative loyalty points)
INSERT INTO gold.orders (
    order_id,
    customer_id,
    order_date,
    amount,
    currency,
    amount_inr,
    loyalty_points,
    published_at
)
VALUES (
    'ORD-MOCK-FAIL-01',
    'CUST-02',
    CURRENT_DATE(),
    1500.00,
    'INR',
    1500.00,
    -25,
    CURRENT_TIMESTAMP()
);

-- 2. Removal statement to clean up mock order
DELETE FROM gold.orders
WHERE order_id = 'ORD-MOCK-FAIL-01';


-- ---------------------------------------------------------------------
-- Edit (d): New MOCK_CRM_TIER_EVENTS row for Arjun
-- CUST-02, arjun.k@yahoo.in, Gold, effective_from = 2026-08-15
-- ---------------------------------------------------------------------
INSERT INTO ref.mock_crm_tier_events (
    customer_id,
    customer_email,
    tier,
    effective_from
)
VALUES (
    'CUST-02',
    'arjun.k@yahoo.in',
    'Gold',
    '2026-08-15'::DATE
);
