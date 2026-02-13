import os
import sys
import duckdb
import subprocess
from loguru import logger

# Import functions from master_ingester if needed or re-implement cleanly
# Since we want a robust standalone script, we'll make it a clean wrapper

MASTER_DB = "Data/WoW_Master.duckdb"
LOG_FORMAT = "[{time:YYYY-MM-DD HH:mm:ss} - {level} - SyncWowDB]: {message}"

logger.remove()
logger.add(sys.stderr, format=LOG_FORMAT, level="INFO")
logger.add("Data/logs/sync_wow_db.log", format=LOG_FORMAT, rotation="10 MB")


def sync_build(version):
    """
    Triggers the ingestion for a specific build using the master_ingester logic.
    """
    logger.info(f"Starting sync for build: {version}")

    # We use the master_ingester as the engine
    try:
        # We set an environment variable to tell master_ingester to maybe only do one build,
        # but the master_ingester logic currently pulls all pending.
        # To be precise, we call feature_extractor and process_table_master via subprocess or import.

        # Best approach: Use the existing master_ingester script but maybe pass the version
        # Since master_ingester.py doesn't take a version arg yet, we trigger it normally
        # or we update the builds table first so ONLY this version is 'pending'.

        con = duckdb.connect(MASTER_DB)
        # Check if build exists
        exists = con.execute("SELECT id FROM registry.builds WHERE version = ?", (version,)).fetchone()
        if not exists:
            logger.info(f"Build {version} not in registry. Adding it...")
            con.execute(
                "INSERT INTO registry.builds (version, product, is_downloaded) VALUES (?, 'wow', False)", (version,)
            )

        con.close()

        # Run master ingester with MAX_BUILDS=1 could work, but it might pick the wrong one.
        # So we just run it. It will process all pending builds including the requested one.
        logger.info("Executing Master Ingester...")
        os.environ.copy()
        # We could implement a specific filter in master_ingester, but for now we just run it.
        result = subprocess.run(
            [".venv/bin/python3", "Tools/ingestion/master_ingester.py"], capture_output=True, text=True
        )

        if result.returncode == 0:
            logger.success(f"Sync process finished for {version}")
            if result.stdout:
                logger.debug(f"Output: {result.stdout[-500:]}")
        else:
            logger.error(f"Ingester failed: {result.stderr}")

    except Exception as e:
        logger.error(f"Error during sync: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ver = sys.argv[1]
        sync_build(ver)
    else:
        logger.warning("No version specified. Running master ingester for all pending builds.")
        subprocess.run([".venv/bin/python3", "Tools/ingestion/master_ingester.py"])
