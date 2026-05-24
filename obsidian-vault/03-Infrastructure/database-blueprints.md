# OMEGA Database Engineering Blueprints

This document details the standard schema designs, indexing rules, transaction isolations, and query optimization guidelines for OMEGA databases (hosted natively on PlanetScale / MySQL).

---

## 1. Core Schema Design Standards

All relational tables compiled under OMEGA must adhere to these structural constraints:

### A. Primary Key Construction
- High-write transactional tables (OLTP) **MUST** utilize narrow, monotonically increasing primary keys:
  ```sql
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
  ```
- **Banned**: Random UUID values as clustered primary keys (causes severe B-tree page fragmentation and index node splits). 
- **Exception**: If external UUIDs are required, store them in a secondary `BINARY(16)` or `VARCHAR(36)` column with a unique index, keeping the primary key clustered on the auto-increment integer.

### B. Character Sets and Collations
- All databases must use modern, full unicode support:
  - **Character Set**: `utf8mb4`
  - **Collation**: `utf8mb4_0900_ai_ci` (MySQL 8.0 standard)

### C. Data Type Disciplines
- Prefer `NOT NULL` constraints on all columns. Default to empty strings or specific numerical standard defaults where possible to avoid `NULL` logic complexities.
- Use `DATETIME` rather than `TIMESTAMP` for dates to prevent timezone boundary bugs (unless automatic UTC mapping is explicitly required).
- Do not use database-level `ENUM` columns (schema modifications to ENUMs trigger full table rebuilds on older engines). Normalize state structures into a secondary Lookup Table.

---

## 2. Composite Indexing Standard

To optimize search query performance, all composite (multi-column) indexes must be constructed based on the **Leftmost Prefix Rule**:

```
Composite Index Order = [Equality Predicates] -> [Sort/Range Predicates]
```

### Best Practices
- Place columns queried via absolute equality (`=`, `IS NULL`) first in the index.
- Place columns queried via range predicates (`>`, `<`, `LIKE`, `BETWEEN`) or sorting (`ORDER BY`) last. A range predicate stops index matching for any subsequent columns in the composite index.
- Periodically check the `performance_schema` to identify and drop unused secondary indexes (`count_read = 0`).

---

## 3. Query Optimization and Explain Auditing

OMEGA developers must run `EXPLAIN` or `EXPLAIN ANALYZE` on all query vectors.

### Red Flags to Eliminate
- `type: ALL`: Triggers a full table scan.
- `Using filesort`: Indicates sorting operations are performed in memory rather than using indexes.
- `Using temporary`: Heavy operations spawning temporary disk tables.

### Optimization Rules
- Enforce **Cursor Pagination** (filtering on keys like `WHERE id > LAST_ID LIMIT N`) instead of large `OFFSET` queries (e.g., `LIMIT 10000, 10` forces database to read and discard 10,000 rows).
- Batch inserts in sizes of **500 to 5000 rows** to maximize throughput.

---

## 4. Transaction Isolation and Locking

- **Default Isolation Level**: `REPEATABLE READ` (utilizes gap locks to prevent phantom reads).
- High-contention workloads should scale down to `READ COMMITTED` to avoid deadlocks.
- Perform all heavy I/O operations (like calling external APIs) **outside** of active database transactions. Keep transactions as short as humanly possible to minimize row lock hold times.
- Ensure row modifications are executed in a consistent sorted order across concurrent workflows to prevent cyclic **Deadlocks**.
