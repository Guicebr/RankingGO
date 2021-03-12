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
import logging
from time import sleep
import constant as CONS


from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler

from CREDENTIALS import BOT_TOKEN
from Database.dbhelper import DBHelper
from Modelo import TypeRankTranslator
# from Plugins.visionocr import *
from Modelo.TypeRanking import bool_to_icon
from Modelo.TypeRanking import typeranking_enum as tr_enum
from Plugins import common_func as c_func
from Plugins import visionocr

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='example.log')

logger = logging.getLogger(__name__)

""" logger.debug(‘Este mensaje es sólo para frikis programadores como nosotros ;)’)
    logger.info(‘Este mensaje representa algo normal’)
    logger.warning(‘Esto ya no es tan normal’)
    logger.error(‘Deberías empezar a preocuparte’)
    logger.critical(‘El bot está así X(’)"""

dbconn = DBHelper()

translator = TypeRankTranslator.TypeRankTranslator()
xml_lang_selector = "es"

REGISTER_VAL, NICK, NICK_VAL = range(3)
TRTYPESEL, TYPE_AMOUNT, PHOTO_VAL = range(3)
RANKINGTRSEL, RANKINGTOPSEL = range(2)
RANKINGTOPS = [10, 50, 100]


# DEBUG = 1

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.message.from_user

    authuser(update, context)
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

    if authuser(update, context) > 0:
        text = "%s ya estás registrad@" % context.user_data[CONS.CONTEXT_VAR_USERDBNICK]
        message = update.message.reply_text(
            text=text,
            reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # context.bot.send_message(
    #     chat_id=chat_id,
    #     text="Soy un Achicayna, que entre los primeros pobladores de Canarias era el equivalente a un plebeyo."
    # )

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
                userdbid = registeruser(ocr_user.nick, user.id)

            context.user_data[CONS.CONTEXT_VAR_USERDBID] = userdbid
            txt = 'Nick registrado' + bool_to_icon[1] + ': ' + str(nickctx)
            update.message.reply_text(txt)

            return ConversationHandler.END

        except Exception as e:
            print(e)


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


def authuser(update: Update, context: CallbackContext):
    """ Return Id User in database and Save ID, NICK in Context"""
    user = update.message.from_user

    if CONS.CONTEXT_VAR_USERDBID in context.user_data.keys() and CONS.CONTEXT_VAR_USERDBNICK in context.user_data.keys():
        return context.user_data[CONS.CONTEXT_VAR_USERDBID]
    else:
        try:
            # Buscar usuario en la BD y conseguir userdbid
            dbconn = DBHelper()
            index = dbconn.get_user_tgid(user.id)
            # print("Len Index", len(index))
            if len(index) >= 1:
                context.user_data[CONS.CONTEXT_VAR_USERDBID] = index[0][0]
                context.user_data[CONS.CONTEXT_VAR_USERDBNICK] = index[0][1]
                return context.user_data[CONS.CONTEXT_VAR_USERDBID]
            else:
                return None
        except Exception as e:
            print(e)
        finally:
            dbconn.close()


def registeruser(nick, tgid):
    """Register User in database"""
    try:
        dbconn = DBHelper()
        userdbid = dbconn.add_user(nick, tgid)

        return userdbid
    except Exception as e:
        print(e)
    finally:
        dbconn.close()


def manual_up(update: Update, context: CallbackContext):
    """Start the update data proccess, ask user for category"""
    user = update.message.from_user
    lang = xml_lang_selector

    # Verificamos que el usuario este registrado
    if authuser(update, context) is None:
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


def get_ranking(update: Update, context: CallbackContext):
    """Mostrar categorías disponibles, y el usuario selecciona una"""
    user = update.message.from_user
    lang = xml_lang_selector

    # TODO: Argumento 0 -> Indique tipoderanking, se comprueba si esta en la lista de disponible
    # TODO: Argumento 1 -> Numero de elementos, tiene que ser una de los establecido 10, 50, 100

    # Verificamos que el usuario este registrado
    if authuser(update, context) is None:
        text = "Usuario no registrado, ejecute el comando /registro primero"
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    text = "Por favor selecciona la categoría: "
    keyboard = []

    # Imprimir solo los tiposderanking que tengan algún dato en la BD
    tr_avalible = dbconn.get_types_ranking()

    print(tr_avalible)
    for tr_id in tr_avalible:
        tr_id = str(tr_id[0])
        name = translator.translate_DBidtoHUMAN(xml_lang_selector, tr_id)
        keyboard.append([name])

    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return RANKINGTRSEL


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

    tr_id = translator.translate_HumantoSEL(xml_lang_selector, translator.ID, tr)
    data = dbconn.get_ranking(tr_id, num_elem)

    # print(str(data))
    head = "Ranking " + str(tr) + "\n"
    txt = head
    for useri in range(len(data)):
        mention = "%s. %s [%s](tg://user?id=%s)\n" % (useri + 1, data[useri][2], data[useri][0], data[useri][1])
        txt += mention

    update.message.reply_text(txt, parse_mode="Markdown")
    return ConversationHandler.END


def pruebabot(update: Update, context: CallbackContext) -> None:
    logger.info('He recibido un comando start')

    chat_id = update.message.chat_id

    print(update.message, chat_id, update.message.chat.type)

    context.bot.send_message(
        chat_id=chat_id,
        text="Soy un Achicayna, que entre los primeros pobladores de Canarias era el equivalente a un plebeyo."
    )


def set_lang():
    # TODO: establecer lenguaje en Contexto
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


def getchatdata(update: Update, context: CallbackContext):
    """klmcds"""
    chat_id = update.message.chat_id
    user = update.message.from_user
    print(chat_id, user)

    chat = context.bot.getChat(chat_id)
    admins = context.bot.getChatAdministrators(chat_id)
    count = context.bot.getChatMembersCount(chat_id)
    member = context.bot.getChatMember(chat_id, user["id"])
    # print(context.bot.getChat(chat_id))

    txt = "%s \n %s" % (chat_id, user)
    txt = "" + str(chat) + "\n"
    txt += str(admins) + "\n"
    txt += str(count) + "\n"
    txt += str(member) + "\n"
    print(txt)

    context.bot.send_message(
        chat_id=chat_id,
        text=txt
    )


def authgroups(update: Update, context: CallbackContext):
    """Verificar si un grupo esta en la BD y si no se añade yse devuelve el groupid"""
    # TODO: Verificar si un grupo esta en la BD y si no se añade y se devuelve el groupid

    group_tgid = update.message.chat_id
    group_name = update.message.chat.title
    print(group_tgid, group_name)

    if CONS.CONTEXT_VAR_GROUPDBID in context.user_data.keys():
        return context.user_data[CONS.CONTEXT_VAR_GROUPDBID]
    else:
        try:
            # Buscar grupo en la BD y conseguir userdbid
            dbconn = DBHelper()
            index = dbconn.get_group_tgid(group_tgid)
            # print("Len Index", len(index))
            if len(index) >= 1:
                context.user_data[CONS.CONTEXT_VAR_GROUPDBID] = index[0][0]
                return context.user_data[CONS.CONTEXT_VAR_GROUPDBID]
            else:
                dbconn = DBHelper()
                group_id = dbconn.add_group(group_name, group_tgid)
                context.user_data[CONS.CONTEXT_VAR_GROUPDBID] = group_id
                return group_id

        except Exception as e:
            print(e)
        finally:
            dbconn.close()

def add_user_groups(group_id, user_tgid) -> None:
    """Add user to a telegroup in db"""
    try:
        dbconn = DBHelper()
        dbconn.add_user_telegroup(group_id, user_tgid)

    except Exception as e:
        print(e)
    finally:
        dbconn.close()


def groups_new_chat_members_handler(update: Update, context: CallbackContext):
    """"""
    # Obtener telegroup DBID
    group_id = authgroups(update, context)
    print(group_id, update.message)
    new_users = update.message.new_chat_members
    print(new_users)

    # Insertar usuario en el grupo asociado a la BD
    for new_user in new_users:
        print("new_user.id", new_user.id)
        add_user_groups(group_id, new_user.id)

def groups_left_chat_member_handler(update: Update, context: CallbackContext):
    """"""
    # Obtener telegroup DBID
    group_id = authgroups(update, context)
    left_user = update.message.left_chat_member
    print(group_id, update.message)
    print(left_user)
    try:
        dbconn = DBHelper()
        dbconn.delete_user_telegroup(group_id, left_user.id)
    except Exception as e:
        print(e)
    finally:
        if dbconn:
            dbconn.close()

def main():
    """Start the bot."""
    updater = Updater(BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("userdata", printcontextdata))
    dp.add_handler(CommandHandler("chatdata", getchatdata))
    # TODO: Set lang
    dp.add_handler(CommandHandler("lang", set_lang))

    dp.add_handler(CommandHandler("pruebabot", pruebabot))
    # command
    # dp.add_handler(CommandHandler("experience", experience))


    # El bot se fue/echaron de un grupo o Usuario abandona el grupo en el que esta el bot.
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, groups_left_chat_member_handler))


    # El bot se unio a un grupo/canal/supergrupo no privado o Usuario se une a un grupo en el que se encuentra el bot.
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, groups_new_chat_members_handler))

    # Registramos cuando el usuario pulsa un boton del formulario de registro
    # updater.dispatcher.add_handler(CallbackQueryHandler(register_val))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, screenshot_handler))

    # Add conversation handler with the states NICK, NICK_VAL, REGISTER_VAL
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("registro", register)],

        states={
            NICK: [MessageHandler(Filters.text & ~Filters.command, nick)],
            NICK_VAL: [MessageHandler(Filters.photo & ~Filters.command, nickval)],
            # REGISTER_VAL: [CallbackQueryHandler(register_val)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(conv_handler)

    manual_up_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("manual_up", manual_up)],

        states={
            TRTYPESEL: [MessageHandler(Filters.text & ~Filters.command, manual_up_trtype)],
            TYPE_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, manual_up_typeamount)],
            PHOTO_VAL: [MessageHandler(Filters.photo & ~Filters.command, manual_up_photoval)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(manual_up_conv_handler)

    ranking_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("ranking", get_ranking)],

        states={
            RANKINGTRSEL: [MessageHandler(Filters.text & ~Filters.command, get_ranking_trtype)],
            RANKINGTOPSEL: [MessageHandler(Filters.text & ~Filters.command, show_ranking)]
        },

        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dp.add_handler(ranking_conv_handler)

    # Start the Bot, añadimos allowed_update para poder editar lo mensajes
    updater.start_polling(allowed_updates=[])

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()