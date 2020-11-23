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

    # users
    def add_user(self, nick, tgid):
        stmt = 'insert into users(nick, tgid) values ("%s",%s)'
        args = (nick, tgid)

        try:
            self.cursor = self.conn.cursor()
            #print(stmt % args)
            self.cursor.execute(stmt % args)
            self.conn.commit()

            return self.cursor.lastrowid

        except MySQLdb.Error as e:
            print("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                print("MySQL cursor is closed")
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
            print("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                print("MySQL cursor is closed")

    def update_user(self, nick, tgid):
        stmt = 'update users set tgid="%s" where nick = "%s"'
        args = (tgid, nick)
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            print("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                print("MySQL cursor is closed")

    def get_user_tgid(self, tgid):
        stmt = 'select * from users where tgid="%s"'
        args = (tgid, )
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            print("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                print("MySQL cursor is closed")

    def get_user_name(self, name):
        stmt = 'select * from users where nick="%s"'
        args = (name, )
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            print("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                print("MySQL cursor is closed")

    def get_users(self):
        stmt = 'select * from users'
        try:
            self.cursor.execute(stmt)
            print(self.cursor.fetchall())

        except MySQLdb.Error as e:
            print("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                print("MySQL cursor is closed")

    # ranking
    def add_ranking_data(self, personid, type, amount):
        stmt = "insert into ranking(personid, type, amount) VALUES (%s,%s,%s)"
        args = (personid, type, amount)

        try:
            self.cursor = self.conn.cursor()
            print(stmt % args)
            self.cursor.execute(stmt % args)
            self.conn.commit()

        except MySQLdb.Error as e:
            print("Error %s" % str(e))

        finally:
            if self.conn:
                self.cursor.close()
                print("MySQL cursor is closed")

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("MySQL connection is closed")




    def add_item(self, item_text):
        stmt = "INSERT INTO items (description) VALUES (?)"
        args = (item_text,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text):
        stmt = "DELETE FROM items WHERE description = (?)"
        args = (item_text,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self):
        stmt = "SELECT description FROM items"
        return [x[0] for x in self.conn.execute(stmt)]
