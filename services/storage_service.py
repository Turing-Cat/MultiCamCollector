import json
import os
from datetime import datetime
from typing import List
import cv2

from models.camera import Frame
from models.metadata import CaptureMetadata

class StorageService:
    """Handles saving captured frames and metadata to disk."""

    def __init__(self, root_dir: str):
        self._root_dir = root_dir

    def save(self, frames: List[Frame], metadata: CaptureMetadata) -> None:
        """Save frames and metadata to a structured directory."""
        session_dir = self._create_session_directory(metadata)

        # Save metadata
        metadata_path = os.path.join(session_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=4)

        # Save frames
        for frame in frames:
            timestamp_str = datetime.now().strftime("%Y%m%dT%H%M%S")
            rgb_filename = f"{timestamp_str}_{frame.camera_id}_RGB.png"
            depth_filename = f"{timestamp_str}_{frame.camera_id}_Depth.tiff"

            rgb_path = os.path.join(session_dir, rgb_filename)
            depth_path = os.path.join(session_dir, depth_filename)

            # Save RGB image
            cv2.imwrite(rgb_path, frame.rgb_image)

            # Save depth image as 16-bit TIFF
            cv2.imwrite(depth_path, frame.depth_image.astype("uint16"))

        print(f"Saved {len(frames)} frames to {session_dir}")

    def _create_session_directory(self, metadata: CaptureMetadata) -> str:
        """Create the directory for the current capture session."""
        date_str = datetime.now().strftime("%Y%m%d")
        dir_path = os.path.join(
            self._root_dir,
            date_str,
            metadata.lighting.value,
            metadata.background_id,
            f"seq_{metadata.sequence_number:03d}",
        )
        os.makedirs(dir_path, exist_ok=True)
        return dir_path
