from __future__ import print_function
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from yelpapi import YelpAPI
from wit import Wit


# Setup Google Sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret_sheet.json', scope)
client = gspread.authorize(creds)

# Open the Spreadsheets
user_info_sheet = client.open('SIA_USERS').sheet1
sms_request_sheet = client.open('SIA_USERS').get_worksheet(1)
api_keys_sheet = client.open('SIA_USERS').get_worksheet(2)

# Download API Keys from Database
HERE_APPID = api_keys_sheet.cell(2, 3).value
HERE_APPCODE = api_keys_sheet.cell(2, 4).value
OPEN_WEATHER_API = api_keys_sheet.cell(2, 5).value
NY_TIMES_API = api_keys_sheet.cell(2, 6).value
NEWS_API = api_keys_sheet.cell(2, 7).value
JOKES_URL = api_keys_sheet.cell(2, 8).value
WOLFRAM_API = api_keys_sheet.cell(2, 9).value
SECRET_MONGO_URI = str(api_keys_sheet.cell(2, 13).value)
SECRET_YELP_API = str(api_keys_sheet.cell(2, 14).value)
YELP_API = YelpAPI(SECRET_YELP_API)
ZONE_API_KEY = str(api_keys_sheet.cell(2, 19).value)

# SET UP NLP w/ WIT.AI
WIT_CLIENT = Wit(str(api_keys_sheet.cell(2, 18).value))
GV_EMAIL = str(api_keys_sheet.cell(2, 16).value)
GV_PASSWORD = str(api_keys_sheet.cell(2, 17).value)
