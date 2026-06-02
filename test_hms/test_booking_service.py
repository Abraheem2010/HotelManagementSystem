import sys
import importlib
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

"""
Unit tests for BookingService.
Uses lightweight in‑memory stubs so the suite runs without project persistence.
"""

# Dynamically locate BookingService regardless of project layout
booking_service_module = None
for mod_name in (
    "hms.services.booking_service",
    "services.booking_service",
    "bookings.booking_service",
    "booking_service",
):
    try:
        booking_service_module = importlib.import_module(mod_name)
        break
    except ModuleNotFoundError:
        continue

if booking_service_module is None:
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
    for mod_name in (
        "hms.services.booking_service",
        "services.booking_service",
        "bookings.booking_service",
        "booking_service",
    ):
        try:
            booking_service_module = importlib.import_module(mod_name)
            break
        except ModuleNotFoundError:
            continue
    if booking_service_module is None:
        raise ImportError("Cannot locate booking_service module. Check project structure.")

BookingService = booking_service_module.BookingService

# ----------------- In‑memory domain stubs ------------------ #
class DummyGuest:
    def __init__(self, guest_id):
        self.guest_id = guest_id
        self.points = 0

    @staticmethod
    def get_discount_percentage():
        return 0

    @staticmethod
    def get_guest_type():
        return "Regular"

    def add_points(self, pts):
        self.points += pts


class DummyMemberGuest(DummyGuest):
    @staticmethod
    def get_discount_percentage():
        return 10

    @staticmethod
    def get_guest_type():
        return "Member"


class DummyRoom:
    def __init__(self, room_number, price: float = 100.0, status: str = "available", room_type: str = "Standard"):
        self.room_number = room_number
        self.price = price
        self.status = status
        self.room_type = room_type


class DummyBooking:
    def __init__(self, booking_id, guest, room, check_in, check_out, status, paid, installments):
        self.booking_id = booking_id
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.status = status
        self.paid = paid
        self.installments = installments

    def update_booking(self, new_in, new_out, new_room):
        self.check_in = new_in
        self.check_out = new_out
        self.room = new_room


class DummyBookingManager:
    def __init__(self):
        self.bookings = []

    def add_booking(self, booking):
        self.bookings.append(booking)

    def get_all_bookings(self):
        return self.bookings

    def get_booking_by_id(self, booking_id):
        return next((b for b in self.bookings if b.booking_id == booking_id), None)

    def get_bookings_by_room_id(self, room_number):
        return [b for b in self.bookings if b.room.room_number == room_number]

    @staticmethod
    def to_dict():
        return []


class DummyGuestManager:
    def __init__(self):
        self.guests = {1: DummyMemberGuest(1), 2: DummyGuest(2)}

    def get_guest_by_id(self, guest_id):
        return self.guests.get(guest_id)

    @staticmethod
    def to_dict():
        return []


class DummyRoomManager:
    def __init__(self):
        self.rooms = {101: DummyRoom(101), 102: DummyRoom(102, status="maintenance")}

    def get_room_by_id(self, room_number):
        return self.rooms.get(room_number)

    @staticmethod
    def to_dict():
        return []


class DummyDataStore:
    def __init__(self):
        self.saved = None

    def save(self, payload):
        self.saved = payload


class _FactoryStub:
    """Replacement for UniversalEntityFactory so tests are self‑contained."""

    @staticmethod
    def create_booking(booking_id, guest, room, check_in, check_out, installments=1):
        return DummyBooking(booking_id, guest, room, check_in, check_out, "confirmed", False, installments)

    @staticmethod
    def create_guest_service_strategy(_guest):
        return None


# Monkey‑patch BookingService dependencies only for the duration of this module's
# tests, then restore them, so the dummy stand-ins do not leak into the shared
# module and contaminate other test modules.
_orig_factory = booking_service_module.UniversalEntityFactory
_orig_member_guest = booking_service_module.MemberGuest


def setUpModule():
    booking_service_module.UniversalEntityFactory = _FactoryStub  # type: ignore
    booking_service_module.MemberGuest = DummyMemberGuest  # type: ignore


def tearDownModule():
    booking_service_module.UniversalEntityFactory = _orig_factory  # type: ignore
    booking_service_module.MemberGuest = _orig_member_guest  # type: ignore


# ---------------------------- TESTS ----------------------------------- #
class TestBookingService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guest_manager = DummyGuestManager()
        cls.room_manager = DummyRoomManager()
        cls.booking_manager = DummyBookingManager()
        cls.service = BookingService(
            cls.booking_manager,
            cls.guest_manager,
            cls.room_manager,
            DummyDataStore(),
            DummyDataStore(),
            DummyDataStore(),
            SimpleNamespace(),
        )

    def setUp(self):
        self.booking_manager.bookings = []

    def test_validate_booking_dates_past(self):
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)
        ok, _ = self.service.validate_booking_dates(101, yesterday, tomorrow)
        self.assertFalse(ok)

    def test_validate_booking_dates_future(self):
        tomorrow = date.today() + timedelta(days=1)
        after_tomorrow = date.today() + timedelta(days=2)
        ok, _ = self.service.validate_booking_dates(101, tomorrow, after_tomorrow)
        self.assertTrue(ok)

    def test_availability_overlap(self):
        start = date.today() + timedelta(days=1)
        end = date.today() + timedelta(days=3)
        existing = DummyBooking(10, self.guest_manager.get_guest_by_id(2), self.room_manager.get_room_by_id(101), start, end, "confirmed", False, 1)
        self.booking_manager.add_booking(existing)
        req_in = date.today() + timedelta(days=2)
        req_out = date.today() + timedelta(days=4)
        ok, _ = self.service.check_room_availability(101, req_in, req_out)
        self.assertFalse(ok)

    def test_create_booking_member_success(self):
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        after_tomorrow = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        booking, _ = self.service.create_booking(1, 1, 101, tomorrow, after_tomorrow, 2)
        self.assertIsNotNone(booking)
        self.assertEqual(len(self.booking_manager.get_all_bookings()), 1)
        self.assertEqual(self.guest_manager.get_guest_by_id(1).points, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
