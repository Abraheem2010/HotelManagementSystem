"""Booking domain object – unit tests

Covers constructor flexibility, serialization (`to_dict`), mutation helpers
(`update_booking`, `update_status`, `mark_as_paid`), night‑count calculation and
`__str__` output.  The tests rely on minimal in‑memory stubs for guest and room
objects.

Run via project root:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import datetime as _dt
import unittest

from bookings.bookings import Booking

# ---------------------------------------------------------------------------
# Simple stubs (guest, room) – only attributes accessed by Booking are needed
# ---------------------------------------------------------------------------

class _Guest:
    def __init__(self, gid: int, name: str) -> None:
        self.guest_id = gid
        self.name = name


class _Room:
    def __init__(self, rn: int) -> None:
        self.room_number = rn


class BookingTests(unittest.TestCase):
    """Happy‑path & edge‑case checks for `Booking`."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ci = _dt.date(2025, 5, 10)
        cls.co = _dt.date(2025, 5, 15)
        cls.ci_str, cls.co_str = "2025-05-10", "2025-05-15"

    def setUp(self) -> None:
        self.guest = _Guest(42, "Test Guest")
        self.room = _Room(7)

    # ---------------- constructor ----------------
    def test_init_accepts_date_or_str(self):
        b1 = Booking(1, self.guest, self.room, self.ci, self.co,
                     status="confirmed", paid=False, installments=3)
        self.assertEqual(b1.check_in, self.ci)
        self.assertEqual(b1.installments, 3)

        b2 = Booking(2, self.guest, self.room, self.ci_str, self.co_str)
        self.assertEqual(b2.check_in, self.ci)

    # ---------------- serialization -------------
    def test_to_dict_roundtrip(self):
        b = Booking(5, self.guest, self.room, self.ci_str, self.co_str,
                     status="checked-in", paid=True, installments=2)
        d = b.to_dict()
        self.assertEqual(d["check_in"], self.ci_str)
        self.assertEqual(d["installments"], 2)

    # ---------------- update helpers ------------
    def test_update_booking_and_status(self):
        b = Booking(3, self.guest, self.room, self.ci_str, self.co_str)
        new_room = _Room(99)
        b.update_booking(check_in="2025-06-01", room=new_room)
        self.assertEqual(b.check_in, _dt.date(2025, 6, 1))
        self.assertIs(b.room, new_room)

        self.assertTrue(b.update_status("checked-in"))
        self.assertFalse(b.update_status("invalid"))
        self.assertEqual(b.status, "checked-in")

    # ---------------- payments & nights ---------
    def test_mark_paid_and_calculate_nights(self):
        b = Booking(6, self.guest, self.room, self.ci_str, self.co_str)
        b.mark_as_paid(True)
        self.assertTrue(b.paid)
        self.assertEqual(b.calculate_nights(), 5)

    # ---------------- str output ---------------
    def test_str_contains_key_details(self):
        b = Booking(8, self.guest, self.room, self.ci_str, self.co_str,
                     status="cancelled", paid=True, installments=4)
        s = str(b)
        self.assertIn("Booking 8", s)
        self.assertIn("Room 7", s)
        self.assertIn("Guest Test Guest", s)
        self.assertIn("Paid: Yes", s)


if __name__ == "__main__":
    unittest.main()
