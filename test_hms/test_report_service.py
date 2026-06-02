"""Unit tests for **ReportService** with lightweight in‑memory stubs.
The module auto‑locates `report_service.py` up to 5 ancestors, so it runs
independently of project structure.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

# ------------------------- dynamic import -------------------------- #

def _load_report_service():
    here = Path(__file__).resolve()
    for ancestor in [here.parent] + list(here.parents)[:5]:
        for root, _dirs, files in os.walk(ancestor):
            if "report_service.py" in files:
                fp = Path(root) / "report_service.py"
                spec = importlib.util.spec_from_file_location("report_service", fp)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore[arg-type]
                    sys.modules["report_service"] = mod
                    return mod.ReportService  # type: ignore[attr-defined]
    raise ImportError("report_service.py not found (searched up to 5 levels)")


ReportService = _load_report_service()

# -------------------------- stubs ---------------------------------- #

class DummyGuest:
    def __init__(self, guest_id: int, name: str = "Guest"):
        self.guest_id = guest_id
        self.name = name

    @staticmethod
    def get_discount_percentage():
        return 10

    @staticmethod
    def get_guest_type():
        return "Member"


class DummyRoom:
    def __init__(self, room_number: int, status: str = "available"):
        self.room_number = room_number
        self.status = status


class DummyBooking:
    def __init__(self, booking_id, guest, room, check_in, check_out, status="confirmed"):
        self.booking_id = booking_id
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.status = status


class DummyBookingManager:
    def __init__(self):
        self.bookings: list[DummyBooking] = []

    def add_booking(self, b):
        self.bookings.append(b)

    def get_all_bookings(self):
        return self.bookings

    def get_bookings_by_guest_id(self, gid):
        return [b for b in self.bookings if b.guest.guest_id == gid]


class DummyGuestManager:
    def __init__(self):
        self.guests = {1: DummyGuest(1, "Alice"), 2: DummyGuest(2, "Bob")}

    def get_guest_by_id(self, gid):
        return self.guests.get(gid)


class DummyRoomManager:
    def __init__(self):
        self.rooms = [DummyRoom(101), DummyRoom(102)]

    def get_all_rooms(self):
        return self.rooms


class DummyBookingService:
    @staticmethod
    def calculate_booking_cost(_booking_id):
        return {
            "discount_percent": 10,
            "discount_amount": 20,
            "total_after_discount": 180,
        }


# ---------------------------- tests -------------------------------- #

class TestReportService(unittest.TestCase):
    def setUp(self):
        self.guest_mgr = DummyGuestManager()
        self.room_mgr = DummyRoomManager()
        self.booking_mgr = DummyBookingManager()
        self.report = ReportService(
            self.guest_mgr,
            self.room_mgr,
            self.booking_mgr,
            DummyBookingService,
        )

        ci = date.today() + timedelta(days=1)
        co = date.today() + timedelta(days=2)
        self.booking_mgr.add_booking(
            DummyBooking(1, self.guest_mgr.get_guest_by_id(1), self.room_mgr.rooms[0], ci, co)
        )

    def test_guest_history_found(self):
        name, bookings = self.report.view_guest_booking_history(1)
        self.assertEqual(name, "Alice")
        self.assertEqual(len(bookings), 1)

    def test_guest_history_not_found(self):
        name, error = self.report.view_guest_booking_history(99)
        self.assertIsNone(name)
        self.assertEqual(error, "Guest not found.")

    def test_search_by_date(self):
        target = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        _, matches = self.report.search_bookings_by_date(target)
        self.assertEqual(len(matches), 1)

    def test_search_by_guest_name(self):
        _, matches = self.report.search_bookings_by_guest("ali")
        self.assertEqual(len(matches), 1)

    def test_view_discounts_applied(self):
        res = self.report.view_discounts_applied()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["discount_percent"], 10)

    def test_room_status_report(self):
        rooms = self.report.view_room_status_report()
        self.assertEqual(len(rooms), 2)

    def test_upcoming_bookings(self):
        upcoming = self.report.view_upcoming_bookings()
        self.assertEqual(len(upcoming), 1)

    def test_occupancy_rate(self):
        rate = self.report.view_occupancy_rate()
        self.assertIsInstance(rate, (int, float))


if __name__ == "__main__":
    unittest.main(verbosity=2)
