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
from Modelo import LangTranslator

langtranslator = LangTranslator.LangTranslator()
trtranslator = TypeRankTranslator.TypeRankTranslator()
logger = logging.getLogger(__name__)

RANKINGTRSEL, RANKINGTOPSEL = range(2)
RANKINGTOPS = [10, 50, 100]


def get_ranking(update: Update, context: CallbackContext):
    """Mostrar categorías disponibles, y el usuario selecciona una"""

    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    # TODO: Argumento 0 -> Indique tipoderanking, se comprueba si esta en la lista de disponible
    # TODO: Argumento 1 -> Numero de elementos, tiene que ser una de los establecido 10, 50, 100

    # Verificamos que el usuario este registrado
    if users.authuser(update, context) is None:
        text = langtranslator.getWordLang("USER_NOT_REGISTERED", lang)
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    text = langtranslator.getWordLang("ASK_USER_CATEGORY", lang)
    keyboard = []

    try:
        dbconn = DBHelper()
        # Imprimir solo los tiposderanking que tengan algún dato en la BD
        tr_avalible = dbconn.get_types_ranking()

        # print(tr_avalible)
        for tr_id in tr_avalible:
            tr_id = str(tr_id[0])
            name = trtranslator.translate_DBidtoHUMAN(lang, tr_id)
            keyboard.append([name])

        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return RANKINGTRSEL
    except Exception as e:
        logger.error(e)
    finally:
        if dbconn:
            dbconn.close()


def get_ranking_trtype(update: Update, context: CallbackContext):
    """Obtenemos la categoría que ha seleccionado el usuario y pedimos el número de elementos a buscar"""
    context.user_data[CONS.CONTEXT_VAR_TRTYPE] = update.message.text
    keyboard = []

    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    for ranks in RANKINGTOPS:
        name = "TOP " + str(ranks)
        keyboard.append([str(name)])

    text = langtranslator.getWordLang("ASK_TOPNUM_RANKING", lang) % (context.user_data[CONS.CONTEXT_VAR_TRTYPE])

    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return RANKINGTOPSEL


def show_ranking(update: Update, context: CallbackContext):
    """Tenemos la categoría y el número de elementos a mostrar, se hace una petición a la BD con
     la categoria y el número de elemtos buscados"""

    tr = context.user_data[CONS.CONTEXT_VAR_TRTYPE]
    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    try:
        if len(update.message.text) > 0:
            num_elem = int(update.message.text.split(" ")[1])

    except Exception as e:
        num_elem = 100
        logger.warning("Error %s con el valor: %s\n", e, update.message.text)
        print(e)
    try:
        dbconn = DBHelper()
        tr_id = trtranslator.translate_HumantoSEL(lang, trtranslator.ID, tr)
        data = dbconn.get_ranking(tr_id, num_elem)

        # print(str(data))
        head = "Ranking " + str(tr) + "\n"
        txt = head
        for useri in range(len(data)):
            mention = "%s. %s [%s](tg://user?id=%s)\n" % (useri + 1, data[useri][2], data[useri][0], data[useri][1])
            txt += mention

        update.message.reply_text(txt, parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
    finally:
        if dbconn:
            dbconn.close()

        return ConversationHandler.END