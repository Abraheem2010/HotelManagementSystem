"""Unit tests for GuestService using in‑memory stubs only."""

import importlib.util
import os
import sys
from pathlib import Path
import unittest


# ---------------------------------------------------------------------
#  Dynamically import guest_service.py from parent directories
# ---------------------------------------------------------------------


def _load_guest_service():
    here = Path(__file__).resolve()
    for ancestor in [here.parent] + list(here.parents)[:5]:
        for root, _dirs, files in os.walk(ancestor):
            if "guest_service.py" in files:
                fp = Path(root) / "guest_service.py"
                spec = importlib.util.spec_from_file_location("guest_service", fp)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore[arg-type]
                    sys.modules["guest_service"] = mod
                    return mod.GuestService  # type: ignore[attr-defined]
    raise ImportError("guest_service.py not found")


GuestService = _load_guest_service()


# ---------------------------------------------------------------------
#  Domain stubs
# ---------------------------------------------------------------------


class DummyGuest:
    def __init__(self, guest_id, name, contact, guest_type="regular"):
        self.guest_id = guest_id
        self.name = name
        self.contact = contact
        self.points = 0
        self._type = guest_type

    def get_guest_type(self):
        return self._type.capitalize()

    def update_guest(self, name=None, contact=None):
        if name:
            self.name = name
        if contact:
            self.contact = contact

    def __str__(self):
        return f"Guest {self.guest_id}: {self.name} ({self._type})"


class DummyMemberGuest(DummyGuest):
    def __init__(self, guest_id, name, contact):
        super().__init__(guest_id, name, contact, "member")


class _FactoryStub:
    @staticmethod
    def create_guest(guest_id, name, contact, guest_type="regular"):
        if guest_type.lower() == "member":
            return DummyMemberGuest(guest_id, name, contact)
        return DummyGuest(guest_id, name, contact, guest_type.lower())


import guest_service  # type: ignore  # noqa: E402

guest_service.UniversalEntityFactory = _FactoryStub  # type: ignore[attr-defined]
guest_service.MemberGuest = DummyMemberGuest  # type: ignore[attr-defined]


class DummyGuestManager:
    def __init__(self):
        self.guests = {}

    def add_guest(self, guest):
        self.guests[guest.guest_id] = guest

    def get_guest_by_id(self, guest_id):
        return self.guests.get(guest_id)

    def replace_guest(self, guest_id, new_guest):
        self.guests[guest_id] = new_guest

    def remove_guest(self, guest_id):
        return self.guests.pop(guest_id, None) is not None

    def get_all_guests(self):
        return list(self.guests.values())

    @staticmethod
    def to_dict():
        return []


class DummyGuestData:
    def __init__(self):
        self.saved = None

    def save(self, payload):
        self.saved = payload


# ---------------------------------------------------------------------
#  Unit tests
# ---------------------------------------------------------------------


class TestGuestService(unittest.TestCase):
    def setUp(self):
        self.gm = DummyGuestManager()
        self.data = DummyGuestData()
        self.service = GuestService(self.gm, self.data)

    def test_register_guest_success(self):
        msg = self.service.register_guest(1, "Alice", "050-111")
        self.assertIn("registered", msg.lower())
        self.assertIsNotNone(self.gm.get_guest_by_id(1))

    def test_register_existing_id(self):
        self.service.register_guest(1, "Alice", "050-111")
        msg = self.service.register_guest(1, "Bob", "050-222")
        self.assertIn("already", msg.lower())

    def test_update_guest_type(self):
        self.service.register_guest(2, "Bob", "050-222")
        msg = self.service.update_guest_type(2, "member")
        self.assertIn("updated", msg.lower())
        self.assertEqual(self.gm.get_guest_by_id(2).get_guest_type(), "Member")

    def test_view_guest_details_by_id(self):
        self.service.register_guest(3, "Carl", "050-333")
        res = self.service.view_guest_details("3")
        self.assertIn("Carl", res)

    def test_view_guest_details_by_name(self):
        self.service.register_guest(4, "Dana", "050-444")
        res = self.service.view_guest_details("dan")
        self.assertEqual(len(res), 1)

    def test_view_guests_empty(self):
        self.assertEqual(self.service.view_guests(), "No registered guests.")

    def test_view_guests_non_empty(self):
        self.service.register_guest(5, "Eve", "050-555")
        self.assertEqual(len(self.service.view_guests()), 1)

    def test_update_guest(self):
        self.service.register_guest(6, "Foo", "000")
        msg = self.service.update_guest(6, name="FooBar", contact="111")
        self.assertIn("updated", msg.lower())
        g = self.gm.get_guest_by_id(6)
        self.assertEqual((g.name, g.contact), ("FooBar", "111"))

    def test_remove_guest(self):
        self.service.register_guest(7, "Gina", "777")
        msg = self.service.remove_guest(7)
        self.assertIn("removed", msg.lower())
        self.assertIsNone(self.gm.get_guest_by_id(7))


if __name__ == "__main__":
    unittest.main(verbosity=2)
