from dataclasses import dataclass

@dataclass
class Settings:
    save_rgb: bool = True
    save_depth: bool = True
    save_point_cloud: bool = False
    lock_metadata: bool = False
    path: str = ""
