#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" modulo users
"""

# GENERAL
import logging

# TELEGRAM
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

# PROYECTO
import users
import constant as CONS
from Database.dbhelper import DBHelper
from Plugins import common_func as c_func
from Plugins import visionocr
from Modelo import TypeRankTranslator
from Modelo import LangTranslator


logger = logging.getLogger(__name__)

trtranslator = TypeRankTranslator.TypeRankTranslator()
langtranslator = LangTranslator.LangTranslator()

TRTYPESEL, TYPE_AMOUNT, PHOTO_VAL = range(3)

def manual_up(update: Update, context: CallbackContext):
    """Start the update data proccess, ask user for category"""

    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    # Verificamos que el usuario este registrado
    if users.authuser(update, context) is None:
        text = langtranslator.getWordLang("USER_NOT_REGISTERED", lang)
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    logger.info("Inicio ManualUp")
    text = langtranslator.getWordLang("ASK_USER_CATEGORY", lang)
    keyboard = []

    # Almacenar en un fichero temporal las categorias de la BD

    for name in trtranslator.getlist_TypeRank(lang):
        keyboard.append([str(name)])

    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return TRTYPESEL


def manual_up_trtype(update: Update, context: CallbackContext):
    """Echo and finish Conversation"""

    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code
    context.user_data[CONS.CONTEXT_VAR_TRTYPE] = update.message.text
    text = langtranslator.getWordLang("ASK_USER_AMOUNT", lang)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return TYPE_AMOUNT

def manual_up_typeamount(update: Update, context: CallbackContext):
    """"""

    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code
    context.user_data[CONS.CONTEXT_VAR_AMOUNT] = update.message.text
    text = langtranslator.getWordLang("ASK_USER_VALIDATION_PHOTO", lang)
    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return PHOTO_VAL


def manual_up_photoval(update: Update, context: CallbackContext):
    """ """
    user = update.message.from_user
    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    context.user_data[CONS.CONTEXT_VAR_AMOUNT] = update.message.text
    tr_type = context.user_data[CONS.CONTEXT_VAR_TRTYPE]
    amount = context.user_data[CONS.CONTEXT_VAR_AMOUNT]
    amount = c_func.string_cleaner_for_num(amount)
    userbdid = context.user_data[CONS.CONTEXT_VAR_USERDBID]
    nick = context.user_data[CONS.CONTEXT_VAR_USERDBNICK]

    logger.info("Validando TipoRanking %s y Cantidad %s", tr_type, amount)
    photo_file = update.message.photo[-1].get_file()
    print(photo_file)
    data_valid = visionocr.ocrScreenshot_CheckTyp_Amount(photo_file, tr_type, amount, nick)

    if data_valid:
        try:
            # tr_id = tr_enum[tr_type]
            tr_id = trtranslator.translate_HumantoSEL(lang, trtranslator.ID, tr_type)
            # print("tr_id", tr_id)
            dbconn = DBHelper()
            dbconn.add_ranking_data(userbdid, tr_id, amount)
            text = langtranslator.getWordLang("PHOTOMEDAL_VALID_OK", lang) % (str(tr_type), str(amount))
            update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        except Exception as e:
            logger.error(e)
            return ConversationHandler.END
    else:
        text = langtranslator.getWordLang("PHOTOMEDAL_VALID_NOK", lang) % (tr_type, amount)
        logger.info("TipoRanking %s o Cantidad %s no válidos", tr_type, amount)
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

# def screenshot_handler(update: Update, context: CallbackContext) -> None:
#     """ Function comment"""
#     # Sustituir por authuser()
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
#             update.message.reply_text(txt)desde el main
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

# def getKeyboardRegisterValidation(ocr_user, ocr_user_valid):
#     keyboard = []
#     for type_rank in ocr_user:
#         if ocr_user[type_rank] is not None:
#             value = str(type_rank) + ": " + str(ocr_user[type_rank]) + bool_to_icon[int(ocr_user_valid[type_rank])]
#             cb_data = list(ocr_user.keys()).index(type_rank)
#
#             keyboard.append([InlineKeyboardButton(str(value), callback_data=str(cb_data))])
#     keyboard.append([InlineKeyboardButton("Finish", callback_data='finish')])
#
#     return keyboard