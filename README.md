# Meet Tia 

TIA, aka <b><u>S</u></b>MS <b><u>I</u></b>nternet <b><u>A</u></b>ssistant, is a suite of tools to access the internet <i>without</i> the internet. Tia communicates to users through text messages. 

#### What Can Tia Do?

1. Forward | Delete | Mark-As-Read new emails (OWNER-ONLY, see gmailfeatures.py)
2. Driving | Walking | Pedestrian Directions 
3. Current Weather | 5-Day-Forecast
4. Information Summaries (Wolfram-Alpha and Wikipedia)
5. Article Summaries from 75+ News Sources
6. Jeopardy Trivia Questions
7. Yelp Searches
8. Tranlsation Services
9. Late-Night Jokes
10. Timed Reminders (WIP) 

## How it works

Running on a server built using <i>Python 3</i>, TIA communicates with 10+ RESTful APIs, beginning with ...
 
### GMAIL API 

TIA has a dedicated google voice number - (347) 352-6247 - which auto-forwards all texts to its own GMAIL account. Once the script starts, TIA continuously loops every 10 seconds `time.sleep(10)`:

1. A GET request is made to the Gmail API's inbox to check if anything new has been added to the list of messages currently marked <i>UNREAD</i>.  If there's nothing new in the 'unread' list, TIA skips ahead to #5. 

2. If there <i>is</i> a new unread item, TIA makes another GET request for that most recent 'UNREAD' message, and parses the body/subject of the email, checking whether it's a forwarded text from the GV number or a regular email.

3. If the text is a GV text, TIA parses the email, extracting the body of the text as well as the sender's number, then marks the e-mail as 'read'. 

4. The new info is added to TIA's <i><a href="https://mlab.com">MongoDB</i></a>, which features two <i>collections</i>, message_records and user_records. If there is a previous user_record with the sender's phone number, saved personal info -- name, home address, how many times they've interacted with TIA -- is transferred to the new message_record. Finally, the message is listed on the MongoDB as 'unsent'. 

5. TIA checks for any 'unsent' message_records in the MongoDB. If there are, TIA begins to process that message_record. 

6. TIA queries <i><a href="https://mlab.com">Wit.AI</i></a>, a natural language processing API, which parses the message for multitude of potential intents and keywords. Once the response is returned from the WIT API, the processing begins:

## TIA COMMANDS

### Check Weather / 5-Day-Forecast

There are two commands for weather services:

Example: "How's the weather in Dubuque?"
Example: "What's the forecast near me?"

First, the <a href="https://developer.here.com/documentation/geocoder/topics/quick-start-geocode.html"><i>Geocoder</i> API by Here</a> is queried to find the exact location entered -- for example, if the enters "malibu" without a zip code or state, Geocoder fetches more accurate information (i.e., zip, latitude/longitude) necessary for the next API call. 

This second call is sending the zip code information to <i><a href="https://openweathermap.org/API">Open Weather Map</a></i> API.  Once the request has been returned as JSON, weather information is extracted, formatted, and decorated with condition-specific weather emojis. 

Next, a <b>create request</b> is made in the GMAIL API, to craft a new email, populate it with the formatted (and emoji-fied) results of the weather call. Next, another request is made to the Gmail API to send this email to the cell-email address. This process is the same for each of Tia's non-gmail commands (except <i>Jeopardy</i>, which actually sends two emails).  

For both weather-based commands, if left blank, the location defaults to home (hard-coded for Tia's creator, in Cranford, NJ).

<a href="https://ibb.co/dFdw4y">Screenshot</a>

### Turn-By-Turn-Directions

There are three types of direction commands:

1. "I want to drive from home to Santa Clarita, CA"
2. "Let's walk from the brooklyn bridge to williamsburg"
3. "How would I take public transit from faneuil hall marketplace boston to 1575 cambridge street cambridge massachusetts?"

Similar to the weather commands, each of the two waypoint locations are used in a GET request to the <a href="https://developer.here.com/documentation/geocoder/topics/quick-start-geocode.html"><i>Geocoder</i> API by Here</a>. Once Latitude/Longitude information is returned, a call is made to the <a href="https://developer.here.com/documentation/routing/topics/what-is.html"><i>Route API</i></a>, also by Here. The GET request URL is altered depending on the transit mode requested (pedestrian, driving, or public transit), but each uses the same route-based API. 

Again, "home" synonyms can be used in either direction to default to the creator's home location.

<a href="https://ibb.co/mLyJHJ">Screenshot</a>

### News Sources

There are four commands related to news services:

Example: "What's going on at the New York Times?"
Example: "Tell me the latest from hacker news"
Examples: "ABC headlines please"

The <a href="https://newsapi.org/"><i>News Api</i></a> features a plethora of updated news summaries from providers across the globe, 75 of which were hand-picked to use on Tia. 

For this command a GET request is made to the News API for the latest ABC news headlines, which then return up to 10 of the most recent Article Titles along with brief summary, which are numbered, formatted, and emoji-fied for sms-viewing.  

While NY Times and Hacker News headlines are also available through the News API, these two have their own respective APIs, which TIA defaults to when requested, since there is more content available by querying the <a href= "https://developer.nytimes.com/">NY Times API</a> and <a href="https://github.com/HackerNews/API">Hacker News API</a>.  

<a href="https://ibb.co/fEJUPy">Screenshot</a>

### Language Translation

Example: "How would an Italian say, 'How much for that book?'"
Example: "Translate お元気ですか into English"

The translation command utlizes another NLP resource, <a href="https://textblob.readthedocs.io/en/dev/">TextBlob</a>, an open-source NLP library which in turn uses Google Translate to translate text to and from over 100 different languages. 

### Knowledge

Example: "Bio of Betty White"
Example: "Let's play some Jeopardy"
Example: "How many baseballs could fit inside a boeing 747?"

The wiki search makes a GET request using the simple <a href="https://www.mediawiki.org/wiki/API:Main_page">Wikipedia API</a>, where the response is a substantial summary of the requested wikipedia page.  

More advanced, non-biographical questions use the Wolfram-Alpha algorithmic answer API, which has a wide variety of topics and sources,  including ➗ Mathematics, 🔬 Science & Technology, 🎭 Society & Culture and 🍴 Everyday Life 🏀

The jeopardy call uses a <a href="http://jservice.io/">Jeopardy Trivia API</a> to first get a random question. Using the category ID from that number, a second GET request is made for all the clues ever aired in that category. Tia randomly picks a matched set of five clues for that category, and sends the category questions along with the spoiler answers below it. 

### Late Night Jokes

Example: "Make me laugh"
Example: "I want some late night jokes from January 1st, 2010"
Example: "Give me some random jokes"

This author put together a google sheets-based API using topical Late Night Monologue jokes from <a href="https://www.newsmax.com/jokes/">Newsmax's</a> vast collection from 2009-Present. A call to the API will yield all hosts' jokes (Fallon, Kimmel, Colbert, etc.) combined for a specific night. This request defaults to the most recent airdate, but users can select a specific date or request jokes from a random date as well. 

<a href="https://ibb.co/mG7pPy">Screenshot</a>

### HELP

There are two helper commands which give more information to the user:

Example: "Please help"
Example: "Which news sources can I choose from again?" (WIP)

These commands do not utilize any APIs, and are hard-coded text messages to remind the user of TIA's commands and which news sources are available. 

<a href="https://ibb.co/evXdHJ">Screenshot</a>

