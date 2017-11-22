#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import requests
from pprint import pprint
from xml.etree import ElementTree

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    print("Ciao")
    update.message.reply_text('Insert /set <Name> to insert a new serie')




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


''' 

r = requests.get('http://www.tntvillage.scambioetico.org/rss.php?c=29&p=40')
if(r.status_code == requests.codes.ok):
	tree = ElementTree.fromstring(r.content)
	for neighbor in tree.iter('item'):
		print(neighbor.find('title').text)
'''