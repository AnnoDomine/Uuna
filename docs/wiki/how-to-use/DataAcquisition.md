# 📥 Data Acquisition (Ingestion)
[⬅️ Back to Home](../Home.md)

The Library requires raw DB2 data to function. We use a dedicated "Master Ingester" to fetch and deduplicate data from Wago.tools.

## The Ingestion Pipeline
The `master_ingester.py` script performs the following:
1.  **Syncs** the build list with Wago.tools.
2.  **Downloads** CSV files for each table.
3.  **Deduplicates** data using MD5 row hashing.
4.  **Integrates** data into the DuckDB Archive.

## How to Start Syncing
To start a batch sync (e.g., for 100 builds):
```bash
MAX_BUILDS=100 python3 Tools/ingestion/master_ingester.py
```

## Monitoring Progress
Logs are written to `Data/logs/master_ingester.log`. You can watch them in real-time:
```bash
tail -f Data/logs/master_ingester.log
```
