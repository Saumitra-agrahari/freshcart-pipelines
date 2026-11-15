-- =====================================================================
-- FreshCart ELT Pipeline Edits (Part B - Verified against Course Notebook)
-- Source of Truth: material/07-10-2026/freshcart_elt_commented.ipynb
-- =====================================================================

-- ---------------------------------------------------------------------
-- Edit (a): SQL_10_ORDERS_CLEAN
-- Add validation reason 'unsupported_currency' inside ARRAY_CONSTRUCT_COMPACT(...)
-- Location: Cell 17 in freshcart_elt_commented.ipynb
-- ---------------------------------------------------------------------
/*
--- a/SQL_10_ORDERS_CLEAN (Cell 17)
+++ b/SQL_10_ORDERS_CLEAN (Cell 17)
@@ -40,6 +40,7 @@
     IFF(pincode IS NULL OR NOT REGEXP_LIKE(pincode, '^[1-9][0-9]{5}$'), 'bad_pincode', NULL),
     IFF(order_date IS NULL, 'unparseable_date', NULL),
     IFF(updated_at IS NULL, 'unparseable_updated_at', NULL),
-    IFF(amount <= 0, 'non_positive_amount', NULL)          -- NULL amount is allowed (flagged below)
+    IFF(amount <= 0, 'non_positive_amount', NULL),          -- NULL amount is allowed (flagged below)
+    IFF(currency NOT IN ('INR', 'USD'), 'unsupported_currency', NULL)
   ) AS reasons
 FROM typed;
*/


-- ---------------------------------------------------------------------
-- Edit (b): Sixth quality check in quality_checks() checks dictionary
-- Must equal 0: gold orders with loyalty_points < 0 in gold.fct_orders
-- Location: Cell 24 in freshcart_elt_commented.ipynb
-- ---------------------------------------------------------------------
/*
--- a/quality_checks() (Cell 24)
+++ b/quality_checks() (Cell 24)
@@ -10,6 +10,8 @@
         "orders with an amount but no FX rate":
             "SELECT COUNT_IF(amount IS NOT NULL AND fx_rate IS NULL) FROM silver.orders_enriched",
         "orders with no city":
             "SELECT COUNT_IF(city IS NULL) FROM silver.orders_enriched",
+        "gold orders with loyalty_points < 0":
+            "SELECT COUNT_IF(loyalty_points < 0) FROM gold.fct_orders",
     }
*/


-- ---------------------------------------------------------------------
-- Edit (c): Mock order to make quality check fail, with removal step
-- Entered the same way as other notebook mock data (MOCK_WEB_ORDERS in Cell 6)
-- and via direct query() to gold.fct_orders
-- ---------------------------------------------------------------------

-- Option 1: Direct SQL test on gold.fct_orders (using notebook query() helper)
/*
query("""
INSERT INTO gold.fct_orders (
    order_id, order_date, cust_id, email, tier, multiplier,
    amount, currency, fx_rate, amount_inr, loyalty_points,
    is_high_value, city, state, region, updated_at, row_hash, published_at
)
VALUES (
    'ORD-MOCK-FAIL', '2026-09-01', 'CUST-02', 'arjun.k@yahoo.in', 'Gold', 2,
    1250.00, 'INR', 1.0, 1250.00, -25, FALSE, 'Bengaluru', 'Karnataka', 'South',
    '2026-09-01 10:00:00', 99999, CURRENT_TIMESTAMP()
);
""")

-- Removal statement:
query("DELETE FROM gold.fct_orders WHERE order_id = 'ORD-MOCK-FAIL'")
*/


-- ---------------------------------------------------------------------
-- Edit (d): New CRM tier event for Arjun added to MOCK_CRM_TIER_EVENTS
-- Location: Cell 6 in freshcart_elt_commented.ipynb
-- ---------------------------------------------------------------------
/*
--- a/MOCK_CRM_TIER_EVENTS (Cell 6)
+++ b/MOCK_CRM_TIER_EVENTS (Cell 6)
@@ -35,6 +35,7 @@
     {"cust_id": "CUST-01", "email": "priya.r@gmail.com", "tier": "Gold", "effective_from": "2026-09-03"},
     {"cust_id": "CUST-02", "email": "arjun.k@yahoo.in", "tier": "Silver", "effective_from": "2024-01-15"},
+    {"cust_id": "CUST-02", "email": "arjun.k@yahoo.in", "tier": "Gold", "effective_from": "2026-08-15"},
     {"cust_id": "CUST-03", "email": "meera@outlook.com", "tier": "Platinum", "effective_from": "2022-11-01"},
 ]
*/
