from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.services.ingestion.models import DisasterObservation, DataSourceType

class BaseConnector(ABC):
    """
    Abstract connector interface for real and demo data sources.
    Guarantees graceful fallback when external credentials are not present.
    """
    def __init__(self, name: str, source_type: DataSourceType = DataSourceType.SIMULATED):
        self.name = name
        self.source_type = source_type
        self.is_connected = True
        self.last_sync = ""

    @abstractmethod
    def fetch_observations(self) -> List[DisasterObservation]:
        """Fetches normalized observations from the upstream provider or mock stream."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Returns connector health and configuration metadata."""
        pass
