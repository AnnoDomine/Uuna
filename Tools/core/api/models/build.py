from datetime import datetime
from .base import DBModel


class Build(DBModel):
    id: int
    version: str
    product: str = "wow"
    is_downloaded: bool = False
    indexed: bool = False
    last_seen: datetime = datetime.now()

    @classmethod
    def get_schema(cls) -> str:
        return "registry"
