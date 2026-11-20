# 0001: Switch from the synthetic Walmart dataset to Olist

**Status:** accepted (2026-11)

## Context
Version 1 (git tag `walmart-v1`) used a synthetic Walmart dataset loaded once into Neon.
Nothing in the source ever changed, so the incremental models, snapshots (SCD2) and CDC
ingestion were never actually exercised. An assessment also found modelling bugs in gold
(a join on store that copied every order line ~10x, a mixed fact grain, dimensions built
from the wide table).

## Decision
Rebuild on the Kaggle **Olist Brazilian e-commerce** dataset and add a **replay generator**
that writes Olist's real order lifecycle into Neon on a simulated clock.

## Why
- Olist has real lifecycle timestamps (purchase, approval, carrier, delivery), so changes over
  time can be replayed instead of invented.
- It contains real data-quality problems (orders without items, duplicate review IDs,
  carrier-before-approval timestamps, payment mismatches).
- The original CSVs act as an answer key to verify every pipeline layer.

## Consequences
- Silver, gold and tests are rewritten for the new tables. Docker, Airflow, Lakeflow Connect
  and dbt setup are reused.
- The Walmart code stays available at tag `walmart-v1`.
