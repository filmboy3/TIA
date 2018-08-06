from __future__ import print_function
import httplib2
import os
from apiclient.discovery import build
import time
import base64
import re
import wikipedia
from apiclient import errors
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime
import requests
import string
import numbers
import math
import random
import calendar

comboHeader = ""
result = ""
home = default_home
zip = home.split(" ")
zip = str(zip[len(zip)-1])

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

import auth

################################## GMAIL API FUNCTIONS / SETUP ##################################

SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'
authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
credentials = authInst.get_credentials()

http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)

import send_email
# import get_email

# Build the Gmail service from discovery
gmail_service = build('gmail', 'v1', http=http)


def ListMessagesWithLabels(service, user_id, label_ids=[]):
  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      if 'messages' in response:
        messages.extend(response['messages'])

    return messages
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

def GetMessage(service, user_id, msg_id):
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    print('Message snippet: %s' % message['snippet'])

    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)
  
def DeleteMessage(service, user_id, msg_id):
  try:
    service.users().messages().delete(userId=user_id, id=msg_id).execute()
    print('Message with id: %s deleted successfully.' % msg_id)
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

def ModifyMessage(service, user_id, msg_id, msg_labels):
  try:
    message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                body=msg_labels).execute()

    label_ids = message['labelIds']

    print('Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

def CreateMsgLabels():
  """Create object to update labels.

  Returns:
    A label update object.
  """
  return {'removeLabelIds': ['UNREAD'], 'addLabelIds': []}

def snippetClean(result):
    result = re.sub("&nbsp;", " ", result)
    result = re.sub("&amp;", "&", result)
    result = re.sub("&quot;", "'", result)
    result = re.sub("&ndash;", "--", result)
    result = re.sub("&#39;", "'", result)
    result = re.sub("&amp;", "&", result)
    result = re.sub("View in browser", " ", result)
    result = re.sub("&#8217;", "'", result)
    result = re.sub("&rdquo;", "'", result)
    result = re.sub("&vert;", "'", result)
    result = re.sub("&lt;", "", result)
    result = re.sub("&rt;", "", result)
    result = re.sub("&#8220;", "'", result)
    result = re.sub("&#8221;", "'", result)
    result = re.sub("&#8217;", "'", result)
    result = re.sub("&ldquo;", "'", result)
    result = re.sub("&mdash;", "-", result)
    result = re.sub("&rsquo;", "'", result)
    result = re.sub("&quot;", "'", result)
    result = re.sub("&mdash;", "--", result)
    result = re.sub("&nbsp;", " ", result)
    result = re.sub("New blank template", " ", result)
    result = re.sub("View in browser", " ", result)
    result = re.sub("View this email in your browser.", " ", result)
    result = re.sub("Learn about our Privacy Policy", " ", result)
    result = re.sub("Subscribe", " ", result)
    result = re.sub("|", "", result)
    result = re.sub("unsubscribe.", " ", result)
    result = re.sub("manage your subscriptions.", " ", result)
    result = re.sub("mailing address.", " ", result)
    result = re.sub("received this email.", " ", result)
    result = re.sub("click here.", " ", result)
    result = re.sub("Click Here.", " ", result)
    result = re.sub("&amp;", "&", result)
    result = re.sub("&#8217;", "'", result)
    result = re.sub("&rdquo;", "'", result)
    result = re.sub("&vert;", "'", result)
    result = re.sub("&#8220;", "'", result)
    result = re.sub("&#8221;", "'", result)
    result = re.sub("&#8217;", "'", result)
    result = re.sub("&ldquo;", "'", result)
    result = re.sub("&mdash;", "-", result)
    result = re.sub("-footer", "", result)
    result = re.sub("&rsquo;", "'", result)
    result = re.sub("Copyright.", " ", result)
    result = re.sub("copyright.", " ", result)
    result = re.sub("#email", "", result)
    result = re.sub("Subscribe", " ", result)
    result = re.sub("copyright.", " ", result)
    result = re.sub("copyright.", " ", result)
    result = re.sub("Click here", " ", result)
    result = re.sub("Click here", " ", result)
    result = re.sub("Sponsored by", " ", result)
    result = re.sub("^(.*?)\.-body", " ", result)
    result = re.sub("'}-body", "", result)
    result = re.sub("^(.*?)\.-footer", " ", result)
    result = re.sub("All rights reserved.", " ", result)
    result = re.sub("&quot;", "'", result)
    result = re.sub("&ndash;", "--", result)
    result = re.sub("&#39;", "'", result)
    result = re.sub("forward this email.", " ", result)
    result = re.sub("Don't want to receive as many emails?", " ", result)
    result = re.sub("free subscription.", " ", result)
    return result

def fullTextClean(result):
  result = re.sub( '\s+', ' ', result ).strip()
  result = re.sub("<.*?>", "", result)
  result = re.sub("[\{][\s\S\w\W]*?[\}]", "", result)
  result = re.sub("[\}][\s\S\w\W]*?[\}]", "", result)
  result = re.sub("[\*][\s\S\w\W]*?[\*]", "", result)
  result = re.sub("[\[][\s\S\w\W]*?[\]]", "", result)
  result = re.sub("[\/*][\s\S\w\W]*?[\*]", "", result)
  result = re.sub("\.\S+", "", result)
  result = re.sub("^(.*)view in browser*", "", result)
  result = re.sub("html CSS for hiding content in desktop", "", result)
  result = re.sub("&nbsp;", " ", result)
  result = re.sub("&amp;", "&", result)
  result = re.sub("&quot;", "'", result)
  result = re.sub("&ndash;", "--", result)
  # result = re.sub("[?:$].\S*", " ", result)
  # result = re.sub("[\/\/][\s\S\w\W].*.?[\/\]]", " ", result)
  # result = re.sub("[\>][\s\S\w\W]*?[\>]", " ", result)
  result = re.sub("&#39;", "'", result)
  result = re.sub("&reg;", " ", result)
  result = re.sub("&copy;", " ", result)
  result = re.sub("^(.*)px\)*", "'", result)
  result = re.sub("[ ]{2,}", " ", result)
  result = re.sub("&nbsp;", " ", result)
  result = re.sub("New blank template", " ", result)
  result = re.sub("View in browser", " ", result)
  result = re.sub("View this email in your browser.", " ", result)
  result = re.sub("Learn about our Privacy Policy", " ", result)
  result = re.sub("Subscribe", " ", result)
  result = re.sub("|", "", result)
  result = re.sub("unsubscribe.", " ", result)
  result = re.sub("manage your subscriptions.", " ", result)
  result = re.sub("mailing address.", " ", result)
  result = re.sub("received this email.", " ", result)
  result = re.sub("click here.", " ", result)
  result = re.sub("Click Here.", " ", result)
  result = re.sub("&amp;", "&", result)
  result = re.sub("&#8217;", "'", result)
  result = re.sub("&rdquo;", "'", result)
  result = re.sub("&vert;", "'", result)
  result = re.sub("&#8220;", "'", result)
  result = re.sub("&#8221;", "'", result)
  result = re.sub("&#8217;", "'", result)
  result = re.sub("&ldquo;", "'", result)
  result = re.sub("&mdash;", "-", result)
  result = re.sub("-footer", "", result)
  result = re.sub("&rsquo;", "'", result)
  result = re.sub("Copyright.", " ", result)
  result = re.sub("copyright.", " ", result)
  result = re.sub("#email", "", result)
  result = re.sub("Subscribe", " ", result)
  result = re.sub("copyright.", " ", result)
  result = re.sub("copyright.", " ", result)
  result = re.sub("Click here", " ", result)
  result = re.sub("Click here", " ", result)
  result = re.sub("'} -body,", " ", result)
  result = re.sub("Sponsored by", " ", result)
  result = re.sub("^(.*?)\.-body", " ", result)
  result = re.sub("^(.*?)\.-footer", " ", result)
  result = re.sub("All rights reserved.", " ", result)
  result = re.sub("&quot;", "'", result)
  result = re.sub("&ndash;", "--", result)
  result = re.sub("&#39;", "'", result)
  result = re.sub("forward this email.", " ", result)
  result = re.sub("Don't want to receive as many emails?", " ", result)
  result = re.sub("free subscription.", " ", result)
  return result


####################################### WEATHER/DIRECTIONS FUNCTIONS ########################################
def convertWeatherToEmoji(iconName):
  if (iconName == "01d"): 
    return "☀️"
  if (iconName == "01n"):
    return "🌃" 
  if (iconName == "02d"):
    return "🌤"
  if (iconName == "02n"):
    return "🌤" 
  if (iconName == "03d"):
    return "☁️" 
  if (iconName == "03n"):
    return "☁️" 
  if (iconName == "04d"):
    return "⛅️" 
  if (iconName == "04n"):
    return "⛅️" 
  if (iconName == "09d"):
    return "🌧" 
  if (iconName == "09n"):
    return "🌧" 
  if (iconName == "10d"):
    return "☔️" 
  if (iconName == "10n"):
    return "☔️" 
  if (iconName == "11d"):
    return "🌩" 
  if (iconName == "11n"):
    return "🌩" 
  if (iconName == "13d"):
    return "🌨" 
  if (iconName == "13n"):
    return "🌨" 
  if (iconName == "50d"):
    return "🌁" 
  if (iconName == "50n"):
    return "🌁" 

def convertKelvinToFahrenheit(tempK):
  return (9/5) * (tempK - 273) + 32

def parseWeather(str):
  location = lookupSingleLocation(str)
  zip = getZip(location)
  print(zip)
  
  return zip

def lookupSingleLocation(str):
  url = "https://geocoder.cit.api.here.com/6.2/geocode.json?app_id=" + geoCoderAppID "&app_code=" + geoCoderCode + "&searchtext="
  for s in string.punctuation:
    str = str.replace(s,'')
  str = str.split(" ")
  str = "+".join(str)
  url = url + str
  print(url)
  json_data = requests.get(url).json()
  return json_data

def getLatLong(str):
  json_data = lookupSingleLocation(str)
  latLong = []
  latLong.append(json_data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude'])
  latLong.append(json_data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude'])
  return latLong

def getZip(str):
  json_data = lookupSingleLocation(str)
  zip = json_data['Response']['View'][0]['Result'][0]['Location']['Address']['PostalCode']
  print(zip)
  return zip

def weatherAlert(subjectLabel):
    if subjectLabel == "":
      zip = home.split(" ")
      zip = str(zip[len(zip)-1])
      url = weatherAppSecretURL + zip
      subjectLabel = zip
    else:
      api_address = weatherAppSecretURL + " &zip="
      url = api_address + getZip(subjectLabel)  
    json_data = requests.get(url).json()
    print(json_data)
    currentTemp = str(int(round(convertKelvinToFahrenheit(json_data['main']['temp']), 0)))
    print(currentTemp)
    highTemp = str(int(round(convertKelvinToFahrenheit(json_data['main']['temp_max']), 0)))
    print(highTemp)
    lowTemp = str(int(round(convertKelvinToFahrenheit(json_data['main']['temp_min']), 0)))
    print(lowTemp)
    description = str(json_data['weather'][0]['description'])
    print(description)
    humidity = str(json_data['main']['humidity'])
    print(humidity)
    weatherIcon = convertWeatherToEmoji(str(json_data['weather'][0]['icon']))
    comboHeader = "Weather"
    result = ("Today in " + subjectLabel.upper() + " expect " + description + ", " + weatherIcon + ", with a current 🌡 of " + currentTemp + "°F, high of " + highTemp + "°F, low of " + lowTemp + "°F, and humidity at " + humidity + "%. Have a great day!")
    return result

def readableForecast(data, subjectLabel):
  outer = "Your 5-Day Forecast in " + subjectLabel.upper() + "\n"
  for i in range(0, len(data) - 1):
    dateCheck = data[i]["dt_txt"].split(" ")[0]
    dayOfWeek = calendar.weekday(int(dateCheck.split("-")[0]), int(dateCheck.split("-")[1]), int(dateCheck.split("-")[2]))
    if dayOfWeek == 0:
        strOfDay = "Mon @ "
    if dayOfWeek == 1:
        strOfDay = "Tue @ "
    if dayOfWeek == 2:
        strOfDay = "Wed @ "
    if dayOfWeek == 3:
        strOfDay = "Thu @ "
    if dayOfWeek == 4:
        strOfDay = "Fri @ "
    if dayOfWeek == 5:
        strOfDay = "Sat @ "
    if dayOfWeek == 6:
        strOfDay = "Sun @ "
    timeOfDay = data[i]["dt_txt"].split(" ")[1]
    updatedTime = int(timeOfDay.split(":")[0])
    if (updatedTime > 12):
        updatedTime = updatedTime - 12
        finalTime = str(updatedTime) + " pm"
    elif (updatedTime == 12):
        finalTime = "noon"
    elif (updatedTime == 0):
        finalTime = "12am"
    else:
        finalTime = str(updatedTime) + " am" 
    miniPhrase = strOfDay + finalTime + " 🌡 " + str(int(round(convertKelvinToFahrenheit((data[i]['main']['temp']))))) + "° " + convertWeatherToEmoji(data[i]['weather'][0]['icon']) + " " + data[i]['weather'][0]['description'] + "\n"
    # print(miniPhrase)
    outer += miniPhrase  
  return outer

def forecastAlert(subjectLabel):
    if subjectLabel == "":
        zip = home.split(" ")
        zip = str(zip[len(zip)-1])
        url = "http://api.openweathermap.org/data/2.5/forecast?appid=" + weatherAPI + "&zip=" + zip
        subjectLabel = zip
    # Or input zipcode
    else:
        api_address = "http://api.openweathermap.org/data/2.5/forecast?appid=" + weatherAPI + "&zip="
        url = api_address + getZip(subjectLabel)
    json_data = requests.get(url).json()
    strOfDay = ""
    dayOfWeek = 0
    dateCheck = ""
    result = ('So far so good with forecast')
    data = json_data['list']
    result = readableForecast(json_data['list'], subjectLabel)
    return result

def removeSubjectCommand(subjectLabel):
  subjectLabel = subjectLabel.split(" ")
  print(subjectLabel)
  subjectLabel.pop(0)
  subjectLabel = " ".join(subjectLabel)
  return subjectLabel

def lookupSingleLocation(str):
  url = "https://geocoder.cit.api.here.com/6.2/geocode.json?app_id=" + geoCodeAPI + "&searchtext="
  for s in string.punctuation:
    str = str.replace(s,'')
  str = str.split(" ")
  str = "+".join(str)
  url = url + str
  print(url)
  json_data = requests.get(url).json()
  return json_data

def getLatLong(str):
  json_data = lookupSingleLocation(str)
  latLong = []
  latLong.append(json_data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude'])
  latLong.append(json_data['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude'])
  return latLong

def removeSubjectCommand(subjectLabel):
  subjectLabel = subjectLabel.split(" ")
  print(subjectLabel)
  subjectLabel.pop(0)
  subjectLabel = " ".join(subjectLabel)
  return subjectLabel

def getTwoLatLong(subjectLabel):
  subjectLabel = subjectLabel.split(" to ")
  latLongOrigin = []
  # If either start or final destination are the home, then change it to Preset Cranford home address.  
  if (subjectLabel[0] == 'home'):
    latLongOrigin.append(getLatLong(home))
  else:
    latLongOrigin.append(getLatLong(subjectLabel[0]))
  if (subjectLabel[1] == 'home'):
    latLongOrigin.append(getLatLong(home))
  else:
    latLongOrigin.append(getLatLong(subjectLabel[1]))
  return latLongOrigin

def convertDistanceFromMetric(text):
  num = re.findall('<span class="length">(.*?)</span>', text)
  for i in range(0, len(num)):
    numPreConvert = num[i].split(" ")
    newNum = ""
    if (numPreConvert[1] == 'm'):
      print("\nHey, I'm a metre:")
      print(numPreConvert)
      feet = int(round(int(numPreConvert[0]) * 3.28084, 0))
      feet = int(math.ceil(feet / 25.0)) * 25
      print(feet)
      newNum = str(feet) + " ft"
      print("Post converted meters: " + str(newNum))
    else:
      print("\nhey, I'm a km")
      miles = round(float(numPreConvert[0]) / 0.6213, 1)
      newNum = str(miles) + " miles"
      print("post converted km: " + str(newNum))
    text = text.replace(num[i], newNum)
  return text

def cleanUpDirections(text):
  text = convertDistanceFromMetric(text)
  text = text.replace("Airport", "✈️ Airport")
  text = text.replace("Arrive at", "🎯 Arrive at")
  text = text.replace('<span class="time">', "⌚ ")
  text = text.replace('<span class="cross_street">', "🛣️ ")
  text = text.replace('<span class="distance-description">', '')
  text = text.replace('<span class="stops">', '🚇 ')
  text = text.replace('<span class="station">', '🚉 ')
  text = text.replace('<span class="line">', '🚆 ')
  text = text.replace('<span class="heading">northwest', '↖️ ↖')
  text = text.replace('<span class="heading">north', '⬆️ ')
  text = text.replace('<span class="heading">south', '⬇️ ')
  text = text.replace('<span class="heading">northeast', '↗️ ↗')
  text = text.replace('<span class="heading">southwest', '↙️ ↙')
  text = text.replace('<span class="heading">southeast', '↘️ ↘')
  text = text.replace('<span class="street">', ' 🛣️ ️')
  text = text.replace('<span class="next-street">', '')
  text = text.replace('<span class="direction">left', '⬅️ left')
  text = text.replace('<span class="direction">middle', '⬆️ middle')
  text = text.replace('<span class="street">', '🛣️ ')
  text = text.replace('<span class="length">', '')
  text = text.replace('<span class="transit">', '🚉 ')
  text = text.replace('<span class="toward_street">', '🛣️ ')
  text = text.replace('<span class="direction">right', 'right ➡️')
  text = text.replace('<span class="number">', '🛣️ ')
  text = text.replace('<span class="sign">', '🚧 ')
  text = text.replace('<span lang="en">', '')
  text = text.replace('<span class="exit">', '↪️')
  text = text.replace('<span class="destination">', '')
  text = text.replace('<span class="direction">slightly left', '↖️ left')
  text = text.replace('<span class="direction">slightly right', '↗️ right')
  text = text.replace('<span class="direction">sharp right', '🔪➡️ sharp right')
  text = text.replace('<span class="direction">sharp left', '🔪⬅️ sharp right')
  text = text.replace('</span>', '')
  text = text.replace('ftiles', 'miles')
  return text

def formatDirections(data, latLongList):
  # print(data)
  data = data['response']['route'][0]
  transit = str(data["mode"]['transportModes'][0]) 

  # Retrieving human-readable destination/origin for display in header
  originLocation = "your start"
  destinationLocation = "your final destination"
  if(data['leg'][0]['start']['label'] != ""):
    originLocation = str(data['leg'][0]['start']['label'])
  if(data['leg'][0]['end']['label'] != ""):
    destinationLocation = str(data['leg'][0]['end']['label'])

  # Creating a Header
  if (transit == "pedestrian"):
    transit = '🚶 walking'
  elif (transit == "car"):
    transit = '🚗 driving'
  elif (transit == "publicTransport"):
    transit = '🚉 public transit'
  text = ("\nHere are your " + transit + " directions from " + originLocation + " to " + destinationLocation + ".\n\n" + str(data['summary']['text']) + "🏃 Let's Go! 🏃\n")

  for i in range(0, len(data['leg'][0]['maneuver'])):
    text += "\n\n" + str(data['leg'][0]['maneuver'][i]['instruction'])
  text = cleanUpDirections(text)
  result = text
  comboHeader = "Directions"
  print(text)
  return text

def makeDirectionsRequest(latLongList, transitMode):
  url = "https://route.cit.api.here.com/routing/7.2/calculateroute.json?" + keyCodeGeo + "&waypoint0=geo!" + str(latLongList[0][0]) + "," + str(latLongList[0][1]) + "&waypoint1=geo!" + str(latLongList[1][0]) + "," + str(latLongList[1][1]) + "&mode=fastest;" + transitMode + ";traffic:enabled"
  print(url)
  return formatDirections(requests.get(url).json(), latLongList)

def carDirections(subjectLabel):
  latLongList = getTwoLatLong(subjectLabel);
  print("Car Trip: " + str(latLongList))
  return makeDirectionsRequest(latLongList, "car")

def publicTransitDirections(subjectLabel):
  latLongList = getTwoLatLong(subjectLabel);
  print("Public Transit Trip: " + str(latLongList))
  return makeDirectionsRequest(latLongList, "publicTransport")

def walkingDirections(subjectLabel):
  latLongList = getTwoLatLong(subjectLabel);
  print("Walking Trip: " + str(latLongList))
  return makeDirectionsRequest(latLongList, "pedestrian")

def directionsAlert(subjectLabel):
  if (subjectLabel.split(" ")[0] == "drive"):
    return carDirections(removeSubjectCommand(subjectLabel))
  elif (subjectLabel.split(" ")[0] == "transit"):
    return publicTransitDirections(removeSubjectCommand(subjectLabel))
  elif (subjectLabel.split(" ")[0] == "walk"):
    return walkingDirections(removeSubjectCommand(subjectLabel))

############################################ NEWS FUNCTIONS ####################################################

def newsSourceParse(str):
  if str == "ap":
    return "associated-press"
  elif str == "abc":
    return "abc-news"
  elif str == "abc-au":
    return "abc-news-au"
  elif str == "al-jazeera":
    return "al-jazeera-english"
  elif str == "ars-technica":
    return "ars-technica"
  elif str == "axios":
    return "axios"
  elif str == "bbc":
    return "bbc-news"
  elif str == "bbc-sport":
    return "bbc-sport"
  elif str == "br":
    return "bleacher-report"
  elif str == "bloomberg":
    return "bloomberg"
  elif str == "breitbart":
    return "breitbart-news"
  elif str == "business-insider":
    return "business-insider"
  elif str == "business-insider-uk":
    return "business-insider-uk"
  elif str == "buzzfeed":
    return "buzzfeed"
  elif str == "cbc-news":
    return "cbc-news"
  elif str == "cbs-news":
    return "cbs-news"
  elif str == "cnbc":
    return "cnbc"
  elif str == "cnn":
    return "cnn"
  elif str == "crypto":
    return "crypto-coins-news"
  elif str == "daily-mail":
    return "daily-mail"
  elif str == "engadget":
    return "engadget"
  elif str == "ew":
    return "entertainment-weekly"
  elif str == "espn":
    return "espn"
  elif str == "financial-post":
    return "financial-post"
  elif str == "ft":
    return "financial-times"
  elif str == "fortune":
    return "fortune"
  elif str == "fox-sports":
    return "fox-sports"
  elif str == "google":
    return "google-news"
  elif str == "google-uk":
    return "google-news-uk"
  elif str == "hn":
    return "hacker-news"
  elif str == "ign":
    return "ign"
  elif str == "independent":
    return "independent"
  elif str == "mashable":
    return "mashable"
  elif str == "medical":
    return "medical-news-today"
  elif str == "metro":
    return "metro"
  elif str == "mirror":
    return "mirror"
  elif str == "msnbc":
    return "msnbc"
  elif str == "mtv":
    return "mtv-news"
  elif str == "mtv-uk":
    return "mtv-news-uk"
  elif str == "national-geographic":
    return "national-geographic"
  elif str == "national-review":
    return "national-review"
  elif str == "nbc":
    return "nbc-news"
  elif str == "new-scientist":
    return "new-scientist"
  elif str == "news-com-au":
    return "news-com-au"
  elif str == "newsweek":
    return "newsweek"
  elif str == "nymag":
    return "new-york-magazine"
  elif str == "future":
    return "next-big-future"
  elif str == "nfl":
    return "nfl-news"
  elif str == "nhl":
    return "nhl-news"
  elif str == "politico":
    return "politico"
  elif str == "polygon":
    return "polygon"
  elif str == "recode":
    return "recode"
  elif str == "reddit":
    return "reddit-r-all"
  elif str == "reuters":
    return "reuters"
  elif str == "techcrunch":
    return "techcrunch"
  elif str == "techradar":
    return "techradar"
  elif str == "economist":
    return "the-economist"
  elif str == "globe-and-mail":
    return "the-globe-and-mail"
  elif str == "guardian":
    return "the-guardian-uk"
  elif str == "guardian-au":
    return "the-guardian-au"
  elif str == "huffpost":
    return "the-huffington-post"
  elif str == "the-irish-times":
    return "irish-times"
  elif str == "lad-bible":
    return "the-lad-bible"
  elif str == "nyt":
    return "the-new-york-times"
  elif str == "next-web":
    return "the-next-web"
  elif str == "sport-bible":
    return "the-sport-bible"
  elif str == "telegraph":
    return "the-telegraph"
  elif str == "verge":
    return "the-verge"
  elif str == "wsj":
    return "the-wall-street-journal"
  elif str == "washington-post":
    return "the-washington-post"
  elif str == "washington-times":
    return "the-washington-times"
  elif str == "time":
    return "time"
  elif str == "usa-today":
    return "usa-today"
  elif str == "vice-news":
    return "vice-news"
  elif str == "wired":
    return "wired"
  else:
    return str

def getDomainForHN(url):
    #requires 'http://' or 'https://'
    #pat = r'(https?):\/\/(\w+\.)*(?P<domain>\w+)\.(\w+)(\/.*)?'
    #'http://' or 'https://' is optional
    pat = r'((https?):\/\/)?(\w+\.)*(?P<domain>\w+)\.(\w+)(\/.*)?'
    m = re.match(pat, url)
    if m:
        domain = m.group('domain')
        return domain
    else:
        return False

def hackerNewsAlert():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
    json_data = requests.get(url).json()
    fullText = ""
    for i in range(0, 30):
        newUrl = "https://hacker-news.firebaseio.com/v0/item/" + str(json_data[i]) + ".json?print=pretty"
        item_json_data = requests.get(newUrl).json()
        numAsString = str(i + 1)
        domainStr = ""
        try:
            domainStr = str(getDomainForHN(str(item_json_data['url'])))
        except:
            print("Domain Str is not present")
        innerCombine = numAsString + ": " + str(item_json_data['title']) + "\n🔼 " + str(item_json_data['score']) + " 🔼" + domainStr + "\n\n"
        fullText += innerCombine
    return fullText

def newYorkTimesAlert():
    url = "https://api.nytimes.com/svc/topstories/v2/home.json?api-key=" + nyTimesKey 
    json_data = requests.get(url).json()
    print(json_data)
    print(type(json_data))
    fullText = ""
    for i in range(0, len(json_data['results']) - 1):
        phrase = ""
        section = str(json_data['results'][i]['section']) 
        title = str(json_data['results'][i]['title'])
        abstract = str(json_data['results'][i]['abstract'])
        phrase = str(section + " 📰 '" + title + "' 📰\n" + abstract + "\n\n\n")
        if section != "Briefing":
            fullText += phrase
    return fullText

def newsAlert(news):
    sourceInsert = newsSourceParse(news)
    url = "https://newsapi.org/v2/top-headlines?sources=" + sourceInsert + "&apiKey" + key
    json_data = requests.get(url).json()
    articles = json_data['articles']
    fullText = "Top Headlines from " + articles[0]['source']['name'] + ":\n\n"
    for i in range(0, len(articles)):
        title = articles[i]['title']
        description = ""
        if str(articles[i]['description']) != "None":
            description = "\n" + articles[i]['description']
        innerCombine = str(i+1) + " 📰 " + title + " 📰 " + description + "\n\n"
        fullText += innerCombine
    return fullText

def jeopardyTrivia():
  url = "http://jservice.io/api/random?count=1"
  json_data = requests.get(url).json()
  categoryID = json_data[0]["category"]["id"]

  url = "http://jservice.io/api/category?id=" + str(categoryID)
  json_data = requests.get(url).json()
  # print(len(json_data['clues']))
  # print("Clues Count: " + str(json_data['clues_count']))
  total_clues = json_data['clues_count']
  clues_in_category = 5
  multiple = (total_clues / 5) - 1
  startingIndex = round(random.random()*multiple)*clues_in_category
  # print(startingIndex)
  category = str(json_data["title"].upper())
  totalString = ""
  airYear = str(json_data['clues'][startingIndex]["airdate"].split("-")[0])
  totalString = "This. Was. Jeopardy. (" + airYear + ")\n\n" + category + "\n\n"
  # print(totalString)
  answerKey = "\n🚧 🚧 🚧 🚧 🚧 🚧 \n⬇️ SPOILERS ⬇️\n🚧 🚧 🚧 🚧 🚧 🚧 \n\n"
  answerKey = answerKey + totalString
  for i in range (startingIndex, startingIndex+5):
    if (str(json_data['clues'][i]["invalid_count"]) == 1):
      return jeopardyTrivia();
    response = str(json_data['clues'][i]["question"])
    value = "💰 $" + str(json_data['clues'][i]["value"]) + "💰"
    if (str(json_data['clues'][i]["value"]) == "None"):
      return jeopardyTrivia();
    totalString = totalString + value + "\n" + response + "\n\n"
    answerQuestion = str(json_data['clues'][i]["answer"])
    answerKey = answerKey + response + "\n" + "🎯 " + answerQuestion + " 🎯 " + "\n\n"
    # answerKey = answerKey + value + " " + answerQuestion + "\n"
  answerKey = answerKey + "\n🚧 🚧 🚧 🚧 🚧 🚧 \n⬆️ SPOILERS ⬆️\n🚧 🚧 🚧 🚧 🚧 🚧 \n"
  answerKey = answerKey.replace('<i>', '')
  answerKey = answerKey.replace('</i>', '')
  return (totalString, answerKey)
  # print(totalString)
############################################ RUNNING SMS ASSISTANT ####################################################


def runSMSAssist():
    # A 'temp' global variable is initialized since
    # we need to be able to keep track of the most 
    # recent 'unread' email for deleting/marking-as-read purposes
    temp = ''
    def inner():
        print('Starting...') 
        a = ListMessagesWithLabels(service, 'me', label_ids = ['UNREAD'])[0]['id']
        nonlocal temp
        if a != temp: 
            b = GetMessage(service,'me',a)
            fromLabel = ""
            subjectLabel = ""

            # Parsing the 'From' and 'Subject's of the email 
            for item in b['payload']['headers']:
              if item['name'] == 'From':
                fromLabel = item['value']
                print("fromLabel: " + str(fromLabel))
              if item['name'] == 'Subject':
                subjectLabel = item['value']
                print("subjectLabel: " + str(subjectLabel))

            # Re-formatting the Subject-line
            comboHeader = fromLabel + " " + subjectLabel
            comboHeader = re.sub("<.*?>", "", comboHeader)
            print("comboHeader: " + str(comboHeader))

            try:
              # Parsing Email Messages to be forwarded via SMS 
              msg_str = base64.urlsafe_b64decode(b['payload']['body']['data'].replace('-_', '+/').encode('ASCII'))
              result = msg_str.decode('utf-8')

              # Lots of HTML scrubbing in the following two functions, fullText is more extensive, 
              # since snippetClean() handles gmail's snippets, which are shorter with less HTML
              result = fullTextClean(result)
              result = snippetClean(result)

              print("result after scrubbing/decoding: " + str(result))
              sendInst = send_email.send_email(service)

              # Commands from the user
              if fromLabel == '9083766480@vtext.com':
                subjectLabel = result.lower()
                print("Triggered Jonathan's " + subjectLabel)
                # Delete the requested message itself first
                DeleteMessage(service,'me',a)

                # Gmail "Delete" most recent unread message
                if subjectLabel == "delete":
                  a = ListMessagesWithLabels(service, 'me', label_ids = ['UNREAD'])[0]['id']
                  DeleteMessage(service,'me',a)
                # Gmail mark as "READ" most recent unread message
                elif subjectLabel == "read":
                  a = ListMessagesWithLabels(service, 'me', label_ids = ['UNREAD'])[0]['id']
                  ModifyMessage(service, 'me', a, CreateMsgLabels())
                  # print("Completed Removing of the Label for " + a + "?")
                # Wikipedia Query
                elif subjectLabel.split(" ")[0] == "wiki":
                  try:
                    query = " ".join(subjectLabel.split(" ")[1:])
                    print(query)
                    result = wikipedia.summary(query)
                    comboHeader = "Wikpedia " + str(query)
                  except:
                    result = ('Wikipedia query ' + query + ' failed ... please try again')
                # Weather Query
                elif (subjectLabel.split(" ")[0].lower() == "weather"):
                  try:
                    result = weatherAlert(removeSubjectCommand(subjectLabel))
                    comboHeader = "Weather"
                  except:
                    result = "Weather Alert failed, which means the sky is currently falling ..."
                # 5-Day-Forecast Query
                elif (subjectLabel.split(" ")[0].lower() == "forecast"):
                    try:
                      result = forecastAlert(removeSubjectCommand(subjectLabel))
                      comboHeader = "Forecast"
                    except:
                      result = "5-Day Forecast failed, which means the world will end in the next couple days..."
                # Directions Query
                elif (subjectLabel.split(" ")[0].lower() == "directions"):
                    try:
                      result = directionsAlert(removeSubjectCommand(subjectLabel))
                      comboHeader = "Directions"
                    except:
                      result = "Directions failed, which means you're never leaving the basement ..."
                # HackerNews Query
                elif (subjectLabel.split(" ")[0].lower() == "hn"):
                    try:
                        result = hackerNewsAlert()
                        comboHeader = "Hacker News"
                    except:
                      result = "Hacker News failed, which means the Silicon Valley Bubble has finally burst..."
                # NY Times Query
                elif (subjectLabel.split(" ")[0].lower() == "nyt"):
                    try:
                        result = newYorkTimesAlert()
                        comboHeader = "NY Times"
                    except:
                        result = "NY times failed, which means they were actually fake news the entire time ..."
                elif (subjectLabel.split(" ")[0].lower() == "jeopardy"):
                  try:
                    tupleResult = jeopardyTrivia()
                    questionResult = tupleResult[0]
                    result = tupleResult[1]
                    comboHeader = "Jeopardy Trivia"
                    # Send the question result 5 seconds before the answers in Jeopardy
                    message = sendInst.create_message(MY_GMAIL_API_EMAIL, MY_SMS_GATEWAY_EMAIL, comboHeader, questionResult)
                    sendInst.send_message('me', message)
                    print(message)
                    time.sleep(10)
                    comboHeader = "Jeopardy SPOILERS"
                  except:
                    result = "Jeopardy failed, which means Alex Trbek is off saving someone's life..."
                # 75+ Aggregated News Sources Query 
                elif (subjectLabel.split(" ")[0].lower() == "news"):
                  try:
                      newsName = removeSubjectCommand(subjectLabel)
                      result = newsAlert(newsName)
                      comboHeader = ("News " + str(newsName).upper())
                  except:
                      result = "News failed, which means somewhere, a poor newsboy is starving..."
                # Directory of 75+ news sources Query
                elif (subjectLabel.split(" ")[0].lower() == "news-directory"):
                    result = "75+ News Sources, to retrieve top stories, type 'news [news-source]', i.e., 'news abc': \n\n📰ap\n📰abc\n📰abc-au\n📰al-jazeera\n📰ars-technica\n📰axios\n📰bbc\n📰bbc-sport\n📰br\n📰bloomberg\n📰breitbart\n📰business-insider\n📰business-insider-uk\n📰buzzfeed\n📰cbc-news\n📰cbs-news\n📰cnbc\n📰cnn\n📰crypto\n📰daily-mail\n📰engadget\n📰ew\n📰espn\n📰financial-post\n📰ft\n📰fortune\n📰fox-sports\n📰google\n📰google-uk\n📰hn\n📰ign\n📰independent\n📰mashable\n📰medical\n📰metro\n📰mirror\n📰msnbc\n📰mtv\n📰mtv-uk\n📰national-geographic\n📰national-review\n📰nbc\n📰new-scientist\n📰news-com-au\n📰newsweek\n📰nymag\n📰future\n📰nfl\n📰nhl\n📰politico\n📰polygon\n📰recode\n📰reddit\n📰reuters\n📰techcrunch\n📰techradar\n📰economist\n📰globe-and-mail\n📰guardian\n📰guardian-au\n📰huffpost\n📰the-irish-times\n📰lad-bible\n📰nyt\n📰next-web\n📰sport-bible\n📰telegraph\n📰verge\n📰wsj\n📰washington-post\n📰washington-times\n📰time\n📰usa-today\n📰vice-news\n📰wired"
                    comboHeader = "News Directory"
                    result = "75+ News Sources, to retrieve top stories, type 'news [news-source]', i.e., 'news abc': \n\n📰ap\n📰abc\n📰abc-au\n📰al-jazeera\n📰ars-technica\n📰axios\n📰bbc\n📰bbc-sport\n📰br\n📰bloomberg\n📰breitbart\n📰business-insider\n📰business-insider-uk\n📰buzzfeed\n📰cbc-news\n📰cbs-news\n📰cnbc\n📰cnn\n📰crypto\n📰daily-mail\n📰engadget\n📰ew\n📰espn\n📰financial-post\n📰ft\n📰fortune\n📰fox-sports\n📰google\n📰google-uk\n📰hn\n📰ign\n📰independent\n📰mashable\n📰medical\n📰metro\n📰mirror\n📰msnbc\n📰mtv\n📰mtv-uk\n📰national-geographic\n📰national-review\n📰nbc\n📰new-scientist\n📰news-com-au\n📰newsweek\n📰nymag\n📰future\n📰nfl\n📰nhl\n📰politico\n📰polygon\n📰recode\n📰reddit\n📰reuters\n📰techcrunch\n📰techradar\n📰economist\n📰globe-and-mail\n📰guardian\n📰guardian-au\n📰huffpost\n📰the-irish-times\n📰lad-bible\n📰nyt\n📰next-web\n📰sport-bible\n📰telegraph\n📰verge\n📰wsj\n📰washington-post\n📰washington-times\n📰time\n📰usa-today\n📰vice-news\n📰wired"   
                # General Welcome/Help PAge 
                elif (subjectLabel.split(" ")[0].lower() == "welcome"):
                  result = "Welcome to 📶 SIA 📶 your mobile SMS Internet Assistant!\n"\
                  "Only text message access is required, no internet necessary 😉\n\n"\
                  "Here are Sia's commands:\n☀️ Current Weather ☀️\nEnter: weather [place location] \n"\
                  "Example: weather malibu ca\n\n(blank location defaults to home)\n\n\n"\
                  "⛅️ 5-Day-Forecast ⛅️\nEnter: forecast [place location] \n"\
                  "Example: forecast las vegas\n\n(blank location defaults to home)\n\n\n"\
                  "🚗 Directions 🚗\nEnter: directions [drive OR walk OR transit] [starting location] to [destination location]\n"\
                  "Example: directions 421 Division St S, Northfield, MN to st olaf college, northfield, minnesota\n\n"\
                  "(either start or end can be listed as 'home', which defaults to home)\n\n\n"\
                  "📰 Aggregated News 📰\nEnter: news [source]\n"\
                  "Example: news abc\n\n\n"\
                  "📰 Aggregated News Source Lookup 📰\nEnter: news-directory\n"\
                  "75+ sources listed\n\n\n"\
                  "📰 NY Times 📰 Top Summaries\nEnter: nyt\n\n\n"\
                  "💻 Hacker News 💻 Top Summaries\nEnter: hn\n\n\n"\
                  "🤔 Jeopardy 🤔 Random Category\nEnter: Jeopardy\n\n\n"\
                  "📚 Wikipedia 📚 Summaries\nEnter: wiki [search]\n\n"\
                  "Example: wiki barack obama\n\n"
                  comboHeader = "Welcome to Sia!"

              # print("result after fromLabel cresult)

              # Compilation of the final message to be sent back to the user
              message = sendInst.create_message(MY_GMAIL_API_EMAIL, MY_SMS_GATEWAY_EMAIL, comboHeader, result)

              # Prevents sending the message if the user is just commanding a delete or mark as read
              if subjectLabel != "delete":
                if subjectLabel != "read":
                  sendInst.send_message('me', message)
            except:
              result = b['snippet']
              result = snippetClean(result)
              sendInst = send_email.send_email(service)
              message = sendInst.create_message(MY_GMAIL_API_EMAIL, MY_SMS_GATEWAY_EMAIL, comboHeader, result)      
              sendInst.send_message('me', message)  
        temp = a
        time.sleep(10)
    while True:
      try:
        inner()
      except:
         time.sleep(10)
         result = "For some reason, there's an error ..."
         print('Hit an error... trying to avoid a crash here')
        #  sendInst = send_email.send_email(service)
        #  message = sendInst.create_message(MY_GMAIL_API_EMAIL, MY_GMAIL_API_EMAIL, 'Error triggered', result)      
        #  sendInst.send_message('me', message)  

runSMSAssist()
