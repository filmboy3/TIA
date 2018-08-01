import unittest
import general_message_helpers as msg_gen
import time

class TestReminder(unittest.TestCase):
    def test_add_time_zone_offset_from_pst(self):
        self.assertEqual(msg_gen.add_time_zone_offset_from_pst("227 Waikalani Drive Mililani, HI 96789", "Unnecessary for Test"), -3)
        time.sleep(2)
        self.assertEqual(msg_gen.add_time_zone_offset_from_pst("548 Market St, San Francisco, CA 94104", "Unnecessary for Test"), 0)
        time.sleep(2)
        self.assertEqual(msg_gen.add_time_zone_offset_from_pst("1730 Blake Street denver co 80202", "Unnecessary for Test"), 1)
        time.sleep(2)
        self.assertEqual(msg_gen.add_time_zone_offset_from_pst("28955 Sunny Beach Rd, Grand Rapids, MN 55744", "Unnecessary for Test"), 2)
        time.sleep(2)
        self.assertEqual(msg_gen.add_time_zone_offset_from_pst("250 Lafayette Street ny ny", "Unnecessary for Test"), 3)

if __name__ == "__main__":
    unittest.main()