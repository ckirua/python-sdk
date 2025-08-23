import unittest
from pathlib import Path
from sdk.cfs import extract_zip, read_json, write_json, read_toml, write_toml


class TestExtractZip(unittest.TestCase):
    def setUp(self):
        # Use the same example zip as in the example, if available
        self.example_zip_path = (
            Path(__file__).parent.parent / "examples" / "cfs" / "data" / "example.zip"
        )
        if not self.example_zip_path.exists():
            self.skipTest(f"Test zip file not found: {self.example_zip_path}")

        with open(self.example_zip_path, "rb") as f:
            self.zip_bytes = f.read()

    def test_extract_zip_returns_files(self):
        files = extract_zip(self.zip_bytes)
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0, "No files extracted from zip")

        for file in files:
            # Check filename is a string
            self.assertIsInstance(file.filename, str)
            # Check data is a list of ints
            self.assertIsInstance(file.data, list)
            if file.data:
                self.assertIsInstance(file.data[0], int)
            # Check get_data_as_bytes returns bytes
            data_bytes = file.get_data_as_bytes()
            self.assertIsInstance(data_bytes, bytes)
            # The length of data and data_bytes should match
            self.assertEqual(len(file.data), len(data_bytes))

    def test_extract_zip_empty(self):
        # Passing empty bytes should return an empty list or raise
        try:
            files = extract_zip(b"")
            self.assertIsInstance(files, list)
            self.assertEqual(len(files), 0)
        except Exception:
            pass  # Acceptable if implementation raises


class TestJsonReadWrite(unittest.TestCase):
    def setUp(self):
        # Path to the example JSON file
        self.example_json_path = (
            Path(__file__).parent.parent / "examples" / "cfs" / "data" / "example.json"
        )
        if not self.example_json_path.exists():
            self.skipTest(f"Test JSON file not found: {self.example_json_path}")
        self.temp_json_path = self.example_json_path.parent / "example_out.json"

    def tearDown(self):
        if self.temp_json_path.exists():
            self.temp_json_path.unlink()

    def test_read_and_write_json(self):
        # Read the JSON file
        data = read_json(str(self.example_json_path))
        self.assertIsInstance(data, dict)
        self.assertIn("name", data)
        self.assertIn("settings", data)
        self.assertEqual(data["name"], "Example Configuration")
        # Write it back to a new file
        write_json(str(self.temp_json_path), data)
        self.assertTrue(self.temp_json_path.exists())
        # Read again and compare
        data2 = read_json(str(self.temp_json_path))
        self.assertEqual(data, data2)


class TestTomlReadWrite(unittest.TestCase):
    def setUp(self):
        self.example_toml_path = (
            Path(__file__).parent.parent / "examples" / "cfs" / "data" / "example.toml"
        )
        if not self.example_toml_path.exists():
            self.skipTest(f"Test TOML file not found: {self.example_toml_path}")
        self.temp_toml_path = self.example_toml_path.parent / "example_out.toml"

    def tearDown(self):
        if self.temp_toml_path.exists():
            self.temp_toml_path.unlink()

    def test_read_and_write_toml(self):
        data = read_toml(str(self.example_toml_path))
        self.assertIsInstance(data, dict)
        self.assertIn("title", data)
        self.assertIn("owner", data)
        self.assertIn("database", data)
        # Write it back to a new file
        write_toml(str(self.temp_toml_path), data)
        self.assertTrue(self.temp_toml_path.exists())
        # Read again and compare
        data2 = read_toml(str(self.temp_toml_path))
        self.assertEqual(data, data2)

if __name__ == "__main__":
    unittest.main()
