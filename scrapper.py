import time
import hashlib
import requests
import psycopg2
import os
import json
import telegram
import urllib.parse
from bs4 import BeautifulSoup, Comment
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import re
# __________________________ CONFIG AREA _______________________

debug = True                                                             # This will prevent sending messages to channel during development
sleep_time =300 #seconds.                                                # Time  delay it will wake and and check for new notification

# Whatsapp forward message
header = "🔈 "
footer2 =  ".\n ------------------------- \nShared from *KTU Notification Channel*"\
    " \n👉 Join Now!  https://t.me/KTU_RC \n⚡️ *No Ads* \n🔸 *Share to your friends* "

# Telegram Message
footer =  "---\n 👉 Join: https://t.me/KTU\\_RC \n🔸 No Ads⚡️"
button_text  = "Visit KTU 🌐"                                               
button_link = "https://ktu.edu.in/eu/core/announcements.htm" 

# _________________________  END OF CONFIG _________________________

# todo : Implemnt a error detection and report system
error_val = ""

bot = telegram.Bot(token=os.environ['BOT_ID'])
CHANNEL_ID = os.environ['CHANNEL_ID']
PRIVATE_ID = os.environ['PRIVATE_ID']
DATABASE_URL = os.environ['DATABASE_URL']
STATUS = os.environ['STATUS']

add_url = "https://ktu.edu.in"
url = "https://ktu.edu.in/eu/core/announcements.htm"

try:
	if "DEBUG" in STATUS:
		debug=True
	else:
		debug=False
except:
	pass


def log(message):
    print(message)
	
def getlist(cur):
    cur.execute("SELECT * FROM hashes;")
    data =convert(cur.fetchall())
    log(str(data))
    if (data is None and not debug) or ( len(data)==0 and not debug):
        bot.send_message(chat_id=PRIVATE_ID, text="*Read From DB Failed*", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
        exit(1)
    elif debug:
        return []
    return data

def save_msg_hash(listi,conn,cur):
    log("Saving :" + str(listi))
    if debug:
        cur.execute("delete FROM hashes;")
        for hash_val in listi:
            cur.execute("INSERT INTO hashes VALUES (%s)", (hash_val, ))
            conn.commit()
    else:
        if listi != None:
            cur.execute("INSERT INTO hashes VALUES (%s)", (listi, ))
            conn.commit()
    log("Saved")

def convert(tip):
	data =[]
	for x in tip:
			data.append(x[0])
	return data		

def remove_last(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def build_menu(buttons, n_cols):
    menu = [buttons[sd:sd + n_cols] for sd in range(0, len(buttons), n_cols)]
    return menu

def send_notification(notification, link_list4, enable_preview_i):
    disable_preview = False
    if enable_preview_i is None:
        disable_preview = True
        enable_preview_i = " "
    try:
        if debug:
            bot.send_message(chat_id=PRIVATE_ID, text= notification + enable_preview_i + footer,
                     reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                     disable_web_page_preview=disable_preview, parse_mode=telegram.ParseMode.MARKDOWN)
        if not debug:
            bot.send_message(chat_id=CHANNEL_ID , text=notification + enable_preview_i + footer, parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                        disable_web_page_preview=disable_preview)
        log("Message Sent")
        return True
    except telegram.error.TimedOut:
        log("Timeout trying again")
        if debug:
            bot.send_message(chat_id=PRIVATE_ID, text= notification  + enable_preview_i + footer,
                     reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                     disable_web_page_preview=disable_preview, parse_mode=telegram.ParseMode.MARKDOWN)
        if not debug:
            bot.send_message(chat_id=CHANNEL_ID , text=notification  + enable_preview_i + footer, parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                        disable_web_page_preview=disable_preview)
        log("Message Sent")
        return True
    except telegram.error.BadRequest as e:
        bot.send_message(chat_id=PRIVATE_ID, text= e.message ,
                    parse_mode=telegram.ParseMode.MARKDOWN)
        bot.send_message(chat_id=PRIVATE_ID, text= "\n\n `" + notification  + enable_preview_i + footer + "`" ,
                    parse_mode=telegram.ParseMode.MARKDOWN)
        log(e.message)
        return False

def find_links(links, body):
    link_list = [InlineKeyboardButton(button_text, url=button_link)]
    for link in links:
        body = remove_last(body, link.text, "", 1)
        if "ktu.edu" in link["href"] or "http" in link["href"][:10] or "www." in link["href"]:
            temp_link = link["href"]
        else:
            temp_link = add_url + link["href"]
        link_list.append(InlineKeyboardButton(link.text, url=temp_link))
    return body,link_list

def get_first_pdf_link(links):
    if links is not None:
        for link in links:
            if ".pdf" in link["url"]:
                return link["url"]
    return None

def main_function(conn,cur):
    hash_list = getlist(cur)
    log("Connecting to website")
    try:
        website = requests.get(url).text
    except:
        log("Unable to access Website!")
        bot.send_message(chat_id=PRIVATE_ID, text="*Unable to accesss Website*", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    if "Page Not Found" in website:
        log("Page not found")
        bot.send_message(chat_id=PRIVATE_ID, text="*Unable to accesss Website*", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
        exit(2)
    else:
        log("Connected Successfully")

    soup = BeautifulSoup(website, 'html.parser')
    all_notification = soup.findAll('tr')

    i = 0
    msg_hash_list =[]
    for item in all_notification:
        contents = item.findAll('li')

        comments = contents[0].findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        
        contents = str(contents)\
            .replace("<br>","\n")\
                .replace("<p>","\n")\
                    .replace("</p>","")\
                        .replace("<b>","*")\
                            .replace("</b>","*\n\n")\
                                .replace("[","")\
                                    .replace("]","")\
                                        .replace("_", "\\_")
                                        
                           
                                   
        temmmm=  BeautifulSoup(contents,'html.parser')   
        body = ""                                  
        for x in temmmm.find("li").findAll(text=True):
            body = body +  x
        body , links = find_links(item.findAll('a', href=True), body=body)
        body = body.replace("**","").strip()
        body = re.sub('\n+','\n',body)
        links.append(InlineKeyboardButton("WhatsApp It!", "https://api.whatsapp.com/send?&text=" + urllib.parse.quote(
            header + body +  footer2)))
        pdf_link = get_first_pdf_link(links)
        footer_pdf = None
        if pdf_link is not None:
            footer_pdf  = "\n\n[-]("+pdf_link+")" 
        if i < 10:
            msg_hash = (hashlib.md5(body.encode('utf-8')).hexdigest())
            if not debug:
            	if not msg_hash in hash_list:
                    send_notification(header + body, links, footer_pdf)
                    save_msg_hash(msg_hash,conn,cur)
            if debug:
                if not send_notification(header + body, links, footer_pdf):
                    log("Message will not be sent")
                msg_hash_list.append(msg_hash)
        else:
            break
        i = i + 1
    if debug:
        save_msg_hash(msg_hash_list,conn,cur)
    

def main():
    if not debug:
        while True:
            log("Scanning for new")
            log("connecting to DB" )
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cur = conn.cursor()
            log("Loading function")
            main_function(conn,cur)
            log("Closing DB")
            cur.close()
            conn.close()
            log("Scan complete")
            time.sleep(sleep_time)            
    else:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
        main_function(conn,cur)
        try:
            cur.close()
            conn.close()
        except:
            log("Already closed")


if __name__ == '__main__':
    if not debug:
        try:
            main()
        except Exception as e :
            log("main failed " + str(e))
            pass
    if debug:
        log("Debug mode")
        main()
        
