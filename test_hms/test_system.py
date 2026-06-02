from unittest import TestCase, mock


class DummyDataManager:
    """Minimal in‑memory replacement for JSON‑backed DataManager."""

    def __init__(self, filename):
        self.filename = filename
        self._data = None

    def load(self):
        return []

    def save(self, data):
        self._data = data


class TestHotelManagementSystem(TestCase):
    @mock.patch("system.system.DataManager", new=DummyDataManager)
    def setUp(self):
        from system.system import HotelManagementSystem

        self.HMSClass = HotelManagementSystem  # keep reference for reuse
        self.hms = self.HMSClass()

    # ------------------------ IDs ------------------------ #
    def test_initial_ids(self):
        self.assertEqual((self.hms.next_guest_id, self.hms.next_booking_id), (1, 1))

    # --------------------- services ---------------------- #
    def test_services_instantiated(self):
        for attr in ("room_service", "guest_service", "booking_service", "report_service"):
            self.assertTrue(hasattr(self.hms, attr))

    # ------------------- persistence -------------------- #
    @mock.patch("system.system.DataManager", new=DummyDataManager)
    def test_save_all_empty(self):
        hms = self.HMSClass()  # fresh instance so patch applies
        hms.save_all()
        self.assertEqual((hms.room_data._data, hms.guest_data._data, hms.booking_data._data), ([], [], []))

    # ------------------- next IDs ---------------------- #
    @mock.patch("system.system.DataManager", new=DummyDataManager)
    def test_next_ids_after_entities(self):
        hms = self.HMSClass()

        class _G:  # simple stub
            def __init__(self, guest_id):
                self.guest_id = guest_id

        class _B:
            def __init__(self, booking_id):
                self.booking_id = booking_id

        hms.guest_manager.guests.append(_G(5))
        hms.booking_manager.bookings.append(_B(8))

        self.assertEqual(hms._get_next_guest_id(), 6)
        self.assertEqual(hms._get_next_booking_id(), 9)


if __name__ == "__main__":
    import unittest

    unittest.main()
