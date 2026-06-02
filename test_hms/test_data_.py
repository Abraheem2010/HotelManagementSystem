"""Unit tests for the DataManager utility class.
Runs entirely on a temporary JSON file so no real data is harmed.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

from utils.data_manager import DataManager


class TestDataManager(unittest.TestCase):
    """Happy-path and regular usage tests."""

    def setUp(self):
        # Use a real temporary file as target storage
        self.tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        self.filename = self.tmp.name
        self.tmp.close()
        self.dm = DataManager(self.filename)
        self.sample = [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
        ]

    def tearDown(self):
        if os.path.exists(self.filename):
            os.unlink(self.filename)

    # --------------- save / load basic --------------- #

    def test_init_stores_filename(self):
        self.assertEqual(DataManager("test.json").filename, "test.json")

    def test_save_creates_file_with_correct_content(self):
        self.dm.save(self.sample)
        self.assertTrue(os.path.exists(self.filename))
        with open(self.filename, "r", encoding="utf-8") as fh:
            self.assertEqual(json.load(fh), self.sample)

    def test_save_overwrites_existing_file(self):
        self.dm.save([{"id": 0}])
        self.dm.save(self.sample)
        with open(self.filename, "r", encoding="utf-8") as fh:
            self.assertEqual(json.load(fh), self.sample)

    def test_save_empty_list(self):
        self.dm.save([])
        with open(self.filename, "r", encoding="utf-8") as fh:
            self.assertEqual(json.load(fh), [])

    # --------------- complex / large payloads --------------- #

    def test_save_complex_nested_data(self):
        complex_payload = [{
            "id": 1,
            "nested": {
                "list": [1, 2, 3],
                "dict": {"k": "v"},
                "bool": True,
                "none": None,
            },
        }]
        self.dm.save(complex_payload)
        with open(self.filename, "r", encoding="utf-8") as fh:
            self.assertEqual(json.load(fh), complex_payload)

    def test_large_dataset(self):
        big = [{"id": i, "data": f"item_{i}"} for i in range(1_000)]
        self.dm.save(big)
        self.assertEqual(len(self.dm.load()), 1_000)

    # --------------- load variants --------------- #

    def test_load_returns_saved_data(self):
        self.dm.save(self.sample)
        self.assertEqual(self.dm.load(), self.sample)

    def test_load_nonexistent_returns_empty_list(self):
        self.assertEqual(DataManager("nouser.json").load(), [])

    def test_load_empty_file_returns_empty_list(self):
        with open(self.filename, "w", encoding="utf-8") as fh:
            json.dump([], fh)
        self.assertEqual(self.dm.load(), [])

    @patch("builtins.open", mock_open(read_data="invalid json"))
    def test_load_corrupted_file(self):
        self.assertEqual(self.dm.load(), [])

    @patch("builtins.open", mock_open(read_data="{\"invalid\": \"not a list\"}"))
    def test_load_valid_json_wrong_shape(self):
        self.assertEqual(self.dm.load(), {"invalid": "not a list"})

    # --------------- edge cases --------------- #

    def test_save_json_indent_formatting(self):
        self.dm.save(self.sample)
        with open(self.filename, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("\n", content)
        self.assertIn("    ", content)  # 4-space indent

    def test_unicode_characters_roundtrip(self):
        data = [
            {"name": "Software", "description": "Hotel management system"},
            {"emoji": "🏨", "special": "café naïve résumé"},
        ]
        self.dm.save(data)
        self.assertEqual(self.dm.load(), data)

    def test_permission_error_on_save(self):
        dm = DataManager("dummy.json")
        with patch("builtins.open", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                dm.save(self.sample)

    def test_empty_filename_behaviour(self):
        dm = DataManager("")
        self.assertEqual(dm.filename, "")
        with self.assertRaises((FileNotFoundError, OSError)):
            dm.save([])

    def test_none_filename_raises(self):
        with self.assertRaises(TypeError):
            DataManager(None)  # type: ignore

    def test_non_serialisable_objects_raise(self):
        dm = DataManager("test.json")
        bad = [
            {"func": lambda x: x},
            {"set": {1, 2}},
            {"dt": datetime.utcnow()},
        ]
        for obj in bad:
            with self.subTest(obj=obj):
                with self.assertRaises(TypeError):
                    dm.save(obj)

    def test_concurrent_write_last_write_wins(self):
        tmp2 = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        fname = tmp2.name
        tmp2.close()
        try:
            dm1, dm2 = DataManager(fname), DataManager(fname)
            dm1.save([{"source": "dm1"}])
            dm2.save([{"source": "dm2"}])
            self.assertEqual(dm1.load(), [{"source": "dm2"}])
        finally:
            if os.path.exists(fname):
                os.unlink(fname)


if __name__ == "__main__":
    unittest.main(verbosity=2)
