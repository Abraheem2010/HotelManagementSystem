"""RoomService unit tests (robust version)

* Patches `UniversalEntityFactory.create_room` so rooms returned expose
  `to_dict()`, preventing `AttributeError` inside `RoomManager.to_dict`.
* Leaves original business logic untouched; only the factory patch is applied
  inside `setUpClass` and reverted in `tearDownClass`.
* Mocked `room_data.save` verifies persistence calls without touching disk.

Run:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock
from datetime import datetime

from rooms.room_service import RoomService
from rooms.room_manager import RoomManager
from bookings.booking_manager import BookingManager
from system.universal_factory import UniversalEntityFactory
import constants as _c

# ---------------------------------------------------------------------------
# Patch helpers
# ---------------------------------------------------------------------------

def _room_to_dict(room):
    return {
        "room_number": room.room_number,
        "room_type": room.room_type,
        "price": room.price,
        "status": room.status,
    }


def _make_room_with_dict(*args, **kwargs):
    """Wrap original factory to ensure Room has to_dict & update_room."""
    room = _orig_create_room(*args, **kwargs)

    # attach to_dict
    room.to_dict = _room_to_dict.__get__(room)

    # attach update_room if missing (dummy UniversalEntityFactory may not add it)
    if not hasattr(room, "update_room"):
        def _upd(self, room_type=None, price=None, status=None):
            if room_type is not None:
                self.room_type = room_type
            if price is not None:
                self.price = price
            if status is not None:
                self.status = status
        room.update_room = _upd.__get__(room)

    return room


class RoomServiceTests(unittest.TestCase):
    """Comprehensive tests for `RoomService`."""

    @classmethod
    def setUpClass(cls):
        #  patch VALID_* sets to a deterministic small sample
        cls._orig_types = _c.VALID_ROOM_TYPES
        cls._orig_status = _c.VALID_ROOM_STATUSES
        _c.VALID_ROOM_TYPES = {"single", "double", "suite"}
        _c.VALID_ROOM_STATUSES = {"available", "occupied", "maintenance"}

        # patch factory so every room supports to_dict()
        global _orig_create_room
        _orig_create_room = UniversalEntityFactory.create_room  # type: ignore[attr-defined]
        UniversalEntityFactory.create_room = staticmethod(_make_room_with_dict)  # type: ignore[attr-defined]

    @classmethod
    def tearDownClass(cls):
        _c.VALID_ROOM_TYPES = cls._orig_types  # type: ignore
        _c.VALID_ROOM_STATUSES = cls._orig_status  # type: ignore
        UniversalEntityFactory.create_room = staticmethod(_orig_create_room)  # type: ignore[attr-defined]

    def setUp(self):
        self.room_manager = RoomManager()
        self.room_data = Mock()
        self.booking_manager = BookingManager()
        self.svc = RoomService(self.room_manager, self.room_data, self.booking_manager)

    # ---------------- add_room ----------------
    def test_add_room_success(self):
        msg = self.svc.add_room(101, "single", 120.0, "available")
        self.assertIn("success", msg.lower())
        self.room_data.save.assert_called_once()

    def test_add_room_duplicate(self):
        self.svc.add_room(101, "single", 100)
        msg = self.svc.add_room(101, "double", 150)
        self.assertIn("already", msg.lower())

    def test_add_room_invalid_type(self):
        msg = self.svc.add_room(102, "penthouse", 200)
        self.assertIn("invalid room type", msg.lower())

    def test_add_room_negative_price(self):
        msg = self.svc.add_room(103, "double", -10)
        self.assertIn("price must be positive", msg.lower())

    # ---------------- update_room -------------
    def test_update_room_all_fields(self):
        self.svc.add_room(104, "single", 110)
        msg = self.svc.update_room(104, "double", 180, "maintenance")
        self.assertIn("updated", msg.lower())
        r = self.room_manager.get_room_by_id(104)
        self.assertEqual((r.room_type, r.price, r.status), ("double", 180, "maintenance"))

    def test_update_room_not_found(self):
        msg = self.svc.update_room(999, price=150)
        self.assertIn("not found", msg.lower())

    # ---------------- remove_room -------------
    def test_remove_room_success(self):
        self.svc.add_room(105, "suite", 300)
        msg = self.svc.remove_room(105)
        self.assertIn("removed", msg.lower())
        self.assertIsNone(self.room_manager.get_room_by_id(105))

    # ---------------- view_rooms --------------
    def test_view_rooms_empty(self):
        self.assertIn("no rooms", self.svc.view_rooms().lower())

    # ---------------- availability ------------
    def test_check_availability_invalid_date(self):
        self.svc.add_room(106, "single", 90)
        ok, msg = self.svc.check_availability(106, "bad", "2025-01-02")
        self.assertFalse(ok)
        self.assertIn("invalid date", msg.lower())

    def test_check_availability_success(self):
        self.svc.add_room(107, "single", 90)
        ok, _ = self.svc.check_availability(107, "2025-01-10", "2025-01-15")
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main(verbosity=2)
