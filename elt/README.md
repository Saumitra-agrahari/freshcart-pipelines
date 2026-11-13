# FreshCart ELT Pipeline (Snowflake)

This directory contains the SQL transformations and quality check edits for Part B.

## Files
- `snowflake_edits.sql`: SQL diffs and statements for:
  - Validation rule `unsupported_currency` in `SQL_10_ORDERS_CLEAN`
  - Sixth quality check (checking negative loyalty points in gold)
  - Failing mock order injection & cleanup statement
  - New CRM tier event for Arjun (CUST-02)

## Execution Instructions
1. Open your Snowflake Worksheets.
2. Ensure active role, warehouse, database, and schemas (`bronze`, `silver`, `dim`, `ref`, `gold`) are selected.
3. Apply the diff to `SQL_10_ORDERS_CLEAN` inside `silver.orders_checked`.
4. Re-run `quality_checks()` to confirm zero defects on baseline.
5. Execute the mock order injection to observe the failure output, then run the cleanup statement.
6. Insert Arjun's new tier event into `ref.mock_crm_tier_events` and re-run pipeline to compare predictions.
