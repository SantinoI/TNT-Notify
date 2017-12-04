#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging, requests, re, time, os, datetime
from pprint import pprint
from xml.etree import ElementTree

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

TOKEN = open('token.conf', 'r').read().replace("\n", "")
LINK = "http://www.tntvillage.scambioetico.org/rss.php?c=29&p="

logger = logging.getLogger(__name__)

def help(bot, update):    
    update.message.reply_text('Use /set <name> to insert a new serie\nUse /unset to show the list of your series and delete one\nUse /last <number> to show the last number series uploaded\nUse /chek to check if there are updates')

def set(bot, update, args, job_queue, chat_data):
    if len(args) >= 1:
        chat_id = update.message.chat_id
        name = [y for y in [re.sub('[^0-9a-zA-Z]+', '', x.lower()) for x in args] if y]    
        
    
        if 'job' not in chat_data:   
            job = [
                job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(9, 00, 00),  context=chat_id, name='At 09:00'),
                job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(11, 00, 00), context=chat_id, name='At 11:00'),
                job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(15, 00, 00), context=chat_id, name='At 15:00'),
                job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(18, 00, 00), context=chat_id, name='At 18:00'),
                job_queue.run_daily(lambda bot, job: check(bot, job, chat_data), datetime.time(20, 00, 00), context=chat_id, name='At 20:00')
            ]
            chat_data['job'] = job

        chat_data[" ".join(name)] = {
            "title": name,
            "lastNotify": [],
            "originalName": " ".join(args)
        }

        update.message.reply_text('Serie successfully set!')
    else:
        update.message.reply_text('Usage: /set <name>')

def last(bot, update, args):
    try:
        times = args[0]
        if int(times) >= 1 and int(times) <= 80 :
            r = requests.get(LINK + times)
            if(r.status_code == 200):
                tree = ElementTree.fromstring(r.content)
                for neighbor in tree.iter('item'):
                    title = neighbor.find('title').text
                    link = neighbor.find('enclosure').get('url')
                    descr = neighbor.find('description').text.split("<BR>")
                    description = ""
                    for d in descr:	
                        if "torrent data" in d.lower():
                            description = d.split(":")[-1].strip() 
                    bot.send_message(update.message.chat_id, text="<b>Serie TV:</b>\n{}\n<b>Info:</b>\n{}\n<a href='{}'>Link Torrent</a>".format(title.encode("utf-8"), description.encode("utf-8"), link), parse_mode="HTML")
        else:
            update.message.reply_text('The number must be between 1 and 80')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /last <number>')

def _check(bot, update,job_queue, chat_data):
    chat_id = update.message.chat_id
    job_queue.run_once(lambda bot, job: check(bot, job, chat_data),1,context=chat_id)


def check(bot, job, chat_data):
    for key, value in chat_data.items():
        if key != 'job':
            r = requests.get(LINK + "30")
            if(r.status_code == 200):
                tree = ElementTree.fromstring(r.content)
                for neighbor in tree.iter('item'):
                    title = neighbor.find('title').text
                    if not title in value["lastNotify"]:
                        if all(ext in re.sub('[^0-9a-zA-Z]+', '', title.lower()) for ext in value["title"]):
                            link = neighbor.find('enclosure').get('url')
                            descr = neighbor.find('description').text.split("<BR>")
                            description = ""
                            for d in descr:	
                                if "torrent data" in d.lower():
                                    description = d.split(":")[-1].strip() 
                            bot.send_message(job.context, text="<b>Serie TV Found:</b>\n{}\n<b>Info:</b>\n{}\n<a href='{}'>Link Torrent</a>".format(title.encode("utf-8"), description.encode("utf-8"), link), parse_mode="HTML")
                            torRequest = requests.get(link)
                            if(torRequest.status_code == 200):
                                fileName = torRequest.headers.get('Content-Disposition').split(";")[1].strip().split("=")[1].strip().replace('"','')
                                with open(fileName, 'wb') as f:
                                    f.write(torRequest.content)    
                                bot.send_document(job.context, document=open(fileName, 'rb'))
                                os.remove(fileName)
                                value["lastNotify"].append(title)

def unset(bot, update, chat_data):
    if len(chat_data) >= 2:    
        keyboard = []
        for key, value in chat_data.items():
            if key != 'job':
                keyboard.append([InlineKeyboardButton(value["originalName"], callback_data=key)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Select the serie to delete:', reply_markup=reply_markup)
    else: 
        update.message.reply_text("You haven't a serie. Use /set <name>")

def button(bot, update, chat_data):
    query = update.callback_query
    del chat_data[query.data]

    bot.edit_message_text(text="Serie TV Delete: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    
    if len(chat_data) == 1:
        for job in chat_data['job']:
            job.schedule_removal()
        del chat_data['job']

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('unset', unset, pass_chat_data=True))
    dp.add_handler(CallbackQueryHandler(button, pass_chat_data=True))
    dp.add_handler(CommandHandler("last", last, pass_args=True))
    dp.add_handler(CommandHandler("set", set, pass_args=True, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("check",_check, pass_job_queue=True, pass_chat_data=True))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()


