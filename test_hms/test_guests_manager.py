"""test_guest_manager.py
=====================
Unit tests for **GuestManager** (the file you uploaded).

Run:
    python -m unittest test_guest_manager.py -v
"""

import unittest

# Adjust import to real package path if needed
from guests.guest_manager import GuestManager  # noqa: F401
from guests.guests import Guest, VIPGuest, MemberGuest  # noqa: F401


class TestGuestManager(unittest.TestCase):
    def setUp(self):
        # Ensure singleton instance is clean before each test
        self.gm = GuestManager()
        self.gm.guests = []

    def _sample_data(self):
        return [
            {"guest_id": 1, "name": "Alice", "contact": "050-111", "guest_type": "regular"},
            {"guest_id": 2, "name": "Bob", "contact": "050-222", "guest_type": "member", "points": 10},
            {"guest_id": 3, "name": "Vera", "contact": "050-333", "guest_type": "vip"},
        ]

    # --- singleton behaviour ---
    def test_singleton(self):
        gm2 = GuestManager()
        self.assertIs(self.gm, gm2)

    # --- load_guests ---
    def test_load_guests_creates_correct_types(self):
        self.gm.load_guests(self._sample_data())
        types = [type(g).__name__ for g in self.gm.get_all_guests()]
        self.assertEqual(types, ["Guest", "MemberGuest", "VIPGuest"])

    # --- add_guest ---
    def test_add_guest_success(self):
        guest = Guest(10, "Carl", "000")
        self.gm.add_guest(guest)
        self.assertIn(guest, self.gm.get_all_guests())

    def test_add_guest_duplicate_id_raises(self):
        self.gm.add_guest(Guest(1, "Alice", "050"))
        with self.assertRaises(ValueError):
            self.gm.add_guest(Guest(1, "Clone", "051"))

    # --- get_guest_by_id ---
    def test_get_guest_by_id_found(self):
        self.gm.load_guests(self._sample_data())
        guest = self.gm.get_guest_by_id(2)
        self.assertIsNotNone(guest)
        self.assertEqual(guest.name, "Bob")

    def test_get_guest_by_id_not_found(self):
        self.assertIsNone(self.gm.get_guest_by_id(999))

    # --- replace_guest ---
    def test_replace_guest_success(self):
        self.gm.add_guest(Guest(5, "Old", "123"))
        replaced = self.gm.replace_guest(5, VIPGuest(5, "New", "123"))
        self.assertTrue(replaced)
        self.assertIsInstance(self.gm.get_guest_by_id(5), VIPGuest)

    # --- remove_guest ---
    def test_remove_guest(self):
        self.gm.load_guests(self._sample_data())
        removed = self.gm.remove_guest(1)
        self.assertTrue(removed)
        self.assertIsNone(self.gm.get_guest_by_id(1))

    # --- to_dict ---
    def test_to_dict_returns_list(self):
        self.gm.load_guests(self._sample_data())
        data = self.gm.to_dict()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
