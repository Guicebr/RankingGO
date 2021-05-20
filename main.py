#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ranking Pokemon Go Medals Bot.


"""
# GENERAL
import logging

# TELEGRAM
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler

# PROYECTO
import users
import medals
import ranking
import groups

from CREDENTIALS import BOT_TOKEN
from Database.dbhelper import DBHelper
from Modelo import TypeRankTranslator, LangTranslator
from Modelo.TypeRanking import bool_to_icon
from Modelo.TypeRanking import typeranking_enum as tr_enum
from Plugins import common_func as c_func
from Plugins import visionocr
import constant as CONS



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='Logs/manin.log')
logger = logging.getLogger(__name__)

# logger.debug('Este mensaje es sólo para frikis programadores como nosotros')
# logger.info('Este mensaje representa algo normal')
# logger.warning('Esto ya no es tan normal')
# logger.error('Deberías empezar a preocuparte')
# logger.critical('El bot está así X')

dbconn = DBHelper()
trtranslator = TypeRankTranslator.TypeRankTranslator()
langtranslator = LangTranslator.LangTranslator()

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""

    reply_keyboard = [['/registro', '/cancel']]
    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    text = langtranslator.getWordLang('START_STRING', lang)
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    logger.error('Update "%s" caused error "%s"', update, context.error)


def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    text = langtranslator.getWordLang('HELP_PRIVATE_STRING', lang)
    update.message.reply_text(text)

def help_command_groups(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    text = langtranslator.getWordLang('HELP_GROUPS_STRING', lang)
    update.message.reply_text(text)


def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def cancel(update: Update, context: CallbackContext):
    """Cancel command."""
    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    logger.info("UserData %s canceled the conversation.", user.first_name)
    text = langtranslator.getWordLang('END_CONVERSATION_STRING', lang)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def set_lang( update: Update, context: CallbackContext):
    """ """
    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code
    keyboard = []

    # Comprobamos si el usuario esta registrado
    if users.authuser(update, context) is None:
        text = langtranslator.getWordLang("USER_NOT_REGISTERED", lang)
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return None

    # Cargamos lista de idiomas disponibles en un keyboard
    for lang in langtranslator.xml_lang_pool:
        keyboard.append([InlineKeyboardButton(str(lang), callback_data=str(lang))])
    keyboard.append([InlineKeyboardButton("Finish", callback_data='finish')])

    # Usuario selecciona un idioma
    text = langtranslator.getWordLang('ASK_USER_LANG', lang)
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def lang_selected (update: Update, context: CallbackContext) -> None:
    """ """
    userdbid = context.user_data[CONS.CONTEXT_VAR_USERDBID]

    query = update.callback_query
    # Check callback type
    callback_text = query.data
    if callback_text in langtranslator.xml_lang_pool:
        # Actualizamos el idioma del usuario
        try:
            lang = callback_text
            dbconn = DBHelper()
            dbconn.update_user_lang(userdbid, lang)
            text = langtranslator.getWordLang("USER_LANG_UPDATED", lang)

            # Comunicamos al usuario en el nuevo idioma
            query.edit_message_text(text=text)
            return ConversationHandler.END

        except Exception as e:
            logger.error(e)
        finally:
            if dbconn:
                dbconn.close()

    elif callback_text == "finish":
        return ConversationHandler.END

def printcontextdata(update: Update, context: CallbackContext):

    chat_id = update.message.chat_id
    print(context.user_data)
    print(update.message.from_user)
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

    dp.add_handler(CommandHandler(command="start", filters=Filters.chat_type.private, callback=start))
    dp.add_handler(CommandHandler(command="help", filters=Filters.chat_type.private, callback=help_command))
    dp.add_handler(CommandHandler(command="help", filters=Filters.chat_type.groups, callback=help_command_groups))
    dp.add_handler(CommandHandler(command="lang", filters=Filters.chat_type.private, callback=set_lang))

    # dp.add_handler(CommandHandler("userdata", filters=Filters.user("@Wicisian"), callback=printcontextdata))
    # Un admin pide por el grupo info sobre los usuarios en el grupo, responde solo si eres admin
    dp.add_handler(CommandHandler(command="group_info", filters=Filters.chat_type.groups, callback=groups.group_info))

    # Registramos cuando el usuario pulsa un boton del formulario de registro
    # updater.dispatcher.add_handler(CallbackQueryHandler(register_val))

    # Registramos cuando el usuario selecciona un idioma
    updater.dispatcher.add_handler(CallbackQueryHandler(lang_selected))


    # dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, screenshot_handler))


    # COMANDO REGISTRO
    # Add conversation handler with the states NICK, NICK_VAL
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command="registro", filters=Filters.chat_type.private, callback=users.register)],

        states={
            users.NICK: [MessageHandler(Filters.text & ~Filters.command, users.nick)],
            users.NICK_VAL: [MessageHandler(Filters.photo & ~Filters.command, users.nickval)],
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # COMANDO MANUAL_UP
    dp.add_handler(conv_handler)
    manual_up_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command="manual_up", filters=Filters.chat_type.private, callback=medals.manual_up)],

        states={
            medals.TRTYPESEL: [MessageHandler(Filters.text & ~Filters.command, medals.manual_up_trtype)],
            medals.TYPE_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, medals.manual_up_typeamount)],
            medals.PHOTO_VAL: [MessageHandler(Filters.photo & ~Filters.command, medals.manual_up_photoval)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dp.add_handler(manual_up_conv_handler)


    # COMANDO RANKING
    ranking_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command="ranking", filters=Filters.chat_type.private, callback=ranking.get_ranking)],

        states={
            ranking.RANKINGTRSEL: [MessageHandler(Filters.text & ~Filters.command, ranking.get_ranking_trtype)],
            ranking.RANKINGTOPSEL: [MessageHandler(Filters.text & ~Filters.command, ranking.show_ranking)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dp.add_handler(ranking_conv_handler)

    # Users in Group Management
    # El bot se fue/echaron de un grupo o Usuario abandona el grupo en el que esta el bot.
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, groups.groups_left_chat_member_handler))
    # El bot se unio a un grupo/canal/supergrupo no privado o Usuario se une a un grupo en el que se encuentra el bot.
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, groups.groups_new_chat_members_handler))

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