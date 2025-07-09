from dataclasses import dataclass, field
import numpy as np
from typing import Optional

@dataclass
class Frame:
    """Represents a single frame from a camera."""
    camera_id: str
    sequence_id: int
    timestamp_ns: int
    rgb_image: np.ndarray
    depth_image: np.ndarray
    rgb_image_right: Optional[np.ndarray] = field(default=None)
