import logging
import constant as CONS
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CallbackContext
from Database.dbhelper import DBHelper

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='example.log')
logger = logging.getLogger(__name__)

def authgroups(update: Update, context: CallbackContext):
    """Verificar si un grupo esta en la BD y si no se añade yse devuelve el groupid"""
    # TODO: Verificar si un grupo esta en la BD y si no se añade y se devuelve el groupid

    group_tgid = update.message.chat_id
    group_name = update.message.chat.title
    # print(group_tgid, group_name)
    logger.info("Authgroup %s %s", group_tgid, group_name)

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
            logger.debug(e)
        finally:
            if dbconn:
                dbconn.close()

def add_user_groups(group_id, user_tgid) -> None:
    """Add user to a telegroup in db"""
    try:
        dbconn = DBHelper()
        dbconn.add_user_telegroup(group_id, user_tgid)
        # logger.info("Add user %s to group %s", user_tgid, group_id)

    except Exception as e:
        logger.debug(e)
    finally:
        if dbconn:
            dbconn.close()


def groups_new_chat_members_handler(update: Update, context: CallbackContext) -> None:
    """"""
    # Obtener telegroup DBID
    group_id = authgroups(update, context)
    new_users = update.message.new_chat_members
    group_name = update.message.chat.title

    # Insertar usuario en el grupo asociado a la BD
    for new_user in new_users:
        logger.info("New user in group %s %s %s", group_name, new_user.name, new_user.id)
        add_user_groups(group_id, new_user.id)

def groups_left_chat_member_handler(update: Update, context: CallbackContext) -> None:
    """"""
    # Obtener telegroup DBID
    group_id = authgroups(update, context)
    left_user = update.message.left_chat_member
    group_name = update.message.chat.title

    logger.info("Users left group %s \n %s", group_name, str(left_user))
    try:
        dbconn = DBHelper()
        dbconn.delete_user_telegroup(group_id, left_user.id)
    except Exception as e:
        logger.debug(e)
    finally:
        if dbconn:
            dbconn.close()

def group_info(update:Update, context: CallbackContext) -> None:
    # TODO: Añadir metodo a command handler. Solo admins
    group_id = authgroups(update, context)
    group_tgid = update.message.chat_id
    group_name = update.message.chat.title
    user_id = update.message.from_user
    chat_users = int(context.bot.get_chat_members_count(group_tgid))
    try:
        dbconn = DBHelper()
        usersdb = int(dbconn.group_users_count(group_id))
        usersvalidated = int(dbconn.group_usersvalidated_count(group_id))
        print(group_name, usersdb)
        print(group_name, usersvalidated)
        # TODO: Preparar mensaje. Reponder en privado

    except Exception as e:
        logger.debug(e)
    finally:
        if dbconn:
            dbconn.close()


