class Room:
    """
    Represents a hotel room, including its number, type, price, and status.
    """

    def __init__(self, room_number, room_type, price, status='available'):
        """
        Initialize a Room instance.

        Args:
            room_number (int): Unique identifier for the room.
            room_type (str): Type of the room (e.g., 'single', 'double', 'suite').
            price (float): Price per night for the room.
            status (str): Current status of the room (e.g., 'available', 'occupied', 'maintenance').
        """
        self.room_number = room_number
        self.room_type = room_type
        self.price = price
        self.status = status

    def to_dict(self):
        """
        Convert the Room object into a dictionary format.

        Returns:
            dict: A dictionary containing room details.
        """
        return {
            "room_number": self.room_number,
            "room_type": self.room_type,
            "price": self.price,
            "status": self.status
        }

    def __str__(self):
        """
        Return a string representation of the room.

        Returns:
            str: A string summarizing the room information.
        """
        return f"Room {self.room_number}: room_type: {self.room_type}, price: {self.price}, status: {self.status}"

    def update_room(self, room_type=None, price=None, status=None):
        """
        Update the room details (type, price, and/or status).

        Args:
            room_type (str, optional): New type for the room.
            price (float, optional): New price for the room. Must be positive if provided.
            status (str, optional): New status for the room.

        Raises:
            ValueError: If the provided price is not a positive number.
        """
        if room_type:
            self.room_type = room_type
        if price is not None:
            if price <= 0:
                raise ValueError("Price must be a positive number.")
            self.price = price
        if status:
            self.status = status
