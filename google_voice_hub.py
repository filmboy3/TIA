# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import math
import mongo_helpers as mongo


def start_google_voice(emailAddress, emailPassword):
    chromedriver = "C:\\Users\\Jonathan2017\\Downloads\\chromedriver.exe"

    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument("--incognito")
    options.add_argument('window-size=1200x600')  # optional

    browser = webdriver.Chrome(
        executable_path=chromedriver,
        chrome_options=options)
    print("Browser: " + str(browser))
    browser.get('https://voice.google.com')
    browser.find_element_by_xpath("""//*[@id="header"]/div[2]/a""").click()
    email = browser.find_element_by_xpath("""//*[@id="identifierId"]""")
    email.click()
    email.send_keys(emailAddress)
    email.send_keys(Keys.RETURN)
    time.sleep(1)

    password = browser.find_element_by_xpath(
        """//*[@id="password"]/div[1]/div/div[1]/input""")
    password.send_keys(emailPassword)
    password.send_keys(Keys.RETURN)
    time.sleep(8)
    return browser


def send_new_message(browser, gv_number, gv_message, sender_info):
    print("Triggered Sending Message on GV")
    send_reply(gv_number, gv_message, browser)
    mongo.change_db_message_value(sender_info, "status", "sent")

def initiate_gv_send(number, browser, message):
    print("Initiated actual GV sending message to: " + str(number))
    interface_prep = setup_message(number, browser)
    enter_message(interface_prep, message, browser)
    time.sleep(2)
    delete_previous_conversation(browser)


def trigger_send_reply(record, browser):
    current_chunk = record['current_chunk']
    current_message = record['result'][current_chunk]
    print("Staged Message: " + str(current_message))
    try:
        number = record['from']
        initiate_gv_send(number, browser, current_message)
        mongo.change_db_user_value(record, "current_sms_id", record['sms_id'])
        mongo.change_db_message_value(record, "current_sms_id", record['sms_id'])
        updated_message = mongo.change_db_message_value(record, "current_chunk", (current_chunk + 1))
        updated_message = mongo.change_db_message_value(record, "current_chunk", (current_chunk + 1))
    except:
        print("Error inside Trigger_send_reply")
    return updated_message

def check_launch_time(record, browser):
    print("Placeholder for launch_time_checker")

def send_all_messages(record, browser):
    print("Sending all Messages at Once...")
    while (record['current_chunk'] < record['chunk_len']):
        record = trigger_send_reply(record, browser)


def send_next_message(record, browser):
    if (record['current_chunk'] < record['chunk_len']):
        print("Sending Next Message") 
        trigger_send_reply(record, browser)

def process_reply(record, browser):
    if record['launch_time'] == "NOW":
        if record['send_all_chunks'] == "NO":
            send_next_message(record, browser)
        else:
            send_all_messages(record, browser)
    else:
        check_launch_time(record, browser)
        

def make_sms_chunks(text, send_all_chunks, sms_size=300):
    count = len(text)
    # print(count)

    chunk_note = "\nFor next message, 📲 text MORE\nFor all messages, 📲 text ALL"
    
    if send_all_chunks == "YES":
        chunk_note = ""

    number_of_chunks = int(math.ceil(count / float(350)))
    chunk_array = []
    if number_of_chunks == 1:
        # print("No chunking Necessary")
        chunk_array.append(text)
    else:
        # print("Chunking Necessary")
        sms_end = sms_size
        sms_start = 0
        while (sms_end < count):
            while (text[sms_end] != "\n"):
                sms_end = sms_end + 1
            # print("sms_end after: " + str(sms_end) + "\n")
            current_chunk = text[sms_start:sms_end]
            # print(chunk_array)
            chunk_array.append(current_chunk)
            sms_start = sms_end
            sms_end = sms_end + sms_size
        final_chunk = text[sms_start:]
        chunk_array.append(final_chunk)
        for i in range(0, len(chunk_array) - 1):
            chunk_array[i] = chunk_array[i] + \
                "\n\n⬇️ (" + str(i + 1) + " of " + str(len(chunk_array)) + ") ⬇️" + chunk_note

        # print("\n\nChunk Array formmated: \n\n" + str(chunk_array) + "\n\n")
        chunk_result = (len(chunk_array), chunk_array)
        return chunk_result

