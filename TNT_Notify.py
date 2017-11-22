#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import requests
import re
from pprint import pprint
from xml.etree import ElementTree

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):    
    update.message.reply_text('Insert /set <Name> to insert a new serie')

def set(bot, update, args, job_queue, chat_data):
    chat_id = update.message.chat_id
    r = requests.get('http://www.tntvillage.scambioetico.org/rss.php?c=29&p=40')
    if(r.status_code == requests.codes.ok):
        tree = ElementTree.fromstring(r.content)
        for neighbor in tree.iter('item'):
            args = [re.sub('[^0-9a-zA-Z]+', '', x.lower()) for x in args]
            if all(ext in re.sub('[^0-9a-zA-Z]+', '',neighbor.find('title').text.lower()) for ext in args):
                print(neighbor.find('title').text.encode("utf8"))

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater('353012747:AAGwaGCDPPorx1CaBgS90DWpnIngPcaP-5E')
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True, pass_chat_data=True))


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()


