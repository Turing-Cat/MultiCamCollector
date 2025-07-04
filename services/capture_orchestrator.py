from typing import List
from models.camera import Frame

class CaptureOrchestrator:
    """Orchestrates the capture of frames from all cameras."""

    def __init__(self, preview_grid):
        self._preview_grid = preview_grid

    def capture_all_frames(self) -> List[Frame]:
        """Get the last fully captured frame from each camera worker."""
        return self._preview_grid.get_last_frames()
