import unittest
import reminder_helpers as reminder

resp = {'_text': 'i want daily hacker news', 'entities': {'recur_frequency': [{'confidence': 1, 'value': 'daily', 'type': 'value'}], 'wikipedia_search_query': [{'suggested': True, 'confidence': 0.93672, 'value': 'hacker', 'type': 'value'}], 'wolfram_search_query': [{'suggested': True, 'confidence': 0.86902, 'value': 'news', 'type': 'value'}], 'intent': [{'confidence': 0.97552003793374, 'value': 'hn_get'}]}, 'msg_id': '04b70XNiCmIbhYetr'}
sender_info = {'_id': "ObjectId('5b6e57cabc3dca33e0776122')", 'sms_id': 'WGypBtFyvEd4R8xe', 'body': 'I want daily hacker news ', 'from': '+13473918206', 'status': 'unprocessed', 'result': 'tba'}
expected_return = "Timmy daily hn_get"
name = "Timmy"
resp_fail = {'_text': 'i want daily hacker news', 'entities': {'recur_frequency': [{'confidence': 1, 'value': 'daily', 'type': 'value'}], 'wikipedia_search_query': [{'suggested': True, 'confidence': 0.93672, 'value': 'hacker', 'type': 'value'}], 'wolfram_search_query': [{'suggested': True, 'confidence': 0.86902, 'value': 'news', 'type': 'value'}], 'intent': [{'confidence': 0.97552003793374}]}, 'msg_id': '04b70XNiCmIbhYetr'}
expected_return = "Sorry, " + name + " ... I'm having trouble setting up your notification. Please try again later. \n\n--😘,\n✨ Tia ✨ Text" \
        " 📲 me another request, " + name + ", or text HELP"

class TestRecurring(unittest.TestCase):
    def test_trigger_recurring(self):
        result = reminder.trigger_recurring(resp_fail, sender_info)
        self.assertEqual(result, expected_return)

if __name__ == "__main__":
    unittest.main()