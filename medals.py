#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" modulo users
"""

# GENERAL
import logging

# TELEGRAM
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ConversationHandler

import constant as CONS
# PROYECTO
import users
from Database.dbhelper import DBHelper
from Modelo import TypeRankTranslator
from Plugins import common_func as c_func
from Plugins import visionocr

logger = logging.getLogger(__name__)


TRTYPESEL, TYPE_AMOUNT, PHOTO_VAL = range(3)
translator = TypeRankTranslator.TypeRankTranslator()
xml_lang_selector = "es"

def manual_up(update: Update, context: CallbackContext):
    """Start the update data proccess, ask user for category"""
    user = update.message.from_user
    lang = xml_lang_selector

    # Verificamos que el usuario este registrado
    if users.authuser(update, context) is None:
        text = "Usuario no registrado, ejecute el comando /registro primero"
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    text = "Por favor selecciona la categoría: "
    keyboard = []
    # TODO Almacenar en un fichero temporal las categorias de la BD

    # for i in tr_enum:
    #     keyboard.append([str(i)])

    # print(translator.xml_translate_dict)
    # print(lang)
    for name in translator.getlist_TypeRank(lang):
        keyboard.append([str(name)])

    # logger.info("Inicio Registro: %s\n ID: %s", user.first_name, user.id)
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return TRTYPESEL


def manual_up_trtype(update: Update, context: CallbackContext):
    """Echo and finish Conversation"""
    context.user_data[CONS.CONTEXT_VAR_TRTYPE] = update.message.text
    text = "Introduce la cantidad sin puntos ni comas, por favor."
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return TYPE_AMOUNT


def manual_up_typeamount(update: Update, context: CallbackContext):
    """"""
    context.user_data[CONS.CONTEXT_VAR_AMOUNT] = update.message.text

    text = "Enviame una captura de pantalla, para que pueda validarlo."
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return PHOTO_VAL


def manual_up_photoval(update: Update, context: CallbackContext):
    tr_type = context.user_data[CONS.CONTEXT_VAR_TRTYPE]
    amount = context.user_data[CONS.CONTEXT_VAR_AMOUNT]
    amount = c_func.string_cleaner_for_num(amount)
    userbdid = context.user_data[CONS.CONTEXT_VAR_USERDBID]
    nick = context.user_data[CONS.CONTEXT_VAR_USERDBNICK]

    lang = xml_lang_selector

    photo_file = update.message.photo[-1].get_file()
    print(photo_file)
    data_valid = visionocr.ocrScreenshot_CheckTyp_Amount(photo_file, tr_type, amount, nick)

    if data_valid:
        try:
            # tr_id = tr_enum[tr_type]
            tr_id = translator.translate_HumantoSEL(lang, translator.ID, tr_type)
            print("tr_id", tr_id)
            dbconn = DBHelper()
            dbconn.add_ranking_data(userbdid, tr_id, amount)
            text = "Datos guardados %s %s" % (str(tr_type), str(amount))
            update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        except Exception as e:
            print(e)
            return ConversationHandler.END
    else:
        text = "Datos no válidos"
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END