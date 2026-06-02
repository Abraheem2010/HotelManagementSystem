import unittest
import datetime
import importlib
import importlib.util
import os
import sys
from pathlib import Path

# ----------------- load UniversalEntityFactory ----------------- #
_candidates = [
    "hms.services.universal_entity_factory",
    "services.universal_entity_factory",
    "factories.universal_entity_factory",
    "system.universal_factory",
    "universal_factory",
]
UniversalEntityFactory = None
for _mod_name in _candidates:
    try:
        UniversalEntityFactory = importlib.import_module(_mod_name).UniversalEntityFactory
        break
    except (ModuleNotFoundError, AttributeError):
        pass

if UniversalEntityFactory is None:
    _here = Path(__file__).resolve()
    for _ancestor in [_here.parent] + list(_here.parents)[:5]:
        for _root, _dirs, _files in os.walk(_ancestor):
            if "universal_factory.py" in _files:
                _path = Path(_root) / "universal_factory.py"
                _spec = importlib.util.spec_from_file_location("universal_factory", _path)
                _mod = importlib.util.module_from_spec(_spec)
                _spec.loader.exec_module(_mod)  # type: ignore
                UniversalEntityFactory = _mod.UniversalEntityFactory  # type: ignore
                break
        if UniversalEntityFactory:
            break
    if UniversalEntityFactory is None:
        raise ImportError("universal_factory.py not found")

# --------------------------- stubs ---------------------------- #
class DummyGuest:
    def __init__(self, guest_id, name, contact):
        self.guest_id = guest_id
        self.name = name
        self.contact = contact
        self.status = "regular"


class DummyMemberGuest(DummyGuest):
    def __init__(self, guest_id, name, contact, points=0):
        super().__init__(guest_id, name, contact)
        self.points = points
        self.status = "member"


class DummyVIPGuest(DummyGuest):
    def __init__(self, guest_id, name, contact):
        super().__init__(guest_id, name, contact)
        self.status = "vip"


class DummyRoom:
    def __init__(self, room_number, room_type, price, status="available"):
        self.room_number = room_number
        self.room_type = room_type
        self.price = price
        self.status = status


class DummyBooking:
    def __init__(self, booking_id, guest, room, check_in, check_out, status="confirmed", installments=1):
        self.booking_id = booking_id
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.status = status
        self.installments = installments


class DummyVIPStrategy: ...
class DummyMemberStrategy: ...
class DummyRegularStrategy: ...

_mod = sys.modules[UniversalEntityFactory.__module__]

# Names in the factory module that we temporarily replace with dummy classes.
_PATCHED = {
    "VIPGuest": DummyVIPGuest,
    "MemberGuest": DummyMemberGuest,
    "RegularGuest": DummyGuest,
    "Room": DummyRoom,
    "Booking": DummyBooking,
    "VIPGuestServiceStrategy": DummyVIPStrategy,
    "MemberGuestServiceStrategy": DummyMemberStrategy,
    "RegularGuestServiceStrategy": DummyRegularStrategy,
}
# Capture the originals so we can restore them and avoid leaking dummy classes
# into the shared module, which would contaminate other test modules.
_ORIGINALS = {name: getattr(_mod, name, None) for name in _PATCHED}


def setUpModule():
    for name, dummy in _PATCHED.items():
        setattr(_mod, name, dummy)


def tearDownModule():
    for name, original in _ORIGINALS.items():
        if original is not None:
            setattr(_mod, name, original)


Factory = UniversalEntityFactory

# --------------------------- tests --------------------------- #
class TestUniversalEntityFactory(unittest.TestCase):
    def test_create_guest_regular(self):
        self.assertEqual(Factory.create_guest(1, "Alice", "000").status, "regular")

    def test_create_guest_member_points(self):
        g = Factory.create_guest(2, "Bob", "111", "member", points=50)
        self.assertEqual((type(g).__name__, g.points), ("DummyMemberGuest", 50))

    def test_create_guest_vip(self):
        self.assertEqual(Factory.create_guest(3, "Vera", "222", "vip").status, "vip")

    def test_create_room(self):
        r = Factory.create_room(101, "suite", 300.0)
        self.assertEqual((r.room_number, r.room_type, r.price), (101, "suite", 300.0))

    def test_create_booking_with_string_dates(self):
        guest = DummyGuest(1, "Alice", "000")
        room = DummyRoom(101, "suite", 300)
        b = Factory.create_booking(10, guest, room, "2025-01-01", "2025-01-03")
        self.assertEqual((type(b.check_in), (b.check_out - b.check_in).days), (datetime.date, 2))

    def test_create_strategy_vip(self):
        self.assertIsInstance(Factory.create_guest_service_strategy(DummyVIPGuest(5, "Vip", "999")), DummyVIPStrategy)

    def test_create_strategy_member(self):
        self.assertIsInstance(Factory.create_guest_service_strategy(DummyMemberGuest(6, "Mem", "888")), DummyMemberStrategy)

    def test_create_strategy_regular(self):
        self.assertIsInstance(Factory.create_guest_service_strategy(DummyGuest(7, "Reg", "777")), DummyRegularStrategy)


if __name__ == "__main__":
    unittest.main()
