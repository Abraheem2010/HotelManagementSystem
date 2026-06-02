from bookings.bookings import Booking
import datetime


class BookingManager:
    """
    Manages a collection of Booking objects in the hotel system.
    Responsible for loading, retrieving, adding, removing, and serializing bookings.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the BookingManager with an empty list of bookings.
        """
        self.bookings = []

    def load_bookings(self, booking_data, guest_manager, room_manager):
        """
        Load bookings from raw data. Skips bookings with missing guests or rooms.

        Args:
            booking_data (list): List of booking dictionaries.
            guest_manager (GuestManager): Manager to retrieve guest objects.
            room_manager (RoomManager): Manager to retrieve room objects.
        """
        self.bookings = []
        for data in booking_data:
            guest = guest_manager.get_guest_by_id(data["guest_id"])
            room = room_manager.get_room_by_id(data["room_number"])

            if not guest:
                print(f"Skipping booking {data['booking_id']}: Guest with ID {data['guest_id']} not found.")
                continue
            if not room:
                print(
                    f"Warning: Room with number {data['room_number']} not found. Skipping booking {data['booking_id']}.")
                continue

            check_in = data["check_in"]
            check_out = data["check_out"]

            if isinstance(check_in, str):
                check_in = datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
            if isinstance(check_out, str):
                check_out = datetime.datetime.strptime(check_out, "%Y-%m-%d").date()

            booking = Booking(
                booking_id=data["booking_id"],
                guest=guest,
                room=room,
                check_in=check_in,
                check_out=check_out,
                status=data.get("status", "confirmed"),
                paid=data.get("paid", False),
                installments=data.get("installments", 1)
            )
            self.bookings.append(booking)

    def add_booking(self, booking: Booking):
        """
        Add a booking to the internal list.

        Args:
            booking (Booking): The booking object to add.
        """
        self.bookings.append(booking)

    def get_all_bookings(self):
        """
        Retrieve all bookings.

        Returns:
            list: List of Booking objects.
        """
        return self.bookings

    def get_booking_by_id(self, booking_id):
        """
        Retrieve a booking by its ID.

        Args:
            booking_id (int): ID of the booking.

        Returns:
            Booking or None: The matching booking, or None if not found.
        """
        for booking in self.bookings:
            if booking.booking_id == booking_id:
                return booking
        return None

    def get_bookings_by_guest_id(self, guest_id):
        """
        Retrieve all bookings for a specific guest.

        Args:
            guest_id (int): ID of the guest.

        Returns:
            list: List of Booking objects.
        """
        return [b for b in self.bookings if b.guest.guest_id == guest_id]

    def get_bookings_by_room_id(self, room_id):
        """
        Retrieve all bookings for a specific room.

        Args:
            room_id (int): Room number.

        Returns:
            list: List of Booking objects.
        """
        return [b for b in self.bookings if b.room.room_number == room_id]

    def cancel_booking(self, booking_id):
        """
        Cancel a booking by removing it from the list.

        Args:
            booking_id (int): ID of the booking to cancel.
        """
        self.bookings = [b for b in self.bookings if b.booking_id != booking_id]

    def remove_booking(self, booking_id):
        """
        Removes a booking by ID and returns True if something was removed.
        """
        initial_count = len(self.bookings)
        self.bookings = [b for b in self.bookings if b.booking_id != booking_id]
        return len(self.bookings) < initial_count

    def to_dict(self):
        """
        Convert all bookings to a list of dictionaries.

        Returns:
            list: List of dictionaries representing each booking.
        """
        return [booking.to_dict() for booking in self.bookings]
