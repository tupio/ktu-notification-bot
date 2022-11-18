# MIT License

# Copyright (c) 2021 Denil C Verghese

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import re
import json
import time
import hashlib
import requests
import psycopg2
import telegram
import urllib.parse
from bs4 import BeautifulSoup, Comment
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# __________________________ CONFIG AREA _______________________

# This will prevent sending messages to channel during development
debug = True

# Time  delay it will wake and and check for new notification
sleep_time = 300  # seconds.

# Whatsapp forward message
wa_header = "🔈 "
wa_footer = ".\n ------------------------- \nShared from *KTU Notification Channel* \n👉 Join Now!  https://t.me/KTU_RC \n⚡️ *No Ads* \n🔸 *Share to your friends* "

# Telegram Message
tl_footer = "---\n 👉 Join: https://t.me/KTU\\_RC \n🔸 No Ads⚡️"
button_text = "Visit KTU 🌐"
button_link = "https://ktu.edu.in/eu/core/announcements.htm"

# _________________________  END OF CONFIG _________________________

# TODO : Implemnt a error detection and report system
error_val = ""

bot = telegram.Bot(token=os.environ['2145285286:AAHg82FlEBh4rFPTx1TuOFj4QhuEcUp-ygY'])
CHANNEL_ID = os.environ['807251865']
PRIVATE_ID = os.environ['807251865']
DATABASE_URL = os.environ['DATABASE_URL']
STATUS = os.environ['STATUS']

url_prefix = "https://ktu.edu.in"
url = "https://ktu.edu.in/eu/core/announcements.htm"

try:
    debug = "DEBUG" in STATUS
except:
    pass


def log(message):
    print(message)


def bot_log(message):
    bot.send_message(chat_id=PRIVATE_ID, text=message,
                     disable_notification=False,
                     parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)


def get_msg_hashes(cur):
    cur.execute("SELECT * FROM hashes;")
    data = convert_to_list(cur.fetchall())
    log(str(data))
    if (data is None or len(data) == 0) and not debug:
        bot_log("*Read From DB Failed*")
        exit(1)
    elif debug:
        return []
    return data


def save_msg_hash(hashes, conn, cur):
    log("Saving :" + str(hashes))
    if debug:
        cur.execute("delete FROM hashes;")
        for _hash in hashes:
            cur.execute("INSERT INTO hashes VALUES (%s)", (_hash, ))
            conn.commit()
    else:
        if hashes != None:
            cur.execute("INSERT INTO hashes VALUES (%s)", (hashes, ))
            conn.commit()
    log("Saved")


def convert_to_list(tip):
# converts result tuples into a dict
    data = []
    for x in tip:
        data.append(x[0])
    return data


def remove_last(s, old, new, occurrence):
# removes link text from the bottom position since it will be added as buttons
    li = s.rsplit(old, occurrence)
    return new.join(li)

def build_menu(buttons, n_cols):
# Builds the button menu for links
    menu = [buttons[sd:sd + n_cols] for sd in range(0, len(buttons), n_cols)]
    return menu


def send_notification(notification, button_list, enable_preview_i):
    disable_preview = enable_preview_i in "\n\n-"
    to = PRIVATE_ID
    if not debug:
        to = CHANNEL_ID
    try:
        bot.send_message(chat_id=to, text=notification +
                         enable_preview_i + tl_footer, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(
                             build_menu(button_list, n_cols=2)),
                         disable_web_page_preview=disable_preview)
        log("Message Sent")
        return True
    except telegram.error.TimedOut:
        log("Timeout trying again")
        bot.send_message(chat_id=to, text=notification +
                         enable_preview_i + tl_footer, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(
                             build_menu(button_list, n_cols=2)),
                         disable_web_page_preview=disable_preview)
        log("Message Sent")
        return True
    except telegram.error.BadRequest as e:
        bot_log(e.message)
        bot_log("\n\n `" + notification + enable_preview_i + tl_footer + "`")
        log(e.message)
        return False


def find_links(links, body):
    link_list = [InlineKeyboardButton(button_text, url=button_link)]
    for link in links:
        body = remove_last(body, link.text, "", 1)
        if "ktu.edu" in link["href"] or "http" in link["href"][:10] or "www." in link["href"]:
            temp_link = link["href"]
        else:
            temp_link = url_prefix + link["href"]
        link_list.append(InlineKeyboardButton(link.text, url=temp_link))
    return body, link_list


def get_first_pdf_link(links):
    if links is not None:
        for link in links:
            if ".pdf" in link["url"] or ".jpg" in link["url"]:
                temp = str(link["url"])\
                    .replace("(", "%28")\
                    .replace(")", "%29")  # encodes the '(' and ')'
                return "\n\n[-]("+temp+")"
    return "\n\n-"


def fetcher(conn, cur):
    hash_list = get_msg_hashes(cur)
    log("Connecting to website")
    try:
        website = requests.get(url).text
    except:
        log("Unable to access Website!")
        bot_log("*Unable to accesss Website*")

    if "Page Not Found" in website:
        log("Page not found")
        bot_log("*Unable to accesss Website*")
        exit(2)
    else:
        log("Connected Successfully")

    soup = BeautifulSoup(website, 'html.parser')
    all_notification = soup.findAll('tr')

    i = 0
    msg_hash_list = []
    for item in all_notification:
        contents = item.findAll('li')

        comments = contents[0].findAll(
            text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]

        contents = str(contents)\
            .replace("<br>", "\n")\
            .replace("<p>", "\n")\
            .replace("</p>", "")\
            .replace("<b>", "*")\
            .replace("</b>", "*#\n\n")\
            .replace("[", "")\
            .replace("]", "")\
            .replace("_", "\\_")

        souped = BeautifulSoup(contents, 'html.parser')
        body = ""
        for x in souped.find("li").findAll(text=True):
            x=str(x).replace("\r", "").replace("\t","").replace("\n","")
            x = re.sub(' +',' ',x)
            body = body + x
        body, links = find_links(item.findAll('a', href=True), body=body)
        body = body.replace("**", "").replace("#","\n").strip()
        body = re.sub('\n+', '\n', body)
        links.append(InlineKeyboardButton("WhatsApp It!", "https://api.whatsapp.com/send?&text=" + urllib.parse.quote(
            wa_header + body + wa_footer)))
        footer_pdf = get_first_pdf_link(links)
        if i < 10:
            msg_hash = (hashlib.md5(body.encode('utf-8')).hexdigest())
            if not debug:
                if not msg_hash in hash_list:
                    send_notification(wa_header + body, links, footer_pdf)
                    save_msg_hash(msg_hash, conn, cur)
            if debug:
                if not send_notification(wa_header + body, links, footer_pdf):
                    log("Message will not be sent")
                msg_hash_list.append(msg_hash)
        else:
            break
        i = i + 1
    if debug:
        save_msg_hash(msg_hash_list, conn, cur)


def main():
    if not debug:
        while True:
            log("Scanning for new")
            log("connecting to DB")
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cur = conn.cursor()
            log("Loading function")
            fetcher(conn, cur)
            log("Closing DB")
            cur.close()
            conn.close()
            log("Scan complete")
            time.sleep(sleep_time)
    else:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        fetcher(conn, cur)
        try:
            cur.close()
            conn.close()
        except:
            log("Already closed")


if __name__ == '__main__':
    if not debug:
        try:
            main()
        except Exception as e:
            log("main failed " + str(e))
    if debug:
        log("Debug mode")
        main()
