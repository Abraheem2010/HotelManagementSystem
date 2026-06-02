"""
Unit tests for **BookingManager**
================================

These tests cover the core behaviour of `BookingManager` while using simple
in‑memory stubs for guests and rooms. No JSON files are touched.

Run all project tests with:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

from datetime import date, timedelta
import io
import unittest
from unittest.mock import patch

from bookings.booking_manager import BookingManager
from bookings.bookings import Booking

# ---------------------------------------------------------------------------
# Minimal stubs for guests and rooms
# ---------------------------------------------------------------------------

class _GuestStub:  # noqa: D401, D101 — simple data holder
    def __init__(self, guest_id: int):
        self.guest_id = guest_id


class _RoomStub:  # noqa: D401, D101
    def __init__(self, room_number: int):
        self.room_number = room_number


class _GuestMgrStub:  # noqa: D401, D101 — returns fixed guests
    def __init__(self):
        self._guests = {1: _GuestStub(1), 2: _GuestStub(2)}

    def get_guest_by_id(self, gid):  # noqa: D401
        return self._guests.get(gid)


class _RoomMgrStub:  # noqa: D401, D101 — returns fixed rooms
    def __init__(self):
        self._rooms = {101: _RoomStub(101), 102: _RoomStub(102)}

    def get_room_by_id(self, rid):  # noqa: D401
        return self._rooms.get(rid)


# ---------------------------------------------------------------------------
# Test‑case class
# ---------------------------------------------------------------------------

class BookingManagerTest(unittest.TestCase):
    """Basic CRUD and query checks for `BookingManager`."""

    @classmethod
    def setUpClass(cls):
        cls.guests = _GuestMgrStub()
        cls.rooms = _RoomMgrStub()

    def setUp(self):
        self.mgr = BookingManager()
        self.mgr.bookings = []  # ensure a clean slate

        tomorrow = date.today() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        self.sample = Booking(
            booking_id=1,
            guest=self.guests.get_guest_by_id(1),
            room=self.rooms.get_room_by_id(101),
            check_in=tomorrow,
            check_out=day_after,
            status="confirmed",
            paid=False,
            installments=1,
        )

    # ------------------------------------------------------------------
    # Singleton behaviour
    # ------------------------------------------------------------------
    def test_singleton_identity(self):
        self.assertIs(BookingManager(), BookingManager())

    # ------------------------------------------------------------------
    # Add / retrieve
    # ------------------------------------------------------------------
    def test_add_and_retrieve(self):
        self.mgr.add_booking(self.sample)
        self.assertIn(self.sample, self.mgr.get_all_bookings())

    # ------------------------------------------------------------------
    # Loading from dicts
    # ------------------------------------------------------------------
    def test_load_creates_booking(self):
        start = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        end = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        data = [{
            "booking_id": 10,
            "guest_id": 1,
            "room_number": 101,
            "check_in": start,
            "check_out": end,
            "status": "confirmed",
            "paid": True,
            "installments": 2,
        }]
        self.mgr.load_bookings(data, self.guests, self.rooms)
        self.assertIsNotNone(self.mgr.get_booking_by_id(10))

    def test_load_skips_unknown_guest(self):
        start = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        end = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        data = [{
            "booking_id": 11,
            "guest_id": 99,  # non‑existing
            "room_number": 101,
            "check_in": start,
            "check_out": end,
        }]
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            self.mgr.load_bookings(data, self.guests, self.rooms)
        self.assertIn("Guest with ID 99 not found", captured.getvalue())
        self.assertIsNone(self.mgr.get_booking_by_id(11))

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def test_query_by_guest(self):
        self.mgr.add_booking(self.sample)
        self.assertEqual(len(self.mgr.get_bookings_by_guest_id(1)), 1)

    def test_query_by_room(self):
        self.mgr.add_booking(self.sample)
        self.assertEqual(len(self.mgr.get_bookings_by_room_id(101)), 1)

    # ------------------------------------------------------------------
    # Cancel / remove
    # ------------------------------------------------------------------
    def test_cancel_booking(self):
        self.mgr.add_booking(self.sample)
        self.mgr.cancel_booking(self.sample.booking_id)
        self.assertIsNone(self.mgr.get_booking_by_id(self.sample.booking_id))

    def test_remove_booking(self):
        self.mgr.add_booking(self.sample)
        self.assertTrue(self.mgr.remove_booking(self.sample.booking_id))
        self.assertIsNone(self.mgr.get_booking_by_id(self.sample.booking_id))

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------
    def test_to_dict_contains_id(self):
        self.mgr.add_booking(self.sample)
        serialised = self.mgr.to_dict()
        self.assertEqual(serialised[0]["booking_id"], self.sample.booking_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
