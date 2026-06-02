import datetime
from constants import VALID_ROOM_TYPES, VALID_ROOM_STATUSES
from system.universal_factory import UniversalEntityFactory


class RoomService:
    """
    Service class for managing room operations such as add, update, remove, and check availability.
    """

    def __init__(self, room_manager, room_data, booking_manager):
        """
        Initializes the RoomService with managers and data handlers.

        Args:
            room_manager: Instance of RoomManager for managing room objects.
            room_data: Instance of DataManager responsible for persisting room data.
            booking_manager: Instance of BookingManager for checking bookings when verifying availability.
        """
        self.room_manager = room_manager
        self.room_data = room_data
        self.bookings = booking_manager

    def add_room(self, room_number, room_type, price, status='available'):
        """
        Adds a new room to the system.

        Args:
            room_number (int): The unique number of the room.
            room_type (str): The type of the room (e.g., single, double, suite).
            price (float): The price per night for the room.
            status (str): The initial status of the room.

        Returns:
            str: A message indicating the result of the operation.
        """
        if room_type not in VALID_ROOM_TYPES:
            return f"Invalid room type. Choose from {', '.join(sorted(VALID_ROOM_TYPES))}."
        if price <= 0:
            return "Price must be positive."
        if status not in VALID_ROOM_STATUSES:
            return f"Invalid status. Choose from {', '.join(sorted(VALID_ROOM_STATUSES))}."
        if self.room_manager.get_room_by_id(room_number):
            return "A room with this number already exists."

        room = UniversalEntityFactory.create_room(room_number, room_type, price, status)
        self.room_manager.add_room(room)
        self.room_data.save(self.room_manager.to_dict())
        return "Room added successfully."

    def view_rooms(self):
        """
        Retrieves all rooms in the system.

        Returns:
            str or list: A message if no rooms exist, or a list of room string representations.
        """
        rooms = self.room_manager.get_all_rooms()
        if not rooms:
            return "No rooms in the system."
        return [str(room) for room in rooms]

    def update_room(self, room_number, room_type=None, price=None, status=None):
        """
        Updates an existing room's details.

        Args:
            room_number (int): The room to update.
            room_type (str, optional): New type for the room.
            price (float, optional): New price for the room.
            status (str, optional): New status for the room.

        Returns:
            str: A message indicating the outcome of the update.
        """
        room = self.room_manager.get_room_by_id(room_number)
        if not room:
            return "Room not found."

        try:
            room.update_room(room_type, price, status)
            self.room_data.save(self.room_manager.to_dict())
            return "Room updated successfully."
        except ValueError as ve:
            return f"Error: {ve}"

    def remove_room(self, room_number):
        """
        Removes a room from the system.

        Args:
            room_number (int): The room number to remove.

        Returns:
            str: A message indicating the result.
        """
        room = self.room_manager.get_room_by_id(room_number)
        if not room:
            return "Room not found."

        self.room_manager.remove_room(room_number)
        self.room_data.save(self.room_manager.to_dict())
        return "Room removed successfully."

    def check_availability(self, room_number, desired_check_in, desired_check_out):
        """
        Checks whether a specific room is available between two dates.

        Args:
            room_number (int): The room number to check.
            desired_check_in (str): Check-in date in YYYY-MM-DD format.
            desired_check_out (str): Check-out date in YYYY-MM-DD format.

        Returns:
            tuple: (bool, str) indicating whether the room is available and a related message.
        """
        room = self.room_manager.get_room_by_id(room_number)
        if not room:
            return False, "Room not found."

        if room.status == 'maintenance':
            return False, "Room is currently under maintenance."

        try:
            desired_in = datetime.datetime.strptime(desired_check_in, "%Y-%m-%d").date()
            desired_out = datetime.datetime.strptime(desired_check_out, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format."

        bookings_for_room = self.bookings.get_bookings_by_room_id(room_number)
        for booking in bookings_for_room:
            existing_in = booking.check_in if isinstance(booking.check_in, datetime.date) \
                else datetime.datetime.strptime(booking.check_in, "%Y-%m-%d").date()
            existing_out = booking.check_out if isinstance(booking.check_out, datetime.date) \
                else datetime.datetime.strptime(booking.check_out, "%Y-%m-%d").date()
            if desired_in < existing_out and desired_out > existing_in:
                return False, "The room is not available for the selected dates."

        return True, "The room is available."
