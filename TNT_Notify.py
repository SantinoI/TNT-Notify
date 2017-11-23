#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging, requests, re, time, os, datetime
from pprint import pprint
from xml.etree import ElementTree

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

TOKEN = open('token.conf', 'r').read().replace("\n", "")

logger = logging.getLogger(__name__)

def start(bot, update):    
    update.message.reply_text('Insert /set <Name> to insert a new serie')

def set(bot, update, args, job_queue, chat_data):
    chat_id = update.message.chat_id
    name = [y for y in [re.sub('[^0-9a-zA-Z]+', '', x.lower()) for x in args] if y]    
    job = [
        job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(9, 00, 00),  context=chat_id, name='At 09:00'),
        job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(11, 00, 00), context=chat_id, name='At 11:00'),
        job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(15, 00, 00), context=chat_id, name='At 15:00'),
        job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(18, 00, 00), context=chat_id, name='At 18:00'),
        job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(20, 00, 00), context=chat_id, name='At 20:00')
    ]

    '''
    For testing
    job = [
        job_queue.run_repeating(lambda bot, job: check(bot, job, chat_data), 10, context=chat_id, name='At 09:00')
    ]

    '''

    chat_data['job'] = job
    chat_data[" ".join(name)] = {
        "title": name,
        "lastNotify": [],
        "originalName": " ".join(args)
    }

    update.message.reply_text('Serie successfully set!')

def check(bot, job, chat_data):
    for key, value in chat_data.items():
        if key != 'job':
            r = requests.get('http://www.tntvillage.scambioetico.org/rss.php?c=29&p=40')
            if(r.status_code == 200):
                tree = ElementTree.fromstring(r.content)
                for neighbor in tree.iter('item'):
                    title = neighbor.find('title').text
                    if not title in value["lastNotify"]:
                        if all(ext in re.sub('[^0-9a-zA-Z]+', '', title.lower()) for ext in value["title"]):
                            link = neighbor.find('enclosure').get('url')
                            bot.send_message(job.context, text="*Serie TV Trovata:*\n{}\n[Link Torrent]({})".format(title, link), parse_mode="Markdown")    
                            torRequest = requests.get(link)
                            if(torRequest.status_code == 200):
                                fileName = torRequest.headers.get('Content-Disposition').split(";")[1].strip().split("=")[1].strip().replace('"','')
                                with open(fileName, 'wb') as f:
                                    f.write(torRequest.content)    
                                bot.send_document(job.context, document=open(fileName, 'rb'))
                                os.remove(fileName)
                                value["lastNotify"].append(title)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(TOKEN)
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


