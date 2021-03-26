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

# import collections
# import telegram

# GENERAL
import logging


# TELEGRAM
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
# PROYECTO
import users, medals, ranking, groups
from CREDENTIALS import BOT_TOKEN
from Database.dbhelper import DBHelper
from Modelo import TypeRankTranslator
from Modelo.TypeRanking import bool_to_icon
from Modelo.TypeRanking import typeranking_enum as tr_enum
from Plugins import common_func as c_func
from Plugins import visionocr
import constant as CONS

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='Logs/manin.log')

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.DEBUG, filename='Logs/manin.log')

logger = logging.getLogger(__name__)

# logger.debug('Este mensaje es sólo para frikis programadores como nosotros')
# logger.info('Este mensaje representa algo normal')
# logger.warning('Esto ya no es tan normal')
# logger.error('Deberías empezar a preocuparte')
# logger.critical('El bot está así X')

dbconn = DBHelper()

translator = TypeRankTranslator.TypeRankTranslator()
xml_lang_selector = "es"

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.message.from_user

    users.authuser(update, context)
    reply_keyboard = [['/registro', '/cancel', '/experience']]
    text = 'Hi! My name is RankingGo Bot. ' \
           'Send /register to register in my database.\n\n' \
           'Send /experience num to save your experience.\n\n' \
           'Send /cancel to stop talking to me.\n\n'
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    text = 'Help!' \
           'Send /registro to register in my database.\n\n' \
           'Send /experience num to save your experience.\n\n' \
           'Send /cancel to stop talking to me.\n\n'
    update.message.reply_text(text)


def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    print(update.message)
    update.message.reply_text(update.message.text)


def experience(update: Update, context: CallbackContext):
    """ Show last experience data writed in telegram chat"""
    update.message.reply_text("Tu experiencia es " + context.args[0])




# def obtener_datos_de_captura_registro(update: Update, context: CallbackContext):
#     # Initialize vars
#     keyboard = []
#     userdbid = authuser(update, context)
#     ocr_user = None
#
#     # Save data in user context and prepare validation form
#     # El nick ya ha sido registrado,vamos a pedir confirmación del resto de valores
#     # Creamos un diccionario de los datos-OCR y eliminamos el nick porque ya lo tenemos
#     ocr_user = ocr_user.getDict()
#     ocr_user.pop("nick")
#
#     # Creamos un dicionario ordenado de los datos-OCR y un otro diccionario, para almacenar la validez de cada dato
#     context.user_data[CONS.CONTEXT_VAR_OCRUSER] = collections.OrderedDict(ocr_user)
#     context.user_data[CONS.CONTEXT_VAR_OCRUSER_VALID] = {k: True for k in context.user_data[CONS.CONTEXT_VAR_OCRUSER]}
#
#     ocr_user = context.user_data[CONS.CONTEXT_VAR_OCRUSER]
#     ocr_user_valid = context.user_data[CONS.CONTEXT_VAR_OCRUSER_VALID]
#
#     # Validation by the user of each data obtained through OCR
#     # Creamos un teclado con los diferentes datos que hemos obtenido al hacer OCR
#     txt = 'Verifica los siguientes datos por favor:'
#     print(ocr_user)
#
#     keyboard = getKeyboardRegisterValidation(ocr_user, ocr_user_valid)
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     update.message.reply_text(txt, reply_markup=reply_markup)


def getKeyboardRegisterValidation(ocr_user, ocr_user_valid):
    keyboard = []
    for type_rank in ocr_user:
        if ocr_user[type_rank] is not None:
            value = str(type_rank) + ": " + str(ocr_user[type_rank]) + bool_to_icon[int(ocr_user_valid[type_rank])]
            cb_data = list(ocr_user.keys()).index(type_rank)

            keyboard.append([InlineKeyboardButton(str(value), callback_data=str(cb_data))])
    keyboard.append([InlineKeyboardButton("Finish", callback_data='finish')])

    return keyboard


# def register_val(update: Update, context: CallbackContext) -> None:
#     """Updates the form and stores the data, based on user actions"""
#
#     query = update.callback_query
#
#     ocr_user_valid = context.user_data[CONS.CONTEXT_VAR_OCRUSER_VALID]
#     ocr_user = context.user_data[CONS.CONTEXT_VAR_OCRUSER]
#     userbdid = context.user_data[CONS.CONTEXT_VAR_USERDBID]
#
#     # print(query.message)
#
#     # Check callback type
#     callback_type = query.data
#     if callback_type.isnumeric():
#         # If numeric callback Store data in context and Update form
#
#         type_rank = list(ocr_user_valid.keys())[int(callback_type)]
#         ocr_user_valid[type_rank] = not ocr_user_valid[type_rank]
#         keyboard = getKeyboardRegisterValidation(ocr_user, ocr_user_valid)
#
#         # TODO Traducir i
#         query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
#
#         query.answer(str(type_rank))
#     elif callback_type == "finish":
#         # If callback is finish Store each data DB and notify user
#         try:
#             dbconn = DBHelper()
#             for type in ocr_user:
#                 if ocr_user_valid[type] is True and type != "nick":
#                     print("Type ", str(type))
#                     dbconn.add_ranking_data(userbdid, tr_enum[type], ocr_user[type])
#             query.answer("Datos guardados")
#             query.edit_message_text(text=f"Datos Guardados")
#         except:
#             print("Error desconocido")
#         finally:
#             dbconn.close()
#     else:
#         print("Callback no programado ", str(callback_type))
#
#     # print(str(ocr_user))
#     # print(str(ocr_user_valid))
#
#     # query.message.reply_text(str(query.data))
#     # print(query.message.reply_markup)
#     # query.edit_message_text(text=f"Selected option: {query.data}")
#
#     return ConversationHandler.END
#

