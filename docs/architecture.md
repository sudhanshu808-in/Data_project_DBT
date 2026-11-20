# Architecture

## Data flow

```
data/olist/*.csv (the "diary")
      │  planner (offline) → event timeline
      ▼
replay generator ──writes──► Neon Postgres
  (steady: every 2h, +1 sim day, branch main)    schema shop  (7 tables + heartbeat)  ← replicated
  (turbo:  back-to-back, branch dev)             schema sim   (clock, run_log, settings) ← private
                                                        │ Lakeflow Connect (log-based CDC)
                                                        ▼
                                              Databricks bronze
                                                        │ dbt (silver → gold, snapshots)
                                                        ▼
                                              gold star schema
Airflow orchestrates: generator → Lakeflow → dbt build → checker
```

Reference data that never changes bypasses CDC: `geolocation` goes to a Databricks Volume,
`category_translation` becomes a dbt seed.

## Neon `shop` schema
| Table | Primary key | Notes |
|-------|-------------|-------|
| customers | customer_id | one row per order (Olist quirk); real person = customer_unique_id |
| orders | order_id | lifecycle columns filled as events happen |
| order_items | (order_id, order_item_id) | |
| order_payments | (order_id, payment_sequential) | |
| order_reviews | (review_id, order_id) | review_id alone is not unique; `REPLICA IDENTITY FULL` (long text) |
| products | product_id | |
| sellers | seller_id | |
| heartbeat | (single row) | current simulated time |

Design rules: keep source columns as-is (typos, text IDs, naive timestamps); every table gets
`created_at`/`updated_at` in simulated time; no foreign keys; zip codes are text.

Users: `generator` (read/write shop + sim), `databricks_replication` (read-only shop + REPLICATION).
Publication `databricks_publication` lists the shop tables explicitly (sim stays private).

## Generator
- **Planner:** CSVs + rules → deterministic event timeline (sorted by time, event-type order, ID).
- **Applier:** each run locks `sim.clock`, applies events in `[clock, clock + step)` one statement
  per event, writes `run_log` + heartbeat, advances the clock, all in **one transaction**
  (crash = nothing happened; safe to retry).
- **Checker (answer key):** L1 Neon vs expected, L2 bronze vs Neon, L3 gold vs expected as-of heartbeat.

## Neon branches
`main` (steady replay, feeds Lakeflow) · `baseline` (frozen save point at 2017-09-01) · `dev` (turbo testing).

See `docs/assumptions.md` for the replay rules and `docs/decisions/` for why things are the way they are.
