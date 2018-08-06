# coding=utf8

######################################################
#
# Tia Text Assistant - Internet tasks without using Data/Wi-Fi
# written by Jonathan Schwartz (jonathanschwartz30@gmail.com)
#
######################################################

from __future__ import print_function
from textblob import TextBlob
import wit_helpers as wit
import re

import general_message_helpers as msg_gen


def language_code_convert(language):
    language = language.lower()
    lang_db = {
        "scots gaelic": "gd",
        "afrikaans": "af",
        "albanian": "sq",
        "amharic": "am",
        "arabic": "ar",
        "armenian": "hy",
        "azeerbaijani": "az",
        "basque": "eu",
        "belarusian": "be",
        "bengali": "bn",
        "bosnian": "bs",
        "bulgarian": "bg",
        "catalan": "ca",
        "cebuano": "ceb",
        "chinese": "zh-CN",
        "traditional chinese": "zh-TW",
        "corsican": "co",
        "croatian": "hr",
        "czech": "cs",
        "danish": "da",
        "dutch": "nl",
        "english": "en",
        "esperanto": "eo",
        "estonian": "et",
        "finnish": "fi",
        "french": "fr",
        "frisian": "fy",
        "galician": "gl",
        "georgian": "ka",
        "german": "de",
        "greek": "el",
        "gujarati": "gu",
        "haitian creole": "ht",
        "hausa": "ha",
        "hawaiian": "haw",
        "hebrew": "iw",
        "hindi": "hi",
        "hmong": "hmn",
        "hungarian": "hu",
        "icelandic": "is",
        "igbo": "ig",
        "indonesian": "id",
        "irish": "ga",
        "italian": "it",
        "japanese": "ja",
        "javanese": "jw",
        "kannada": "kn",
        "kazakh": "kk",
        "khmer": "km",
        "korean": "ko",
        "kurdish": "ku",
        "kyrgyz": "ky",
        "lao": "lo",
        "latin": "la",
        "latvian": "lv",
        "lithuanian": "lt",
        "luxembourgish": "lb",
        "macedonian": "mk",
        "malagasy": "mg",
        "malay": "ms",
        "malayalam": "ml",
        "maltese": "mt",
        "maori": "mi",
        "marathi": "mr",
        "mongolian": "mn",
        "myanmar": "my",
        "nepali": "ne",
        "norwegian": "no",
        "nyanja": "ny",
        "pashto": "ps",
        "persian": "fa",
        "polish": "pl",
        "portuguese": "pt",
        "punjabi": "pa",
        "romanian": "ro",
        "russian": "ru",
        "samoan": "sm",
        "serbian": "sr",
        "sesotho": "st",
        "shona": "sn",
        "sindhi": "sd",
        "sinhala": "si",
        "slovak": "sk",
        "slovenian": "sl",
        "somali": "so",
        "spanish": "es",
        "sundanese": "su",
        "swahili": "sw",
        "swedish": "sv",
        "tagalog": "tl",
        "tajik": "tg",
        "tamil": "ta",
        "telugu": "te",
        "thai": "th",
        "turkish": "tr",
        "ukrainian": "uk",
        "urdu": "ur",
        "uzbek": "uz",
        "vietnamese": "vi",
        "welsh": "cy",
        "xhosa": "xh",
        "yiddish": "yi",
        "yoruba": "yo",
        "zulu": "zu",
    }
    try:
        return lang_db[language]
    except BaseException:
        return 'en'


def trigger_translate(resp, sender_info):
    print("Translate Triggered")
    print(resp)

    language = 'english'

    try:
        language = resp['entities']['wit_language'][0]['value']
    except BaseException:
        language = resp['entities']['wit_yelp_category'][0]['value']

    try:
        translationPhrase = resp['entities']['phrase_to_translate'][0]['value']
    except BaseException:
        try:
            translationFull = resp['_text']
            translationFull = re.sub('"', "'", translationFull)
            translationPhrase = re.search(r'\'(.*?)\'', str(translationFull)).group(1)
        except BaseException:
            translationPhrase = resp['_text']

    blob = TextBlob(translationPhrase)
    langCode = language_code_convert(language)
    translation = (resp['_text'], blob.translate(to=langCode))
    result = "✍️ '" + translationPhrase.capitalize() + "' translated into 🌏 " + \
        language.capitalize() + " 🌏 '" + str(translation[1]).capitalize() + "' ✍️"
    # print(result)
    print("Language Code: ", langCode)
    print("Translation Phrase: ", translationPhrase)
    msg_gen.store_reply_in_mongo(
             result, sender_info, "📝 Translation 📝")
    try:
        msg_gen.store_reply_in_mongo(
             result, sender_info, "📝 Translation 📝")
    except BaseException:
        msg_gen.store_reply_in_mongo(
            
            msg_gen.send_error_text("Translation"),
            sender_info,
            "💀 Error 💀")
