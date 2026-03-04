import requests
import sys
from loguru import logger
from Tools.core.shared_db_instance import db

API_URL = "https://wago.tools/api/builds"
LATEST_API_URL = "https://wago.tools/api/builds/latest"

# Configure Loguru
logger.remove()
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{process}</cyan> - <level>{message}</level>"
logger.add(sys.stderr, format=LOG_FORMAT)


def fetch_versions():
    log = logger.bind(process="Registry")
    log.info(f"Fetching available builds from {API_URL}...")
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.error(f"Error fetching versions: {e}")
    return []


def fetch_latest_build_states():
    log = logger.bind(process="BuildState")
    log.info(f"Fetching latest build states from {LATEST_API_URL}...")
    try:
        r = requests.get(LATEST_API_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.error(f"Error fetching latest build states: {e}")
    return {}


def update_registry(builds_dict=None):
    log = logger.bind(process="Registry")
    if not builds_dict:
        return

    count = 0

    for product_name, entries in builds_dict.items():
        for entry in entries:
            ver_str = entry.get("version")
            if ver_str:
                try:
                    build_num = int(ver_str.split(".")[-1])
                    # UPSERT into DuckDB via shared db instance (API Middleware)
                    db.execute(
                        """
                        INSERT INTO registry.builds (id, version, product, last_seen) 
                        VALUES (?, ?, ?, now())
                        ON CONFLICT (version) DO UPDATE SET 
                            last_seen = excluded.last_seen,
                            product = excluded.product
                    """,
                        [build_num, ver_str, product_name],
                    )
                    count += 1
                except Exception as e:
                    log.error(f"Error processing {ver_str}: {e}")
                    continue

    log.success(f"Registry updated: {count} entries processed via DB Service.")


def update_build_states(states_dict=None):
    log = logger.bind(process="BuildState")
    if not states_dict:
        return

    count = 0
    for product_id, data in states_dict.items():
        try:
            db.execute(
                """
                INSERT INTO registry.build_state (product, version, created_at, build_config, product_config, cdn_config)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (product) DO UPDATE SET
                    version = excluded.version,
                    created_at = excluded.created_at,
                    build_config = excluded.build_config,
                    product_config = excluded.product_config,
                    cdn_config = excluded.cdn_config,
                    last_updated = now()
            """,
                [
                    product_id,
                    data.get("version"),
                    data.get("created_at"),
                    data.get("build_config"),
                    data.get("product_config"),
                    data.get("cdn_config"),
                ],
            )
            count += 1
        except Exception as e:
            log.error(f"Error updating state for {product_id}: {e}")

    log.success(f"Build states updated: {count} entries processed.")


if __name__ == "__main__":
    # 1. Update full registry
    build_data = fetch_versions()
    update_registry(build_data)

    # 2. Update latest build states
    latest_data = fetch_latest_build_states()
    update_build_states(latest_data)
