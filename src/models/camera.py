from dataclasses import dataclass, field
import numpy as np
from typing import Optional

@dataclass
class Frame:
    """Represents a single frame from a camera."""
    camera_id: str
    frame_number: int
    timestamp_ns: int
    rgb_image: np.ndarray
    depth_image: np.ndarray
    rgb_image_left: Optional[np.ndarray] = field(default=None)
    rgb_image_right: Optional[np.ndarray] = field(default=None)
    sequence_id: int = 0 # Add default for backward compatibility if needed
