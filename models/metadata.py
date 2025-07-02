from dataclasses import dataclass, field
from enum import Enum
import time

class LightingLevel(Enum):
    """Enum for lighting levels."""
    VERY_DARK = "极暗"
    DARK = "暗光"
    NORMAL = "正常光"

@dataclass
class CaptureMetadata:
    """Metadata for a single capture sequence."""
    lighting: LightingLevel = LightingLevel.NORMAL
    background_id: str = "default_bg"
    sequence_number: int = 1
    timestamp: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "lighting": self.lighting.value,
            "background_id": self.background_id,
            "sequence_number": self.sequence_number,
            "timestamp": self.timestamp,
        }
