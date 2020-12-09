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


import telegram
import collections
from CREDENTIALS import BOT_TOKEN

from telegram import Update
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup,)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackContext, CallbackQueryHandler)
import logging

from Plugins import visionocr
from Database.dbhelper import DBHelper
from Plugins.visionocr import *
from Modelo.TypeRanking import bool_to_icon
from Modelo.TypeRanking import typeranking_enum as tr_enum
from Modelo.UserData import UserData

# Enable logging
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
    """ Show last experience data writed in telegram chat"""
    update.message.reply_text("Tu experiencia es " + context.args[0])


def register(update, context):
    """Start the register proccess, ask user for nick"""
    user = update.message.from_user

    text = 'Send me your nickname in PokemonGO.'
    logger.info("Inicio Registro: %s\n"
                "ID: %s", user.first_name, user.id)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return NICK


def nick(update, context):
    """Save users nick in context data and ask the user to send you a photo."""
    user = update.message.from_user
    logger.info("Nombre %s: Nick %s", user.first_name, update.message.text)
    context.user_data["nick"] = update.message.text

    text = "Is " + update.message.text + " your nickname?\n" \
                                         "Send me a photo at your profile account to verify"
    update.message.reply_text(text)

    return NICK_VAL


def nickval(update, context):
    """Receive photo from user, save/get User from DB, and create ValidationForm. """
    #Initialize vars
    keyboard = []
    userdbid = 0

    user = update.message.from_user
    nickctx = str(context.user_data["nick"])
    photo_file = update.message.photo[-1].get_file()

    #Get data from OCR and save in context
    ocr_user = visionocr.ocr_register(photo_file, nickctx)
    #print("ocr_return nickval ", str(ocr_user))
    context.user_data["ocr_user"] = ocr_user

    # Check validity of user nick
    if ocr_user.nick is None:
        # If invalid nick, notify user and cancel register
        text = "Nick no válido, vuelva a intentarlo con el comando /registro"
        update.message.reply_text(text)
        return ConversationHandler.END
    else:
        # If nick is valid, check if it exists in the database and get/save to obtain userid
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
    txt = 'Nick registrado: '+str(nickctx)
    update.message.reply_text(txt)

    # Save data in user context and prepare validation form
    ocr_user = ocr_user.getDict()
    ocr_user.pop("nick")
    context.user_data["ocr_user"] = collections.OrderedDict(ocr_user)
    context.user_data["ocr_user_valid"] = {k: True for k in context.user_data["ocr_user"]}

    ocr_user = context.user_data["ocr_user"]
    ocr_user_valid = context.user_data["ocr_user_valid"]

    #Validation by the user of each data obtained through OCR
    txt = 'Verifica los siguientes datos por favor:'
    print(ocr_user)
    for type_rank in ocr_user:
        if ocr_user[type_rank] is not None:
            value = str(type_rank) + ": " + str(ocr_user[type_rank]) + bool_to_icon[int(ocr_user_valid[type_rank])]
            cb_data = list(ocr_user.keys()).index(type_rank)

            keyboard.append([InlineKeyboardButton(str(value), callback_data=cb_data)])

    keyboard.append([InlineKeyboardButton("Finish", callback_data='finish')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(txt, reply_markup=reply_markup)

    return REGISTER_VAL


def register_val(update, context) -> None:
    """Updates the form and stores the data, based on user actions"""

    query = update.callback_query

    ocr_user_valid = context.user_data["ocr_user_valid"]
    ocr_user = context.user_data["ocr_user"]
    userbdid = context.user_data["userdbid"]


    print(query.message)

    # Check callback type
    callback_type = query.data
    if callback_type.isnumeric():
        # If numeric callback Store data in context and Update form
        keyboard = query.message.reply_markup['inline_keyboard'].copy()

        type_rank = list(ocr_user_valid.keys())[int(callback_type)]
        ocr_user_valid[type_rank] = not ocr_user_valid[type_rank]

        # TODO Traducir i
        txt = str(type_rank) + ": " + str(ocr_user[type_rank]) + bool_to_icon[int(ocr_user_valid[type_rank])]
        cb_data = list(ocr_user.keys()).index(type_rank)
        keyboard[int(callback_type)][0] = InlineKeyboardButton(str(txt), callback_data=cb_data)
        # print(keyboard[int(data)][0]['text'])
        # print(str(query))
        query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))

        query.answer(str(type_rank))
    elif callback_type == "finish":
        # If callback is finish Store each data DB and notify user
        try:
            dbconn = DBHelper()
            for type in ocr_user:
                if ocr_user_valid[type] is True and type != "nick":
                    dbconn.add_ranking_data(userbdid, tr_enum[type], ocr_user[type])
            query.answer("Datos guardados")
            query.edit_message_text(text=f"Datos Guardados")
        except:
            print("Error desconocido")
        finally:
            dbconn.close()
    else:
        print("Callback no programado ", str(callback_type))

    #print(str(ocr_user))
    #print(str(ocr_user_valid))

    #query.message.reply_text(str(query.data))
    # print(query.message.reply_markup)
    # query.edit_message_text(text=f"Selected option: {query.data}")

    return ConversationHandler.END

def screenshot_handler(update, context) -> None:
    """ Function comment"""
    userbdid = 0
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()

    # Verificar si el usuario esta registrado -> userbdid
    try:
        # Buscar usuario en la BD y conseguir userdbid
        dbconn = DBHelper()
        result = dbconn.get_user_tgid(user.id)
        # print("Len Index", len(index))
        if len(result) >= 1:
            userdbid = int(result[0][0])
        else:
            txt = "Usuario no registrado ejecute el comando registro"
            update.message.reply_text(txt)
    except:
        print("Error desconocido")
    finally:
        print(userdbid)
        dbconn.close()

    #TODO: Obtener tipo_ranking y cantidad
    ocr_data = visionocr.ocr_screenshot(photo_file)

    #TODO: Validar?
    #TODO: Salvar datos y Notificar al usuario

    # Get data from OCR and save in context
    #ocr_user = visionocr.ocr_register(photo_file, nickctx)
    pass

def cancel(update, context):
    """Cancel command."""
    user = update.message.from_user
    logger.info("UserData %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def main():
    """Start the bot."""

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
    #dp.add_handler(CommandHandler("experience", experience))

    #Registramos cuando el usuario pulsa un boton del formulario de registro
    updater.dispatcher.add_handler(CallbackQueryHandler(register_val))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, screenshot_handler))

    # Add conversation handler with the states NICK, NICK_VAL, REGISTER_VAL
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("registro", register)],

        states={
            NICK: [MessageHandler(Filters.text & ~Filters.command, nick)],
            NICK_VAL: [MessageHandler(Filters.photo & ~Filters.command, nickval)],
            REGISTER_VAL: [CallbackQueryHandler(register_val)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot, añadimos allowed_update para poder editar lo mensajes
    updater.start_polling(allowed_updates=[])

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
