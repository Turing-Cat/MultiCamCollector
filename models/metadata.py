from dataclasses import dataclass, field
from enum import Enum
import time

class LightingLevel(Enum):
    """Enum for lighting levels."""
    VERY_DARK = "VeryDark"
    DARK = "Dark"
    NORMAL = "Normal"

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
