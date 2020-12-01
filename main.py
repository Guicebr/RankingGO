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
from telegram import Update
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup,)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext, CallbackQueryHandler)

from CREDENTIALS import BOT_TOKEN

from Database.dbhelper import DBHelper
from Plugins.visionocr import *

# Enable logging
from Plugins import visionocr
from Modelo.UserData import UserData

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='example.log')

logger = logging.getLogger(__name__)

dbconn = DBHelper()

REGISTER_VAL, NICK, NICK_VAL = range(3)

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

    keyboard = []

    user = update.message.from_user
    nickctx = str(context.user_data["nick"])
    photo_file = update.message.photo[-1].get_file()
    userdbid = 0

    ocr_user = visionocr.ocr_register(photo_file, nickctx)
    print("ocr_return nickval ", str(ocr_user))

    context.user_data["ocr_user"] = ocr_user

    # Si nick no valido comunicar al usuario y cancelar registro
    if ocr_user.nick is None:
        text = "Nick no válido, vuelva a intentarlo con el comando /registro"
        update.message.reply_text(text)
        return ConversationHandler.END

    # Si nick valido comprobar si existe en la bd o no y obtener un userid
    else:
        try:
            # Buscar usuario en la BD y conseguir userdbid
            dbconn = DBHelper()
            index = dbconn.get_user_tgid(user.id)
            #print("Len Index", len(index))
            if len(index) >= 1:
                userdbid = index[0][0]
            else:
                # Añadimos usuario a la BD y obtenemos su userdbid
                print("AddUser DB")
                userdbid = dbconn.add_user(ocr_user.nick, user.id)
        except:
            print("Error desconocido")
        finally:
            print(userdbid)
            dbconn.close()

    context.user_data["userdbid"] = userdbid
    txt = 'Please check the following values:'
    for i in ocr_user.getDict():
        if ocr_user[i] is not None:
            value = str(i)+": "+str(ocr_user[i])
            keyboard.append([InlineKeyboardButton(str(value)),
                            InlineKeyboardButton("✅", callback_data='i')])

    keyboard.append([InlineKeyboardButton("Finish", callback_data='0')])

    #TODO: Validacion por parte del usuario los datos obtenidos mediante OCR, cada uno.
    #TODO: Insertar datos en la BD e indicar al Usuario


    text = "Nickval " + ocr_user.nick +" "+ str(userdbid) +" "+ str(ocr_user)
    update.message.reply_text(text)

    return REGISTER_VAL


def register_val(update, context):


    print("UserDBID", str(context.user_data["userdbid"]))
    print("OCR_USER", str(context.user_data["ocr_user"]))
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("UserData %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    #query.edit_message_text(text=f"Selected option: {query.data}")



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
            NICK_VAL: [MessageHandler(Filters.photo, nickval)],
            REGISTER_VAL: [CallbackQueryHandler(register_val)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling(allowed_updates=[])

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
