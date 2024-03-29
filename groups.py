#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Modulo Groups
Gestiona los grupos y los miembros dentro de ellos
"""
import logging
import constant as CONS
import users

from telegram import Update
from telegram.ext import Updater, CallbackContext
from Database.dbhelper import DBHelper
from Modelo import LangTranslator

logger = logging.getLogger(__name__)
langtranslator = LangTranslator.LangTranslator()


def authgroups(update: Update, context: CallbackContext):
    """Verificar si un grupo esta en la BD y si no se añade y se devuelve el groupid"""

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
        logger.info("Add user %s to group %s", user_tgid, group_id)

    except Exception as e:
        logger.debug(e)
    finally:
        if dbconn:
            dbconn.close()


def groups_new_chat_members_handler(update: Update, context: CallbackContext) -> None:
    """Cuando se une un usuario al grupo, el bot lo añade a la db """
    # Obtener telegroup DBID
    group_id = authgroups(update, context)
    new_users = update.message.new_chat_members
    group_name = update.message.chat.title

    print([group_id, group_name, new_users])

    # Insertar usuario en el grupo asociado a la BD
    for new_user in new_users:
        logger.info("New user in group %s %s %s", group_name, new_user.name, new_user.id)
        add_user_groups(group_id, new_user.id)

def groups_talk_chat_member_handler(update: Update, context: CallbackContext) -> None:
    """Añadir usuario cuando habla por el grupo"""

    # Obtener telegroup DBID
    group_id = authgroups(update, context)
    talk_users = [update.message.from_user]
    group_name = update.message.chat.title

    print([group_id, group_name, talk_users])
    # Insertar usuario en el grupo asociado a la BD
    for new_user in talk_users:
        logger.info("New user in group %s %s %s", group_name, new_user.name, new_user.id)
        add_user_groups(group_id, new_user.id)

def groups_left_chat_member_handler(update: Update, context: CallbackContext) -> None:
    """Eliminar un usuario de la BD cuando se sale del grupo"""
    # Obtener telegroup DBID
    group_id = authgroups(update, context)
    left_user = update.message.left_chat_member
    group_name = update.message.chat.title

    logger.info("Users left group %s \n %s", group_name, str(left_user))
    try:
        dbconn = DBHelper()
        dbconn.delete_user_telegroup(group_id, left_user.id)
    except Exception as e:
        logger.error(e)
    finally:
        if dbconn:
            dbconn.close()


def group_info(update: Update, context: CallbackContext) -> None:
    """Obtener información sobre los usuarios en un grupo y enviarla por privado"""
    # TODO: Comment
    # Comando group_info, solo admins del grupo

    user = update.message.from_user
    group_tgid = update.message.chat_id
    user_id = user.id

    users.authuser(update, context)
    lang = context.user_data[CONS.CONTEXT_VAR_USERDBLANG] or user.language_code

    chatmember = context.bot.get_chat_member(group_tgid, user_id)

    lang = CONS.DEFAULT_LANG #userlang

    if chatmember.status not in ['creator', "administrator"]:
        return None

    group_id = authgroups(update, context)
    group_name = update.message.chat.title
    chat_users = int(context.bot.get_chat_members_count(group_tgid))

    try:
        dbconn = DBHelper()
        usersdb = int(dbconn.group_users_count(group_id))
        usersvalidated = int(dbconn.group_usersvalidated_count(group_id))

        logger.info("%s, %s -> %s", chatmember.user.name, group_name, "group_info")

        # Preparar mensaje. Reponder en privado
        # txt = ("GRUPO: %s\n"
        #        "Usuarios en el grupo: %d\n"
        #        "Almacenados en la BD: %d\n"
        #        "Validados con el bot: %d") % (group_name, chat_users, usersdb, usersvalidated)

        txt = langtranslator.getWordLang("GROUPS_GROUP_INFO", lang) % (group_name, chat_users, usersdb, usersvalidated)
        context.bot.sendMessage(chat_id=user_id, text=txt)

        # Borra el mensaje del comando. Se necesita permisos de administrador
        context.bot.deleteMessage(group_tgid, update.message.message_id)

    except Exception as e:
        logger.error(e)
    finally:
        if dbconn:
            dbconn.close()




