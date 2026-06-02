from rooms.rooms import Room


class RoomManager:
    """
    Manages a collection of Room objects including loading, retrieving, and updating room data.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the RoomManager with an empty list of rooms.
        """
        self.rooms = []

    def load_rooms(self, room_data):
        """
        Loads rooms from a list of dictionaries (e.g., from JSON).

        Args:
            room_data (list): A list of dictionaries, each representing a room's attributes.
        """
        self.rooms = [Room(**data) for data in room_data]

    def get_room_by_id(self, room_number):
        """
        Retrieves a room by its unique room number.

        Args:
            room_number (int): The room number to search for.

        Returns:
            Room or None: The matching Room object if found, else None.
        """
        for room in self.rooms:
            if room.room_number == room_number:
                return room
        return None

    def add_room(self, room: Room):
        """
        Adds a new room to the room list.

        Args:
            room (Room): The Room object to add.
        """
        self.rooms.append(room)

    def get_all_rooms(self):
        """
        Returns a list of all rooms in the system.

        Returns:
            list: A list of Room objects.
        """
        return self.rooms

    def get_available_rooms(self):
        """
        Returns all rooms that are currently available.

        Returns:
            list: A list of Room objects with status 'available'.
        """
        return [room for room in self.rooms if room.status == "available"]

    def remove_room(self, room_number):
        """
        Removes a room with the specified room number.

        Args:
            room_number (int): The number of the room to remove.
        """
        self.rooms = [room for room in self.rooms if room.room_number != room_number]

    def to_dict(self):
        """
        Converts the current list of rooms to a list of dictionaries.

        Returns:
            list: A list of dictionaries representing the room data.
        """
        return [room.to_dict() for room in self.rooms]
