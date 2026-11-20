# Olist CDC Pipeline

A learning-focused data engineering project that turns a static Kaggle dataset into a **living
source system** and builds a change-data-capture pipeline on top of it.

> 🚧 **Work in progress.** The project is being rebuilt on the Olist dataset.
> The first version (synthetic Walmart data) is archived at git tag [`walmart-v1`](../../tree/walmart-v1).

## The idea

Most portfolio pipelines load a CSV once and never see a change. Here, a **replay generator**
writes the real order lifecycle from the Olist dataset (purchase → approval → shipping →
delivery → review) into Postgres on a simulated clock. The pipeline therefore has to handle
real inserts, updates, late data and messy records, and the original CSVs serve as an
**answer key** to verify every layer.

## Architecture

```
Olist CSVs ──► replay generator ──► Neon Postgres ──► Lakeflow Connect (CDC) ──► Databricks bronze
                                                                                      │ dbt
                                                                                      ▼
                                              Airflow orchestrates everything   silver → gold
```

Details: [docs/architecture.md](docs/architecture.md) · Replay rules: [docs/assumptions.md](docs/assumptions.md) ·
Decisions: [docs/decisions/](docs/decisions/)

## Tech stack
Neon Postgres (free tier) · Databricks Free Edition (Lakeflow Connect, Unity Catalog) · dbt ·
Apache Airflow (Docker) · Python (uv)

## Repository layout
```
src/olist_sim/   replay generator (planner, applier, checker)
sql/neon/        Neon schema setup (coming next)
dbt/             dbt project (to be rebuilt for Olist)
airflow/         Docker Compose setup and DAGs
docs/            architecture, assumptions, decision records
data/olist/      dataset (not committed; see below)
```

## Getting the data
Download the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
from Kaggle and unzip the 9 CSV files into `data/olist/`. The dataset is published by Olist on
Kaggle; check its licence there before reusing it.

## Setup (so far)
```bash
uv sync                 # install Python dependencies
cp .env.example .env    # then fill in your own connection details
```

## Status
- [x] v1 Walmart pipeline (archived)
- [x] Project restructured for Olist
- [ ] Neon schema + initial load
- [ ] Replay generator (turbo + steady) with answer-key checks
- [ ] Silver / gold models for Olist with SCD2 and reconciliation tests
- [ ] Airflow orchestration (generator → Lakeflow → dbt → checks)
- [ ] Chaos events (late data, duplicates, deletes, schema change)
