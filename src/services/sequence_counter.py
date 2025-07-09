import json
import os
import threading

class SequenceCounter:
    """
    Manages a persistent, thread-safe sequence number.
    """
    def __init__(self, storage_dir: str):
        self._lock = threading.Lock()
        self._file_path = os.path.join(storage_dir, "sequence.json")
        self._current_number = self._load()

    def _load(self) -> int:
        """Load the last sequence number from the file."""
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, "r") as f:
                    data = json.load(f)
                    return int(data.get("sequence_number", 1))
            except (json.JSONDecodeError, ValueError):
                # If file is corrupt or empty, start from 1
                return 1
        return 1

    def _save(self):
        """Save the current sequence number to the file."""
        with open(self._file_path, "w") as f:
            json.dump({"sequence_number": self._current_number}, f)

    def get_current(self) -> int:
        """Get the current sequence number without incrementing."""
        with self._lock:
            return self._current_number

    def increment(self):
        """Increment the sequence number and save it."""
        with self._lock:
            self._current_number += 1
            self._save()

    def set_current(self, number: int):
        """Manually set the sequence number."""
        with self._lock:
            self._current_number = number
            self._save()
