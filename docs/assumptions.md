# Replay assumptions

The Olist dataset records the main milestones of each order, but not everything. Where the data is
silent, the replay generator follows these rules. All of them are implemented in one place:
`src/olist_sim/rules.py`.

| # | Rule | Why |
|---|------|-----|
| 1 | Payments are inserted at **purchase** (checkout), not at approval. | Matches how checkout works: you pay, then the payment is approved. |
| 2 | **All products and sellers** are loaded at the start date. | Olist has no creation date for them. |
| 3 | Reviews dated **before their order** (64 cases) are inserted at their own date anyway. | Keeps real-world mess (a review briefly exists without an order) for silver tests to catch. |
| 4 | Orders ending as **canceled, unavailable, invoiced or processing** change to that status **the day after their last known timestamp**. | Olist has no timestamp for these final statuses. |
| 5 | The 8 orders that are **delivered but have no delivery date** are delivered on their **estimated delivery date**. | Needed to place the event on the timeline; flagged as an assumption. |
| 6 | `created_at` / `updated_at` use **simulated time**, not wall-clock time. | Keeps them consistent with business timestamps, so the `updated_at` vs log-based CDC comparison is meaningful. |
| 7 | The **status column only moves forward**: created → approved → invoiced/processing → shipped → delivered (canceled/unavailable are endings). Each event still fills its own timestamp column. | 1,294 replayed orders reach the carrier before approval (an Olist data error). A real app wouldn't move status backwards; the odd timestamps stay for silver tests. |
| 8 | A replicated one-row table **`shop.heartbeat`** holds the current simulated time. | Lets the warehouse know "data is complete up to simulated time X" (and measure replication lag). |
| 9 | The replay runs to the **natural end** of the data (last event: 2018-10-29), including the quiet tail. | The thinning tail is a realistic freshness-monitoring test. |
| 10 | Replay **start date is 2017-09-01**: everything before is the initial load (23,297 orders, 1,408 in flight). | Gives a real initial snapshot and includes Black Friday 2017 about 12 weeks in. |
