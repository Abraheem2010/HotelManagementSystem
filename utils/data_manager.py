import json
from typing import Any


class DataManager:
    """
    Utility class for loading and saving JSON data from a file.
    Used for persistence of rooms, guests, and bookings.
    """

    def __init__(self, filename: str):
        """
        Initialize the data manager with a target filename.

        Args:
            filename (str): Path to the JSON file to load/save data.
        Raises:
            TypeError: If filename is not a string.
        """
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")
        self.filename = filename

    def load(self) -> list:
        """
        Load and return data from the JSON file.

        Returns:
            list: Parsed data from the file. Returns an empty list if file not found or corrupted.
        """
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self, data: Any) -> None:
        """
        Save the given data to the JSON file.

        Args:
            data (Any): Data to be serialized and written to the file.
        """
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)
