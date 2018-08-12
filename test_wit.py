import unittest
import wit_helpers as wit

wit_obj_translate = {'_text': "How do I say stop in German?", 'entities': {'phrase_to_translate': [{'suggested': True, 'confidence': 0.90374666666667, 'value': "'hotel'", 'type': 'value'}], 'wit_language': [{'confidence': 0.91663159906656, 'value': 'german', 'type': 'value'}], 'intent': [{'confidence': 0.99951332875839, 'value': 'translate_get'}]}, 'msg_id': '0ESdQYMCK5fs3j1Pg'}
wit_obj_jokes = {'_text': "I want some jokes", 'entities': {'phrase_to_translate': [{'suggested': True, 'confidence': 0.90374666666667, 'value': "'hotel'", 'type': 'value'}], 'wit_language': [{'confidence': 0.91663159906656, 'value': 'german', 'type': 'value'}], 'intent': [{'confidence': 0.99951332875839, 'value': 'jokes_get'}]}, 'msg_id': '0ESdQYMCK5fs3j1Pg'}
wit_obj_new_home = {'_text': "No", 'entities': {'phrase_to_translate': [{'suggested': True, 'confidence': 0.90374666666667, 'value': "'hotel'", 'type': 'value'}], 'wit_language': [{'confidence': 0.91663159906656, 'value': 'german', 'type': 'value'}], 'intent': [{'confidence': 0.99951332875839, 'value': 'translate_get'}]}, 'msg_id': '0ESdQYMCK5fs3j1Pg'}
wit_obj_new_home_2 = {'_text': "1270 Lafayette Street, NY, NY", 'entities': {'phrase_to_translate': [{'suggested': True, 'confidence': 0.90374666666667, 'value': "'hotel'", 'type': 'value'}], 'wit_language': [{'confidence': 0.91663159906656, 'value': 'german', 'type': 'value'}], 'intent': [{'confidence': 0.99951332875839, 'value': 'new_home_get'}]}, 'msg_id': '0ESdQYMCK5fs3j1Pg'}
sender_info = {'_id': "ObjectId('5b67b428bc3dca2ed0f2bc53')", 'sms_id': 'datetime.datetime(2018', 8: None, 5: None, 22: None, 36: None, 24: None, '566000)': None, 'body': "How does a german say 'hello'?", 'from': '+19083766480', 'status': 'unprocessed', 'result': 'tba', 'offset_time_zone': 3, 'local_current_time': '2018-08-05 22:36:24', 'zone_name': 'America/New_York', 'count': 23, 'local_current_time': 'unknown local time', 'home': '250 lafayette street new york ny 10012', 'name': 'Jp '}

class TestWit(unittest.TestCase):
    def test_wit_request(self):
        result = wit.nlp_extraction(wit_obj_jokes, sender_info)
        self.assertEqual(result, "jokes.trigger_jokes(resp, sender_info)")

        result = wit.nlp_extraction(wit_obj_translate, sender_info)
        self.assertEqual(result, "trans.trigger_translate(resp, sender_info)")

        result = wit.nlp_extraction(wit_obj_new_home, sender_info)
        self.assertEqual(result, "msg_gen.trigger_new_home(resp, sender_info)")

        result = wit.nlp_extraction(wit_obj_new_home_2, sender_info)
        self.assertEqual(result, "msg_gen.trigger_new_home(resp, sender_info)")

if __name__ == "__main__":
    unittest.main()