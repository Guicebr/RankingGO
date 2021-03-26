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
from main import trtranslator

logger = logging.getLogger(__name__)

RANKINGTRSEL, RANKINGTOPSEL = range(2)
RANKINGTOPS = [10, 50, 100]

xml_lang_selector = "es"

def get_ranking(update: Update, context: CallbackContext):
    """Mostrar categorías disponibles, y el usuario selecciona una"""
    user = update.message.from_user
    lang = xml_lang_selector

    # TODO: Argumento 0 -> Indique tipoderanking, se comprueba si esta en la lista de disponible
    # TODO: Argumento 1 -> Numero de elementos, tiene que ser una de los establecido 10, 50, 100

    # Verificamos que el usuario este registrado
    if users.authuser(update, context) is None:
        text = "Usuario no registrado, ejecute el comando /registro primero"
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    text = "Por favor selecciona la categoría: "
    keyboard = []

    try:
        dbconn = DBHelper()
        # Imprimir solo los tiposderanking que tengan algún dato en la BD
        tr_avalible = dbconn.get_types_ranking()

        print(tr_avalible)
        for tr_id in tr_avalible:
            tr_id = str(tr_id[0])
            name = trtranslator.translate_DBidtoHUMAN(xml_lang_selector, tr_id)
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

    for ranks in RANKINGTOPS:
        name = "TOP " + str(ranks)
        keyboard.append([str(name)])

    text = """Selecciona el la cantidad de elementos que quieres mostrar de la categoría %s: 
           """ % (context.user_data[CONS.CONTEXT_VAR_TRTYPE])

    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return RANKINGTOPSEL


def show_ranking(update: Update, context: CallbackContext):
    """Tenemos la categoría y el número de elementos a mostrar, se hace una petición a la BD con
     la categoria y el número de elemtos buscados"""

    tr = context.user_data[CONS.CONTEXT_VAR_TRTYPE]
    try:
        if len(update.message.text) > 0:
            num_elem = int(update.message.text.split(" ")[1])

    except Exception as e:
        num_elem = 100
        logger.warning("Error %s con el valor: %s\n", e, update.message.text)
        print(e)
    try:
        dbconn = DBHelper()
        tr_id = trtranslator.translate_HumantoSEL(xml_lang_selector, trtranslator.ID, tr)
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