def sizing_sms_chunks(text, send_all_chunks):
    print("Optimizing SMS chunking")
    try:
        chunk_set = make_sms_chunks(text, send_all_chunks)
    except BaseException:
        try:
            chunk_set = make_sms_chunks(text, send_all_chunks, 250)
            print("Triggered lower SMS chunking size @ 250")
        except BaseException:
            try:
                chunk_set = make_sms_chunks(text, send_all_chunks, 200)
                print("Triggered lower SMS chunking size @ 200")
            except BaseException:
                try:
                    chunk_set = make_sms_chunks(text, send_all_chunks, 150)
                    print("Triggered lower SMS chunking size @ 150")
                except BaseException:
                    try:
                        chunk_set = make_sms_chunks(text, send_all_chunks, 100)
                        print("Triggered lower SMS chunking size @ 100")
                    except BaseException:
                        chunk_set = make_sms_chunks(text, send_all_chunks, 50)
                        print("Triggered lower SMS chunking size @ 50")
    return chunk_set


def enter_message(message, gv_message, browser):
    JS_ADD_TEXT_TO_INPUT = """
    var elm = arguments[0], txt = arguments[1];
    elm.value += txt;
    elm.dispatchEvent(new Event('change'));
    """
    browser.execute_script(JS_ADD_TEXT_TO_INPUT, message, gv_message)
    time.sleep(2)
    message.send_keys(Keys.CONTROL, 'a')
    message.send_keys(Keys.CONTROL, 'c')
    message.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)
    message.send_keys(Keys.RETURN)
    time.sleep(2)


def delete_previous_conversation(browser):
    conversation_box = browser.find_element_by_xpath("""//*[@id="messaging-view"]/div/div/md-content/div/gv-conversation-list/md-virtual-repeat-container/div/div[2]/div[1]/div/gv-text-thread-item/gv-thread-item/div/div[2]/div/gv-annotation
""")
    conversation_box.click()
    time.sleep(1)
    settings_dots = browser.find_element_by_xpath(
        """//*[@id="messaging-view"]/div/div/md-content/gv-thread-details/div/div[1]/gv-message-list-header/div/div[2]/div/md-menu/button/md-icon""")
    settings_dots.click()
    time.sleep(1)
    browser.find_element_by_xpath("""//button[@aria-label='Delete']""").click()
    time.sleep(1)
    try:
        browser.find_element_by_xpath(
            """//md-checkbox[@aria-label='I understand']""").click()
    except BaseException:
        pass
    time.sleep(2)
    browser.find_element_by_xpath(
        """//button[@gv-test-id='delete-thread-confirm']""").click()


# def send_reply(gv_number, gv_message, browser):
#     print("Browser inside SendReply: " + str(browser))
#     message = setup_message(gv_number, browser)
#     try:
#         chunk_set = make_sms_chunks(gv_message)
#     except BaseException:
#         try:
#             chunk_set = make_sms_chunks(gv_message, 250)
#             print("Triggered lower SMS chunking size @ 250")
#         except BaseException:
#             try:
#                 chunk_set = make_sms_chunks(gv_message, 200)
#                 print("Triggered lower SMS chunking size @ 200")
#             except BaseException:
#                 try:
#                     chunk_set = make_sms_chunks(gv_message, 150)
#                     print("Triggered lower SMS chunking size @ 150")
#                 except BaseException:
#                     try:
#                         chunk_set = make_sms_chunks(gv_message, 100)
#                         print("Triggered lower SMS chunking size @ 100")
#                     except BaseException:
#                         chunk_set = make_sms_chunks(gv_message, 50)
#                         print("Triggered lower SMS chunking size @ 50")

#     for i in range(0, len(chunk_set)):
#         time.sleep(1)
#         enter_message(message, chunk_set[i], browser)
#         time.sleep(2)
#     delete_previous_conversation(browser)


def setup_message(gv_number, browser):
    initiate_Message = browser.find_element_by_xpath(
        """//*[@id="messaging-view"]/div/div/md-content/div/div/div""")
    initiate_Message.click()
    time.sleep(2)

    toForm = browser.find_element_by_xpath(
        """//*[@id="messaging-view"]/div/div/md-content/gv-thread-details/div/div[1]/gv-recipient-picker/div/md-content/md-chips/md-chips-wrap/div/div/input""")
    toForm.click()
    toForm.send_keys(gv_number)
    toForm.send_keys(Keys.ARROW_DOWN)
    time.sleep(1)
    toForm.send_keys(Keys.RETURN)
    time.sleep(1)
    time.sleep(2)
    message = browser.find_element_by_xpath(
        """//textarea[@aria-label='Type a message']""")
    message.click()
    return message
