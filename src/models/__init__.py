"""
This file makes the 'models' directory a Python package and exposes key data classes
for easier importing.
"""

from .camera import Frame
from .metadata import CaptureMetadata, LightingLevel

__all__ = [
    "Frame",
    "CaptureMetadata",
    "LightingLevel",
]
