import json
import os
from datetime import datetime
from typing import List, Dict, Any
import cv2
import numpy as np

from src.models.camera import Frame
from src.models.metadata import CaptureMetadata
from src.models.settings import Settings

class StorageService:
    """Handles saving captured frames and metadata to disk."""

    def __init__(self, root_dir: str):
        self.set_root_dir(root_dir)

    def get_root_dir(self) -> str:
        """Return the root directory for saving data."""
        return self._root_dir

    def set_root_dir(self, root_dir: str):
        """Set the root directory for saving data."""
        self._root_dir = root_dir
        os.makedirs(self._root_dir, exist_ok=True)

    def save(self, frames: List[Frame], metadata: CaptureMetadata, settings: Settings) -> str:
        """Save frames and metadata, then return the session directory."""
        session_dir = self._create_session_directory(metadata)

        # Save metadata
        metadata_path = os.path.join(session_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, indent=4, ensure_ascii=False)

        # Save frames
        for frame in frames:
            # Generate a unique timestamp for each frame to prevent filename collisions
            timestamp_str = datetime.now().strftime("%Y%m%dT%H%M%S%f")[:-3]
            base_filename = f"{timestamp_str}_{frame.camera_id}_frame_{frame.frame_number:04d}"

            if settings.save_rgb:
                rgb_filename = f"{base_filename}_RGB.png"
                rgb_path = os.path.join(session_dir, rgb_filename)
                self._save_image_unicode(rgb_path, frame.rgb_image)

            if settings.save_depth and frame.depth_image is not None:
                depth_filename = f"{base_filename}_Depth.tiff"
                depth_path = os.path.join(session_dir, depth_filename)
                
                # Handle potential NaN/inf values
                safe_depth = np.nan_to_num(frame.depth_image, nan=0.0, posinf=0.0, neginf=0.0)
                
                # If the depth image is float, assume it's in meters and convert to uint16 millimeters
                if np.issubdtype(safe_depth.dtype, np.floating):
                    depth_mm = np.clip(safe_depth * 1000, 0, 65535).astype("uint16")
                else:
                    depth_mm = safe_depth.astype("uint16")
                    
                self._save_image_unicode(depth_path, depth_mm)

            if settings.save_point_cloud:
                pc_filename = f"{base_filename}_PC.ply"
                pc_path = os.path.join(session_dir, pc_filename)
                self._save_placeholder_ply(pc_path)

        print(f"Saved data for {len(frames)} frames to {session_dir}")
        return session_dir

    def _save_image_unicode(self, path: str, image: np.ndarray):
        """Saves an image to a path that may contain Unicode characters."""
        try:
            is_success, buffer = cv2.imencode(os.path.splitext(path)[1], image)
            if is_success:
                with open(path, "wb") as f:
                    f.write(buffer)
            else:
                print(f"Failed to encode image for path: {path}")
        except Exception as e:
            print(f"Error saving image to {path}: {e}")

    def _save_placeholder_ply(self, path: str):
        """Saves a placeholder PLY file."""
        header = """ply
format ascii 1.0
element vertex 0
property float x
property float y
property float z
end_header
"""
        with open(path, 'w') as f:
            f.write(header)

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
