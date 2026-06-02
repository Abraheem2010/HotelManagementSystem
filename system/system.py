from rooms.room_manager import RoomManager
from guests.guest_manager import GuestManager
from bookings.booking_manager import BookingManager
from utils.data_manager import DataManager

from rooms.room_service import RoomService
from guests.guest_service import GuestService
from bookings.booking_service import BookingService
from reports.report_service import ReportService


class HotelManagementSystem:
    """
    Central system class for managing hotel operations,
    including rooms, guests, bookings, and reports.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize all managers, services, and load data from storage.
        Also initializes ID counters for guests and bookings.
        """

        # Data managers
        self.room_data = DataManager("rooms.json")
        self.guest_data = DataManager("guests.json")
        self.booking_data = DataManager("bookings.json")

        # Entity managers
        self.room_manager = RoomManager()
        self.guest_manager = GuestManager()
        self.booking_manager = BookingManager()

        # Load saved data
        self.room_manager.load_rooms(self.room_data.load())
        self.guest_manager.load_guests(self.guest_data.load())
        self.booking_manager.load_bookings(
            self.booking_data.load(),
            self.guest_manager,
            self.room_manager
        )

        # Service layers
        self.room_service = RoomService(self.room_manager, self.room_data, self.booking_manager)
        self.guest_service = GuestService(self.guest_manager, self.guest_data)
        self.booking_service = BookingService(
            self.booking_manager,
            self.guest_manager,
            self.room_manager,
            self.booking_data,
            self.guest_data,
            self.room_data,
            self.room_service
        )
        self.report_service = ReportService(
            self.guest_manager,
            self.room_manager,
            self.booking_manager,
            self.booking_service
        )

        # ID counters
        self.next_guest_id = self._get_next_guest_id()
        self.next_booking_id = self._get_next_booking_id()

    def _get_next_guest_id(self) -> int:
        """
        Generate the next available guest ID based on current data.

        Returns:
            int: The next guest ID.
        """
        guests = self.guest_manager.get_all_guests()
        return max((g.guest_id for g in guests), default=0) + 1

    def _get_next_booking_id(self) -> int:
        """
        Generate the next available booking ID based on current data.

        Returns:
            int: The next booking ID.
        """
        bookings = self.booking_manager.get_all_bookings()
        return max((b.booking_id for b in bookings), default=0) + 1

    def save_all(self) -> None:
        """
        Save all current data to persistent JSON files.
        """
        self.room_data.save(self.room_manager.to_dict())
        self.guest_data.save(self.guest_manager.to_dict())
        self.booking_data.save(self.booking_manager.to_dict())
