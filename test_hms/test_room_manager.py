import unittest
from rooms.room_manager import RoomManager
from rooms.rooms import Room


class TestRoomManager(unittest.TestCase):
    def setUp(self):
        self.room_manager = RoomManager()
        self.test_room_data = [
            {"room_number": 101, "room_type": "single", "price": 100.0, "status": "available"},
            {"room_number": 102, "room_type": "double", "price": 150.0, "status": "occupied"},
            {"room_number": 103, "room_type": "suite", "price": 300.0, "status": "maintenance"},
        ]

    def test_room_manager_initialization(self):
        self.assertIsInstance(self.room_manager.rooms, list)
        self.assertEqual(len(self.room_manager.rooms), 0)

    def test_load_rooms_from_data(self):
        self.room_manager.load_rooms(self.test_room_data)
        self.assertEqual(len(self.room_manager.rooms), 3)
        r1, r2, r3 = self.room_manager.rooms
        self.assertEqual((r1.room_number, r1.room_type, r1.price, r1.status), (101, "single", 100.0, "available"))
        self.assertEqual((r2.room_number, r2.status), (102, "occupied"))
        self.assertEqual((r3.room_number, r3.room_type, r3.status), (103, "suite", "maintenance"))

    def test_load_rooms_empty_data(self):
        self.room_manager.load_rooms([])
        self.assertEqual(len(self.room_manager.rooms), 0)

    def test_load_rooms_replaces_existing(self):
        self.room_manager.load_rooms([{"room_number": 999, "room_type": "single", "price": 50.0, "status": "available"}])
        self.room_manager.load_rooms(self.test_room_data)
        self.assertEqual(len(self.room_manager.rooms), 3)
        self.assertIsNone(self.room_manager.get_room_by_id(999))
        self.assertIsNotNone(self.room_manager.get_room_by_id(101))

    def test_get_room_by_id_found(self):
        self.room_manager.load_rooms(self.test_room_data)
        room = self.room_manager.get_room_by_id(102)
        self.assertEqual((room.room_number, room.room_type, room.price), (102, "double", 150.0))

    def test_get_room_by_id_not_found(self):
        self.room_manager.load_rooms(self.test_room_data)
        self.assertIsNone(self.room_manager.get_room_by_id(999))

    def test_get_room_by_id_empty_manager(self):
        self.assertIsNone(self.room_manager.get_room_by_id(101))

    def test_add_room_success(self):
        room = Room(201, "deluxe", 250.0, "available")
        self.room_manager.add_room(room)
        self.assertEqual(len(self.room_manager.rooms), 1)
        self.assertEqual(self.room_manager.get_room_by_id(201), room)

    def test_add_room_multiple(self):
        for num, typ, price in [(201, "single", 100.0), (202, "double", 150.0), (203, "suite", 300.0)]:
            self.room_manager.add_room(Room(num, typ, price))
        self.assertEqual(len(self.room_manager.rooms), 3)
        self.assertIsNotNone(self.room_manager.get_room_by_id(203))

    def test_add_room_to_existing_collection(self):
        self.room_manager.load_rooms(self.test_room_data)
        self.room_manager.add_room(Room(104, "penthouse", 500.0))
        self.assertEqual(len(self.room_manager.rooms), 4)
        self.assertIsNotNone(self.room_manager.get_room_by_id(104))

    def test_get_all_rooms_empty(self):
        self.assertEqual(self.room_manager.get_all_rooms(), [])

    def test_get_all_rooms_with_data(self):
        self.room_manager.load_rooms(self.test_room_data)
        rooms = self.room_manager.get_all_rooms()
        self.assertEqual(len(rooms), 3)
        numbers = [r.room_number for r in rooms]
        self.assertIn(102, numbers)

    def test_get_all_rooms_returns_reference(self):
        self.room_manager.load_rooms(self.test_room_data)
        self.assertIs(self.room_manager.get_all_rooms(), self.room_manager.rooms)

    def test_get_available_rooms_none_available(self):
        data = [
            {"room_number": 101, "room_type": "single", "price": 100.0, "status": "occupied"},
            {"room_number": 102, "room_type": "double", "price": 150.0, "status": "maintenance"},
        ]
        self.room_manager.load_rooms(data)
        self.assertEqual(self.room_manager.get_available_rooms(), [])

    def test_get_available_rooms_some_available(self):
        self.room_manager.load_rooms(self.test_room_data)
        available = self.room_manager.get_available_rooms()
        self.assertEqual(len(available), 1)
        self.assertEqual((available[0].room_number, available[0].status), (101, "available"))

    def test_get_available_rooms_all_available(self):
        data = [
            {"room_number": 101, "room_type": "single", "price": 100.0, "status": "available"},
            {"room_number": 102, "room_type": "double", "price": 150.0, "status": "available"},
            {"room_number": 103, "room_type": "suite", "price": 300.0, "status": "available"},
        ]
        self.room_manager.load_rooms(data)
        self.assertEqual(len(self.room_manager.get_available_rooms()), 3)

    def test_remove_room_existing(self):
        self.room_manager.load_rooms(self.test_room_data)
        self.room_manager.remove_room(102)
        self.assertIsNone(self.room_manager.get_room_by_id(102))

    def test_remove_room_nonexistent(self):
        self.room_manager.load_rooms(self.test_room_data)
        before = len(self.room_manager.rooms)
        self.room_manager.remove_room(999)
        self.assertEqual(len(self.room_manager.rooms), before)

    def test_remove_room_from_empty_collection(self):
        self.room_manager.remove_room(101)
        self.assertEqual(len(self.room_manager.rooms), 0)

    def test_remove_all_rooms(self):
        self.room_manager.load_rooms(self.test_room_data)
        for num in [101, 102, 103]:
            self.room_manager.remove_room(num)
        self.assertEqual(self.room_manager.rooms, [])

    def test_to_dict_empty(self):
        self.assertEqual(self.room_manager.to_dict(), [])

    def test_to_dict_with_data(self):
        self.room_manager.load_rooms(self.test_room_data)
        result = self.room_manager.to_dict()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["room_number"], 101)

    def test_to_dict_data_integrity(self):
        self.room_manager.load_rooms(self.test_room_data)
        data = self.room_manager.to_dict()
        new_mgr = RoomManager()
        new_mgr.load_rooms(data)
        for orig, new in zip(self.room_manager.rooms, new_mgr.rooms):
            self.assertEqual((orig.room_number, orig.room_type, orig.price, orig.status), (new.room_number, new.room_type, new.price, new.status))


if __name__ == "__main__":
    unittest.main()
