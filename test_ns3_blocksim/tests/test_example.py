"""
Example test file to demonstrate pytest functionality.
"""
import unittest


class TestExample(unittest.TestCase):
    """Example test class."""

    def test_addition(self):
        """Test that addition works correctly."""
        self.assertEqual(1 + 1, 2)
