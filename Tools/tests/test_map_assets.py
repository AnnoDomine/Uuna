import sys
import os

sys.path.append(os.getcwd())

from Tools.core.api.managers.asset_manager import AssetManager
from loguru import logger


def test_map_ingestion():
    am = AssetManager()

    test_file = "Data/tmp_test_map.jpg"
    file_id = 999999  # Dummy ID for testing
    build = "Chronicle"  # Source tag
    description = "Map of Azeroth after the Great Sundering from the World of Warcraft: Chronicle. Shows Kalimdor, Eastern Kingdoms, Northrend, and Pandaria around the Maelstrom."

    if not os.path.exists(test_file):
        logger.error(f"File {test_file} not found!")
        return

    logger.info("Ingesting Azeroth Map into Dual-Storage...")
    chash = am.ingest_asset(test_file, file_id, build, description=description)

    if chash:
        logger.success(f"Asset ingested! Hash: {chash}")

        # Verify Retrieval
        data = am.get_asset(chash)
        logger.info(f"Retrieved {len(data)} bytes from DuckDB.")

        # Test Vector Search
        logger.info("Testing semantic search for the map...")
        search_results = am.vector_manager.search_memory(
            "Archivist", "Where is the Maelstrom located on the map of Azeroth?", limit=1
        )

        if search_results:
            res = search_results[0]
            logger.info(f"Search Result Score: {res['score']:.4f}")
            logger.info(f"Found Content: {res['content']}")
            logger.success("Dual-Storage & Vector Search Test successful!")


if __name__ == "__main__":
    test_map_ingestion()
