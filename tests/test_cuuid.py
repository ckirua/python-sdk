import unittest

from sdk.cuuid import UUID, randstr_16, uuid4


class TestUUID(unittest.TestCase):
    def setUp(self):
        self.uuid_str = "12345678-1234-5678-1234-567812345678"
        self.uuid = UUID(self.uuid_str)

    def test_init(self):
        self.assertEqual(str(self.uuid), self.uuid_str)

    def test_hex(self):
        self.assertEqual(self.uuid.hex, self.uuid_str.replace("-", ""))

    def test_int(self):
        expected_int = int(self.uuid_str.replace("-", ""), 16)
        self.assertEqual(self.uuid.int, expected_int)

    def test_equality(self):
        uuid_same = UUID(self.uuid_str)
        uuid_different = UUID("87654321-4321-8765-4321-876543218765")
        self.assertTrue(self.uuid == uuid_same)
        self.assertFalse(self.uuid == uuid_different)

    def test_inequality(self):
        uuid_different = UUID("87654321-4321-8765-4321-876543218765")
        self.assertTrue(self.uuid != uuid_different)
        self.assertFalse(self.uuid != self.uuid)

    def test_uuid4_generation(self):
        uuid_obj = uuid4()
        self.assertEqual(len(uuid_obj.bytes), 16)
        self.assertEqual(uuid_obj.version, 4)

    def test_randstr_16(self):
        # Test that randstr_16 returns bytes of correct length
        random_bytes = randstr_16()
        self.assertIsInstance(random_bytes, bytes)
        self.assertEqual(len(random_bytes), 16)

        # Test that multiple calls return different values
        another_random = randstr_16()
        self.assertNotEqual(random_bytes, another_random)

        # Test that the bytes can be used to create a valid UUID
        uuid_obj = UUID(random_bytes)
        self.assertEqual(len(uuid_obj.bytes), 16)


if __name__ == "__main__":
    unittest.main()
