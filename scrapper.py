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
# ___________ CONFIG AREA ________________

# This will prevent sending messages to channel during development
debug = True
# Time  delay it will wake and and check....
sleep_time =300 #seconds

quick_notification_link = "https://t.me/KTU_RC/14"
add_url = "https://ktu.edu.in"
url = "https://ktu.edu.in/eu/core/announcements.htm"

# Header footer shown for whatsapp link
header = " 📢 New *KTU* Notification: \n"
footer2 =  ".\n ------------------------- \n  Countinue reading: *KTU Notification Channel* \n  👉 Join Now!  https://t.me/KTU_RC  \n*Share to your friends* "

# Footer shown for Other messages
footer =  "\n ------------------------- \n "

# --------------END OF CONFIG--------------------

# todo : Implemnt a error detection and report system
error_val = ""

bot = telegram.Bot(token=os.environ['BOT_ID'])
CHANNEL_ID = os.environ['CHANNEL_ID']
PRIVATE_ID = os.environ['PRIVATE_ID']
DATABASE_URL = os.environ['DATABASE_URL']
STATUS = os.environ['STATUS']


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
	log("Saving")
	if listi != None or len(listi)>2:
		cur.execute("delete from hashes;")
		for hasyh in listi:
			cur.execute("INSERT INTO hashes VALUES (%s)", (hasyh, ))
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

def send_notification(notification, link_list4):
    try:
        if debug:
            bot.send_message(chat_id=PRIVATE_ID, text= notification,
                     reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                     disable_web_page_preview=True, parse_mode=telegram.ParseMode.MARKDOWN)
        if not debug:
            bot.send_message(chat_id=CHANNEL_ID , text=notification, parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                        disable_web_page_preview=True)
        log("Message Sent")
    except telegram.error.TimedOut as e:
        log("Timeout trying again")
        if debug:
            bot.send_message(chat_id=PRIVATE_ID, text= notification,
                     reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                     disable_web_page_preview=True, parse_mode=telegram.ParseMode.MARKDOWN)
        if not debug:
            bot.send_message(chat_id=CHANNEL_ID , text=notification, parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(build_menu(link_list4, n_cols=2)),
                        disable_web_page_preview=True)
        log("Message Sent")

def find_links(links, body):
    link_list = [InlineKeyboardButton("Quick Navigation Panel", url=quick_notification_link)]
    for link in links:
        body = remove_last(body, link.text, "", 1)
        if "ktu.edu" in link["href"]:
            temp_link = link["href"]
        else:
            temp_link = add_url + link["href"]
        link_list.append(InlineKeyboardButton(link.text, url=temp_link))
    return body,link_list

def main_function(conn,cur):
    msg_list = []
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
    for item in all_notification:
        contents = item.findAll('li')

        comments = contents[0].findAll(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]
        
        contents = str(contents)\
            .replace("<br>","\n")\
                .replace("<p>","\n")\
                    .replace("</p>","")\
                        .replace("<b>","*")\
                            .replace("</b>","*\n")\
                                .replace("[","")\
                                    .replace("]","")\
                                        .replace("_", "\\_")
                                   
        temmmm=  BeautifulSoup(contents,'html.parser')   
        body = ""                                  
        for x in temmmm.find("li").findAll(text=True):
            body = body +  x
        body , links = find_links(item.findAll('a', href=True), body=body)
        body = body.replace("**","").strip()
        links.append(InlineKeyboardButton("WhatsApp It!", "https://api.whatsapp.com/send?&text=" + urllib.parse.quote(
            body +  footer2)))
    
        if i < 5:
            msg_hash = (hashlib.md5(body.encode('utf-8')).hexdigest())
            msg_list.append(msg_hash)
            if not debug:
            	if not msg_hash in hash_list:
                	send_notification(body + footer, links)
            if debug:
                	send_notification(body + footer, links)
        else:
            break
        i = i + 1
    save_msg_hash(msg_list,conn,cur)

def main():
	if not debug:
		while True:
			try:
				log("Scanning for new")
				log("cinnecting to DB" )
				conn = psycopg2.connect(DATABASE_URL, sslmode='require')
				cur = conn.cursor()
				log("Loading function")
				main_function(conn,cur)
				log("Closing DB")
				cur.close()
				conn.close()
				log("Scan complete")
				time.sleep(sleep_time)
				error_val = ""
			except Exception as e:
				try:
					bot.send_message(chat_id=PRIVATE_ID, text="*Error* : `" + e + "`", disable_notification=False,
                         parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
				except e:
					pass
				log("Exception Occurred:" + e)
				time.sleep(sleep_time)
	else:
		conn = psycopg2.connect(DATABASE_URL, sslmode='require')
		cur = conn.cursor()
		main_function(conn,cur)
		try:
			cur.close()
			conn.close()
		except e:
			log("Already closed")


if __name__ == '__main__':
	try:
		if debug:
			log("Debug mode")
		main()
		
	except e:
		log("main failed" + e)
		pass

