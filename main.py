#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from CREDENTIALS import BOT_TOKEN

from Database.dbhelper import DBHelper
from Plugins.visionocr import *

# Enable logging
from Plugins import visionocr

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='example.log')

logger = logging.getLogger(__name__)

dbconn = DBHelper()

NICK, NICK_VAL = range(2)

#DEBUG = 1

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""

    reply_keyboard = [['/registro', '/cancel', '/experience']]
    text = 'Hi! My name is RankingGo Bot. ' \
           'Send /register to register in my database.\n\n' \
           'Send /experience num to save your experience.\n\n' \
           'Send /cancel to stop talking to me.\n\n'
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def help_command(update, context):
    """Send a message when the command /help is issued."""
    text = 'Help!' \
           'Send /registro to register in my database.\n\n' \
           'Send /experience num to save your experience.\n\n' \
           'Send /cancel to stop talking to me.\n\n'
    update.message.reply_text(text)


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def experience(update, context):
    """ Show last experience data."""
    update.message.reply_text("Tu experiencia es " + context.args[0])


"""
def sumar(update, context):
    try:
        num1 = int(context.args[0])
        num2 = int(context.args[1])
        sum = num1+num2
        update.message.reply_text("La suma es "+ str(sum))

    except(ValueError):
        update.message.reply_text("Por favor utilice 2 números") 
"""


def register(update, context):
    user = update.message.from_user

    text = 'Send me your nickname in PokemonGO.'
    logger.info("Inicio Registro: %s\n"
                "ID: %s", user.first_name, user.id)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return NICK


def nick(update, context):
    user = update.message.from_user
    logger.info("Nombre %s: Nick %s", user.first_name, update.message.text)
    context.user_data["nick"] = update.message.text
    text = "Is " + update.message.text + " your nickname?\n" \
                                         "Send me a photo at your profile account to verify"
    update.message.reply_text(text)

    return NICK_VAL


def nickval(update, context):
    #reply_keyboard = [['/registro', '/cancel', '/experience']]
    #message = update.message

    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()

    try:
        ocr_text = visionocr.ocr_register(photo_file, context.user_data["nick"])
        context.user_data["ocr_text"] = ocr_text
        print("ocr_return nickval ", str(ocr_text))

        personid = dbconn.add_user(ocr_text[nick], user.id)
        text = "Nickval " + ocr_text[nick] + str(ocr_text)
        update.message.reply_text(text)
    except:
        logger.info("Error OCR nickval")

    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("UserData %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    # Para mandar mensajes a un canal
    # bot.send_message(channel_id, text)

    # Para mandar mensajes a un usuario por privado
    # update.message.reply_text(text)

    bot = telegram.Bot(token=BOT_TOKEN)
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # command
    dp.add_handler(CommandHandler("experience", experience))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("registro", register)],

        states={
            NICK: [MessageHandler(Filters.text & ~Filters.command, nick)],
            NICK_VAL: [MessageHandler(Filters.photo, nickval)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
