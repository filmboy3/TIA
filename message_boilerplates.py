

def send_full_text_message(result, sender_info, topic):
    tia_sign_off = "\n\n--😘,\n✨ Tia ✨\nText" \
            " 📲 me another request, " + str(
            sender_info['name']) + ", or text HELP"
    result = "I've got some " + str(topic) + " info for you, " + str(
        sender_info['name']) + "!\n\n" + result + tia_sign_off
    try:
        send_message(sender_info['from'], result, sender_info)
        print("Responded to request successfully: " + str(topic))
    except BaseException:
        print("Error, was unable to respond to request")
        mark_as_error(sender_info)
        result = "I'm so sorry, " + str(sender_info['name']) + ", " \
            "but I'm having a tough time with your " + str(
            topic) + " request. Please try again." + tia_sign_off
        send_message(sender_info['from'], result, sender_info)
    time.sleep(1)

def send_error_text(text):
    return "\n😟 I hate to be the bearer of bad 🗞️, but right now, your " + \
        text + " request didn't work ... 🙏 try again!"