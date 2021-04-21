#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" modulo users
"""

# GENERAL
import logging
from time import sleep
# PYTHON
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ConversationHandler

# PROYECTO
from Modelo.TypeRanking import bool_to_icon
from Plugins import visionocr
import constant as CONS
from Database.dbhelper import DBHelper

NICK, NICK_VAL = range(2)

logger = logging.getLogger(__name__)

def register(update: Update, context: CallbackContext):
    """Start the register proccess, ask user for nick"""

    chat_id = update.message.chat_id
    chat_type = update.message.chat.type

    if chat_type != "private":
        message = update.message.reply_text(
            text="Para registarte hablame por privado con el comando /registro",
            reply_markup=ReplyKeyboardRemove())
        print(message)
        sleep(3)
        context.bot.deleteMessage(message.chat.id, message.message_id)
        # context.bot.deleteMessage(message.reply_to_message.chat.id, message.reply_to_message.message_id)

        return ConversationHandler.END

    if authuser(update, context) is not None:
        text = "%s ya estás registrad@" % context.user_data[CONS.CONTEXT_VAR_USERDBNICK]
        message = update.message.reply_text(
            text=text,
            reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    user = update.message.from_user

    text = 'Send me your Nickname in PokemonGO.'
    logger.info("Inicio Registro: %s\n"
                "ID: %s", user.first_name, user.id)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return NICK


def nick(update: Update, context: CallbackContext):
    """Save users nick in context data and ask the user to send you a photo."""
    user = update.message.from_user
    logger.info("Nombre %s: Nick %s", user.first_name, update.message.text)
    context.user_data[CONS.CONTEXT_VAR_TMPNICK] = update.message.text

    text = "Is " + update.message.text + " your nickname?\n Send me a photo at your profile account to verify"
    update.message.reply_text(text)

    return NICK_VAL


def nickval(update: Update, context: CallbackContext):
    """Receive photo from user, save/get User from DB, and create ValidationForm. """
    # Initialize vars
    keyboard = []
    userdbid = 0

    user = update.message.from_user
    nickctx = str(context.user_data[CONS.CONTEXT_VAR_TMPNICK])
    photo_file = update.message.photo[-1].get_file()

    # Get data from OCR and save in context
    ocr_user = visionocr.ocr_register(photo_file, nickctx)
    # print("ocr_return nickval ", str(ocr_user))
    context.user_data[CONS.CONTEXT_VAR_OCRUSER] = ocr_user

    # ocr_user[nick]

    # Check validity of user nick
    if ocr_user.nick is None:
        # If invalid nick, notify user and cancel register
        text = "Nick no válido" + bool_to_icon[0] + ", vuelva a intentarlo con el comando /registro"
        update.message.reply_text(text)
        return ConversationHandler.END
    else:
        # If nick is valid, check if it exists in the database and get/save to obtain userid
        try:
            # Buscar usuario en la BD y conseguir userdbid
            user_id = authuser(update, context)
            if user_id is not None:
                userdbid = user_id
            else:
                # Añadimos usuario a la BD y obtenemos su userdbid
                print("AddUser DB")
                userdbid = registeruser(ocr_user.nick, user.id, user.language_code)

            context.user_data[CONS.CONTEXT_VAR_USERDBID] = userdbid
            txt = 'Nick registrado' + bool_to_icon[1] + ': ' + str(nickctx)
            update.message.reply_text(txt)

            return ConversationHandler.END

        except Exception as e:
            print(e)

def authuser(update: Update, context: CallbackContext):
    """ Return Id User in database and Save ID, NICK in Context"""
    user = update.message.from_user

    userdbid = CONS.CONTEXT_VAR_USERDBID in context.user_data.keys()
    userdbnick = CONS.CONTEXT_VAR_USERDBNICK in context.user_data.keys()
    userlang = CONS.CONTEXT_VAR_USERDBLANG in context.user_data.keys()
    if userdbid and userdbnick and userlang:
        return context.user_data[CONS.CONTEXT_VAR_USERDBID]
    else:
        try:
            # Buscar usuario en la BD y conseguir userdbid
            dbconn = DBHelper()
            index = dbconn.get_user_tgid(user.id)
            # print("Len Index", len(index))
            if len(index) >= 1:
                context.user_data[CONS.CONTEXT_VAR_USERDBID] = index[0]
                context.user_data[CONS.CONTEXT_VAR_USERDBNICK] = index[1]
                context.user_data[CONS.CONTEXT_VAR_USERDBLANG] = index[2]
                return context.user_data[CONS.CONTEXT_VAR_USERDBID]
            else:
                return None
        except Exception as e:
            print(e)
        finally:
            dbconn.close()


def registeruser(nick, tgid, lang):
    """Register User in database"""
    try:
        dbconn = DBHelper()
        userdbid = dbconn.add_user(nick, tgid, lang)
        logger.info("Usuario registrado con Nick %s, TGID: %s", nick, tgid)

        return userdbid
    except Exception as e:
        logger.error(e)
    finally:
        if dbconn:
            dbconn.close()