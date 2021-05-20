import MySQLdb  # 10 times more faster than mysql.connector
import logging
from CREDENTIALS import conf

# Join log
# Get logger instance
logger = logging.getLogger("baseSpider")
# Specify the output format
formatter = logging.Formatter('%(asctime)s\
              %(levelname)-8s:%(message)s')
# File log
file_handler = logging.FileHandler("operation_database.log")
file_handler.setFormatter(formatter)


class DBHelper:
    def __init__(self):
        self.conn = MySQLdb.connect(
            host=conf['mysql']['host'],
            db=conf['mysql']['db'],
            user=conf['mysql']['user'],
            passwd=conf['mysql']['passwd'])

        self.cursor = self.conn.cursor()
        logging.info("MySQL connection open")

    # users
    def add_user(self, nick, tgid, lang):

        stmt = 'insert into users(nick, tgid, lang) values ("%s",%s, %s)'
        args = (nick, tgid, lang)

        try:
            self.cursor = self.conn.cursor()
            #print(stmt % args)
            self.cursor.execute(stmt % args)
            self.conn.commit()

            return self.cursor.lastrowid

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")
                #self.conn.close()
                #print("MySQL connection is closed")

    def delete_user(self, tgid):
        stmt = 'delete from users where tgid = "%s"'
        args = (tgid,)
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def update_user(self, nick, tgid):
        stmt = 'update users set tgid="%s" where nick = "%s"'
        args = (tgid, nick)
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def get_user_tgid(self, tgid):
        stmt = 'select id,nick,lang from users where tgid="%s"'
        args = (tgid, )

        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()
            a = self.cursor.fetchone()
            return a

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def get_user_nick(self, userbdid):
        stmt = 'select nick from users where id="%s"'
        args = (userbdid,)

        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()
            a = self.cursor.fetchall()
            return a

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def get_users(self):
        stmt = 'select * from users'
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt)
            print(self.cursor.fetchall())

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def add_ranking_data(self, personid, type, amount):
        stmt = "insert into ranking(personid, type, amount) VALUES (%s,%s,%s)"
        args = (personid, type, amount)

        try:
            self.cursor = self.conn.cursor()
            print(stmt % args)
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    # ranking
    def get_user_name(self, name):
        stmt = 'select * from users where nick="%s"'
        args = (name, )
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def update_user_lang(self, userdbid, lang):
        stmt = 'update users set lang="%s" where id = "%s"'
        args = (lang, userdbid)
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def add_ranking_types(self, id, name, description):
        """insert into tranking(id,name,description) values (30,"sightseer","PokéStops Unique Visited");"""

        stmt = "insert into tranking(id, name, description) VALUES (%s,'%s','%s')"
        args = (id, str(name), str(description))

        try:
            self.cursor = self.conn.cursor()
            print(stmt % args)
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

    def get_ranking(self, tr_id, max_elements):
        """select amount, max(dcreate) max_fecha
        from ranking
        where type = 1;
        """

        stmt = """
        SELECT u.nick, u.tgid, r.amount
        FROM ((ranking r
        INNER JOIN (
            SELECT personid, type, MAX(dcreate) max_dcreate
            FROM ranking
            WHERE type = %s
            GROUP BY personid
        ) AS t
        ON r.dcreate = t.max_dcreate
        AND r.personid = t.personid)
        INNER JOIN (
            SELECT id, nick, tgid
            FROM users
            group by id
        ) AS u
        ON u.id = r.personid)
        ORDER BY r.amount DESC
        LIMIT %s;"""

        args = (str(tr_id), str(max_elements))

        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()
            a = self.cursor.fetchall()
            return a

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def get_types_ranking(self):
        """ Devuelve lista de tipos de los que existe algún valor almacenado en la BD"""

        stmt = "SELECT type FROM ranking GROUP BY type"

        args = ()

        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()
            a = self.cursor.fetchall()
            return a

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")
        pass

    def add_group(self, group_name, group_tgid):

        stmt = 'insert into telegroups(name, tgid) values ("%s",%s)'
        args = (group_name, group_tgid)

        try:
            self.cursor = self.conn.cursor()
            # print(stmt % args)
            self.cursor.execute(stmt % args)
            self.conn.commit()

            return self.cursor.lastrowid

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def get_group_tgid(self, group_tgid):
        stmt = 'select id,name from telegroups where tgid=%s'
        args = (group_tgid,)

        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()
            a = self.cursor.fetchall()
            return a

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def add_user_telegroup(self, group_id, user_tgid):
        """"""
        stmt = 'insert ignore into group_user(groupid, usertgid) values (%s, %s)'
        args = (group_id, user_tgid)

        try:
            self.cursor = self.conn.cursor()
            # print(stmt % args)
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def delete_user_telegroup(self, group_id, user_tgid):
        """"""
        stmt = "delete from group_user where groupid=%s and usertgid=%s"
        args = (group_id, user_tgid)

        try:
            self.cursor = self.conn.cursor()
            # print(stmt % args)
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            logging.info("MySQL connection is closed")

    def group_users_count(self, group_id):
        stmt = 'select count(usertgid) from group_user where groupid=%s'
        args = (group_id,)

        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()
            a = self.cursor.fetchone()
            return a[0]

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")

    def group_usersvalidated_count(self, group_id):

        stmt = """SELECT count(id) 
        FROM users u
        INNER JOIN (
            SELECT usertgid
            FROM group_user
            WHERE groupid=%s
        ) AS t
        ON u.tgid = t.usertgid"""

        args = (group_id,)

        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()
            a = self.cursor.fetchone()
            return a[0]

        except MySQLdb.Error as e:
            logging.error("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                logging.info("MySQL cursor is closed")












