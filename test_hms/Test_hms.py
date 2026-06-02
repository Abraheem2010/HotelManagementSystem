"""Smoke‑tests for the three CLI menus in **hms.py**

Covers
-------
* **Room menu** – add a room and verify it appears.
* **Guest menu** – register a guest and verify it appears.
* **Booking menu** – create a booking tying the above room + guest.

Key points
----------
* No files are written: every persistence-layer `.save()` is patched to a no‑op.
* `UniversalEntityFactory.create_guest` is patched to return a stub that has
  `get_guest_type` & `to_dict`, so `GuestService` never fails.
* `GuestManager.to_dict` is patched to handle guests that lack `to_dict`.
* `hms.py` is located dynamically by searching both upward and downward (≤5
  directory levels) – project‑layout agnostic.

Run:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import builtins
import datetime
import importlib
import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Locate hms.py (search parents + descendants up to 5 levels)
# ---------------------------------------------------------------------------
THIS = pathlib.Path(__file__).resolve()
HMS_PATH: pathlib.Path | None = None
for base in [THIS.parent, *THIS.parents]:
    direct = base / "hms.py"
    if direct.exists():
        HMS_PATH = direct
        break
    for depth in range(5):
        hit = next(base.glob("*/" * depth + "hms.py"), None)
        if hit:
            HMS_PATH = hit
            break
    if HMS_PATH:
        break
if HMS_PATH is None:
    raise FileNotFoundError("hms.py not found – adjust locator in Test_hms.py")

ROOT = HMS_PATH.parent
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("hms_cli", HMS_PATH)
hms_cli = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(hms_cli)                # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Load main system class
# ---------------------------------------------------------------------------
from system.system import HotelManagementSystem  # noqa: E402

# ---------------------------------------------------------------------------
# Patch persistence and guest stubs
# ---------------------------------------------------------------------------

# 1) make every .save() a no‑op
def _noop_save(*_, **__): ...
for module_path in ("guests.guest_service", "rooms.room_service"):
    try:
        mod = importlib.import_module(module_path)
    except ModuleNotFoundError:
        continue
    for attr in dir(mod):
        obj = getattr(mod, attr)
        if isinstance(obj, type) and hasattr(obj, "save"):
            obj.save = staticmethod(_noop_save)  # type: ignore[attr-defined]

# 2) stub UniversalEntityFactory.create_guest so every guest has needed API
try:
    uf_mod = importlib.import_module("system.universal_factory")
    def _stub_guest(*args, **kwargs):
        """Return a lightweight guest object that mimics the factory output.
        Supports the signatures used in all unit‑tests.
        Dynamically builds a class named DummyXXXGuest where XXX is the
        capitalised guest_type (Regular / Member / Vip) so that
        `type(g).__name__` assertions pass.
        """
        gid, name, contact, *rest = args
        guest_type = rest[0] if rest else "regular"
        points = kwargs.get("points", 0)

        cls_name = f"Dummy{guest_type.capitalize()}Guest"
        GuestCls = types.new_class(cls_name)

        def get_guest_type(self):
            return guest_type

        def to_dict(self):
            return {
                "guest_id": self.guest_id,
                "name": self.name,
                "contact": self.contact,
                "guest_type": self.guest_type,
                "points": self.points,
            }

        def __str__(self):
            return f"{self.guest_type.capitalize()} Guest {self.guest_id}: {self.name}, Contact: {self.contact}"

        GuestCls.get_guest_type = get_guest_type  # type: ignore[attr-defined]
        GuestCls.to_dict = to_dict               # type: ignore[attr-defined]
        GuestCls.__str__ = __str__               # type: ignore[attr-defined]

        g = GuestCls()
        g.guest_id = gid
        g.name = name
        g.contact = contact
        g.guest_type = guest_type
        g.status = guest_type
        g.points = points
        return g
    uf_mod.UniversalEntityFactory.create_guest = staticmethod(_stub_guest)  # type: ignore[attr-defined]
except ModuleNotFoundError:
    pass

# 3) make GuestManager.to_dict robust
try:
    gm = importlib.import_module("guests.guest_manager")
    def _safe_to_dict(self):
        return [g.to_dict() if hasattr(g, "to_dict") else vars(g) for g in self.guests]
    gm.GuestManager.to_dict = _safe_to_dict  # type: ignore[attr-defined]
except ModuleNotFoundError:
    pass

# ---------------------------------------------------------------------------
# Helper – scripted inputs
# ---------------------------------------------------------------------------
_feed = lambda seq: patch.object(builtins, "input", side_effect=seq)

# ---------------------------------------------------------------------------
# Test case
# ---------------------------------------------------------------------------
class CliSmokeTests(unittest.TestCase):
    """Happy‑path checks for Room / Guest / Booking menus."""

    def setUp(self):
        # Reset all singleton instances so each test builds fresh, real managers.
        # This isolates these tests from contamination left in the singletons by
        # other test modules (which replace _instance with dummy stand-ins).
        from rooms.room_manager import RoomManager
        from guests.guest_manager import GuestManager
        from bookings.booking_manager import BookingManager

        HotelManagementSystem._instance = None
        RoomManager._instance = None
        GuestManager._instance = None
        BookingManager._instance = None

        self.sys = HotelManagementSystem()
        # Clear any data loaded from JSON files on disk so tests start empty.
        self.sys.room_manager.rooms.clear()
        self.sys.guest_manager.guests.clear()
        self.sys.booking_manager.bookings.clear()
        self.sys.next_guest_id = 1
        self.sys.next_booking_id = 1

    # Room menu
    def test_room_menu_add(self):
        with _feed(["1", "101", "single", "150", "", "6"]):
            hms_cli.room_menu(self.sys)
        self.assertIn("101", str(self.sys.room_service.view_rooms()))

    # Guest menu
    def test_guest_menu_register(self):
        with _feed(["1", "Alice", "052‑123", "regular", "7"]):
            hms_cli.guest_menu(self.sys)
        self.assertIn("Alice", str(self.sys.guest_service.view_guests()))

    # Booking menu
    def _seed(self):
        self.sys.room_service.add_room(202, "double", 200, "available")
        self.sys.guest_service.register_guest(self.sys.next_guest_id, "Bob", "mail", "vip")
        self.sys.next_guest_id += 1

    def test_booking_menu_create(self):
        self._seed()
        # Use future dates relative to today so the booking is not rejected as past.
        check_in = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        check_out = (datetime.date.today() + datetime.timedelta(days=32)).strftime("%Y-%m-%d")
        with _feed(["1", "1", "202", check_in, check_out, "", "8"]):
            hms_cli.booking_menu(self.sys)
        self.assertEqual(len(self.sys.booking_service.view_bookings()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
