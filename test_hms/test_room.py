from rooms.rooms import Room
import unittest


class TestRoom(unittest.TestCase):
    def setUp(self):
        self.room = Room(101, "single", 100.0, "available")

    # --------------------- constructor --------------------- #
    def test_room_creation(self):
        self.assertEqual(
            (self.room.room_number, self.room.room_type, self.room.price, self.room.status),
            (101, "single", 100.0, "available"),
        )

    def test_room_creation_default_status(self):
        self.assertEqual(Room(102, "double", 150.0).status, "available")

    # -------------------- serialization -------------------- #
    def test_room_to_dict(self):
        self.assertEqual(
            self.room.to_dict(),
            {"room_number": 101, "room_type": "single", "price": 100.0, "status": "available"},
        )

    def test_room_str_representation(self):
        self.assertEqual(
            str(self.room),
            "Room 101: room_type: single, price: 100.0, status: available",
        )

    # --------------------- update API --------------------- #
    def test_update_room_all_fields(self):
        self.room.update_room("double", 150.0, "maintenance")
        self.assertEqual((self.room.room_type, self.room.price, self.room.status), ("double", 150.0, "maintenance"))

    def test_update_room_partial_type_only(self):
        self.room.update_room(room_type="suite")
        self.assertEqual((self.room.room_type, self.room.price, self.room.status), ("suite", 100.0, "available"))

    def test_update_room_partial_price_only(self):
        self.room.update_room(price=200.0)
        self.assertEqual((self.room.room_type, self.room.price, self.room.status), ("single", 200.0, "available"))

    def test_update_room_partial_status_only(self):
        self.room.update_room(status="occupied")
        self.assertEqual((self.room.room_type, self.room.price, self.room.status), ("single", 100.0, "occupied"))

    def test_update_room_negative_price_raises_error(self):
        with self.assertRaises(ValueError):
            self.room.update_room(price=-50.0)

    def test_update_room_zero_price_raises_error(self):
        with self.assertRaises(ValueError):
            self.room.update_room(price=0.0)

    def test_update_room_none_values_ignored(self):
        self.room.update_room(None, None, None)
        self.assertEqual((self.room.room_type, self.room.price, self.room.status), ("single", 100.0, "available"))

    # -------------------- price decimals ------------------ #
    def test_room_price_decimal(self):
        self.assertEqual(Room(103, "suite", 299.99, "available").price, 299.99)

    def test_update_room_decimal_price(self):
        self.room.update_room(price=123.45)
        self.assertEqual(self.room.price, 123.45)


if __name__ == "__main__":
    unittest.main()
