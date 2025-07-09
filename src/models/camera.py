from dataclasses import dataclass
import numpy as np

@dataclass
class Frame:
    """Represents a single frame from a camera."""
    camera_id: str
    sequence_id: int
    timestamp_ns: int
    rgb_image: np.ndarray
    depth_image: np.ndarray
