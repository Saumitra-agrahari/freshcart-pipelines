# FreshCart ELT Pipeline (Snowflake)

This directory contains the SQL transformations and quality check edits for Part B, verified against `material/07-10-2026/freshcart_elt_commented.ipynb`.

## Files
- `snowflake_edits.sql`: SQL and Python notebook diffs for:
  - Validation rule `unsupported_currency` in `SQL_10_ORDERS_CLEAN` (Cell 17)
  - Sixth quality check in `quality_checks()` dictionary (`gold.fct_orders`, Cell 24)
  - Failing mock order injection & cleanup statement (Cell 6 & table query)
  - New CRM tier event for Arjun in Python list `MOCK_CRM_TIER_EVENTS` (Cell 6)

## Execution Instructions
1. Open `freshcart_elt_commented.ipynb` in Google Colab or your local Jupyter environment.
2. Apply Edit (a) to `SQL_10_ORDERS_CLEAN` in Cell 17.
3. Apply Edit (b) to the `checks` dict in `quality_checks()` in Cell 24.
4. Apply Edit (d) to `MOCK_CRM_TIER_EVENTS` in Cell 6.
5. Run `run_pipeline()` to verify baseline counts and data quality checks against your Snowflake account.
