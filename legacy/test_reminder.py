import unittest
import reminder_helpers as reminder

class TestReminder(unittest.TestCase):
    def test_reminder_request(self):
        result = reminder.reminder_request("remind me in 2 hours to walk the dog", "2018-07-31T23:05:00.000-07:00")
        self.assertEqual(result, "I've set a reminder for 07/31 @ 11:05 PM: ⏱️ remind me in 2 hours to walk the dog ⏱️")

if __name__ == "__main__":
    unittest.main()