# def screenshot_handler(update: Update, context: CallbackContext) -> None:
#     """ Function comment"""
#     # TODO: Sustituir por authuser()
#     userbdid = 0
#     user = update.message.from_user
#     photo_file = update.message.photo[-1].get_file()
#
#     # Verificar si el usuario esta registrado -> userbdid
#     try:
#         # Buscar usuario en la BD y conseguir userdbid
#         dbconn = DBHelper()
#         result = dbconn.get_user_tgid(user.id)
#         # print("Len Index", len(index))
#         if len(result) >= 1:
#             userdbid = int(result[0][0])
#         else:
#             txt = "Usuario no registrado ejecute el comando registro"
#             update.message.reply_text(txt)
#     except:
#         print("Error desconocido")
#     finally:
#         print(userdbid)
#         dbconn.close()
#
#     # TODO: Obtener tipo_ranking y cantidad
#     ocr_data = visionocr.ocr_screenshot(photo_file)
#
#     # TODO: Validar?
#     # TODO: Salvar datos y Notificar al usuario
#
#     # Get data from OCR and save in context
#     # ocr_user = visionocr.ocr_register(photo_file, nickctx)
#     pass


def cancel(update: Update, context: CallbackContext):
    """Cancel command."""
    user = update.message.from_user
    logger.info("UserData %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def set_lang():
    # TODO:
    pass


def printcontextdata(update: Update, context: CallbackContext):
    print(context.user_data)

    print(update.message.from_user)
    chat_id = update.message.chat_id

    # print(update.getChat(chat_id))
    print(context.bot.getChat(chat_id))

    context.bot.send_message(
        chat_id=chat_id,
        text=str(context.user_data)
    )

def main():
    """Start the bot."""
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("userdata", printcontextdata))
    # TODO: Set lang
    dp.add_handler(CommandHandler("lang", set_lang))

    # GRUPO
    # El bot se fue/echaron de un grupo o Usuario abandona el grupo en el que esta el bot.
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, groups.groups_left_chat_member_handler))
    # El bot se unio a un grupo/canal/supergrupo no privado o Usuario se une a un grupo en el que se encuentra el bot.
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, groups.groups_new_chat_members_handler))

    # Un admin pide por el grupo info sobre los usuarios en el grupo, responde solo si eres admin
    dp.add_handler(CommandHandler(command="group_info", filters=Filters.chat_type.groups, callback=groups.group_info))

    # Registramos cuando el usuario pulsa un boton del formulario de registro
    # updater.dispatcher.add_handler(CallbackQueryHandler(register_val))



    # dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, screenshot_handler))

    # Add conversation handler with the states NICK, NICK_VAL
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("registro", users.register)],

        states={
            users.NICK: [MessageHandler(Filters.text & ~Filters.command, users.nick)],
            users.NICK_VAL: [MessageHandler(Filters.photo & ~Filters.command, users.nickval)],
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(conv_handler)
    manual_up_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("manual_up", medals.manual_up)],

        states={
            medals.TRTYPESEL: [MessageHandler(Filters.text & ~Filters.command, medals.manual_up_trtype)],
            medals.TYPE_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, medals.manual_up_typeamount)],
            medals.PHOTO_VAL: [MessageHandler(Filters.photo & ~Filters.command, medals.manual_up_photoval)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dp.add_handler(manual_up_conv_handler)


    ranking_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("ranking", ranking.get_ranking)],

        states={
            ranking.RANKINGTRSEL: [MessageHandler(Filters.text & ~Filters.command, ranking.get_ranking_trtype)],
            ranking.RANKINGTOPSEL: [MessageHandler(Filters.text & ~Filters.command, ranking.show_ranking)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dp.add_handler(ranking_conv_handler)

    # TODO: Gestionar tambien si un usuario habla en el chat y no esta añadido en la BD
    # dp.add_handler(MessageHandler(Filters.chat_type.groups & Filters.text, groups.groups_talk_chat_member_handler))

    # Start the Bot, añadimos allowed_update para poder editar lo mensajes
    updater.start_polling(allowed_updates=[])

    logger.info("BOT EN MARCHA")
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()