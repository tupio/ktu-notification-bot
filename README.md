# KTU Notification Bot

[![GitHub issues](https://img.shields.io/github/issues/tupio/ktu-notification-bot)](https://github.com/tupio/ktu-notification-bot/issues)
[![GitHub forks](https://img.shields.io/github/forks/tupio/ktu-notification-bot)](https://github.com/tupio/ktu-notification-bot/network)
[![GitHub stars](https://img.shields.io/github/stars/tupio/ktu-notification-bot)](https://github.com/tupio/ktu-notification-bot/stargazers)
[![GitHub license](https://img.shields.io/github/license/tupio/ktu-notification-bot)](https://github.com/tupio/ktu-notification-bot/blob/master/LICENSE)

[This bot]() scrapes [KTU Website](https://ktu.edu.in/eu/core/announcements.htm) and publishes a new post at [KTU Notifications](https://t.me/KTU_RC/) telegram channel.

> Consider placing a :star: for this repo :smile:.

## Status

Instances: **3(known)** 

Total Subscriber Count: **17500+**

Links:
* [KTU Notifications](https://t.me/KTU_RC) This is maintained by me and contains no Ads.
* [KTU Official Notification System](https://t.me/apjktustudents)
* [Ktu study materials](http://t.me/ktustudymaterials)


### Disclaimer
Polling frequently can harm the site, and consume bandwidth of the original site.

## Install & Development 

Before you start with this repository, please make sure that you have installed python3 and postgresql. If not run the following command if you are on Linux or refer respective documentation of your distribution.

`sudo apt-get install postgresql python3`

1. Clone the repo to your local machine.

  ```bash
  git clone https://github.com/tupio/ktu-notification-bot.git
  ```
 
2. Change to `ktu-notification-bot` directory.

  ```bash
  cd ktu-notification-bot
  ```
 
3. Run the following command to install dependencies.
 
  ```bash
  pip install -r requirements.txt
  ```
 
 4. Add environmental variables
 > Replace the contents in angled brakets with appropriate values.
 
 ```bash
   export DATABASE_URL=postgres://$(whoami)
   export PRIVATE_ID=<Enter your telegram ID(This is a number and is not your username or phonenumber)>
   export CHANNEL_ID=<Add your channel ID here(give private id if only for private use)>
   export STATUS=<DEBUG/RELEASE>
   export BOT_ID=<your bot id here>
   ```
 
 5. Create a table with the name `hashes` with one column.
 
 6. Run the bot using
 ```bash
 python scrapper.py
 ```


## Contribute
  I like this bot to be a community-driven and non-profit, hence I can't do it alone. An active contribution in terms of the following can be given.
 
  ### 1. Development of Bot
  The bot requires a huge improvement both in terms of efficiency and functionality.
  
  1. Add guides for different aspects.
  2. Add a personal notification feature.
  3. Increase reliability in terms of delivering notifications.

  ### 2. Combine like-minded endeavors 
  It has been observed that there are many similar ideas of non-profit contributions like bots and channels all over the place. Consider merging it under one umbrella.
  
  ### 3. Support 
  You could support by joining [this channel](https://t.me/KTU_RC/), add this bot to your group or channel(pull a request or ping [me](https://t.me/tupio) with your group/channel id after adding to the same.)
  
  ### 4. Donate Or Sponsor
   I'm currently limited to the free quota of the server to maintain the system. You could donate to me to upgrade to a paid server thus making room for further development. All the donator names will be mentioned on this page.
   
## License 
 This project is under MIT License.
 Use for educational purposes only.
