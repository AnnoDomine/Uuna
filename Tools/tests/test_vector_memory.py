import sys
import os

sys.path.append(os.getcwd())

from Tools.core.api.managers.vector_manager import VectorManager
from loguru import logger


def test_vector_db():
    logger.info("Starting Vector DB Test...")
    vm = VectorManager(db_path="Data/knowledge/test_memory.duckdb")

    # Test adding memory
    role = "Archivist"
    content = "The table 'SpellEffect' usually contains references to 'Spell' via the 'SpellID' column."
    metadata = {"build": "9.0.1", "confidence": 0.9}

    logger.info("Adding test memory...")
    mem_id = vm.add_memory(role, content, metadata)
    if mem_id:
        logger.success(f"Successfully added memory with ID: {mem_id}")
    else:
        logger.error("Failed to add memory")
        return

    # Test searching memory
    logger.info("Searching for similar patterns...")
    query = "Where can I find spell IDs in the database?"
    results = vm.search_memory(role, query, limit=2)

    for i, res in enumerate(results):
        logger.info(f"Result {i + 1} (Score: {res['score']:.4f}):")
        logger.info(f"Content: {res['content']}")
        logger.info(f"Metadata: {res['metadata']}")

    if len(results) > 0:
        logger.success("Vector search test passed!")
    else:
        logger.error("Vector search returned no results")


if __name__ == "__main__":
    test_vector_db()
