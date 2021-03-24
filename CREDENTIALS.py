VISION_KEY_PATH = ''
BOT_TOKEN = "1161816070:AAH03yJ7nyZs5r-M5CtZV2XMiF78YXDYsjk"
# conf = dict(telegram_token="1161816070:AAH03yJ7nyZs5r-M5CtZV2XMiF78YXDYsjk",
#             mysql={
#                 'user': 'wicitelebot',  # mysql user
#                 'passwd': 'wicipass',  # mysql password
#                 'host': 'localhost',  # mysql host
#                 'db': 'RankingPOGO',  # mysql database
#                 'port': 3306,  # mysql port
#                 'unix_socket': '/var/run/mysqld/mysqld.sock',  # mysql unix socket file
#             })

# https://api.telegram.org/1161816070:AAH03yJ7nyZs5r-M5CtZV2XMiF78YXDYsjk/getupdates
conf = dict(telegram_token="1161816070:AAH03yJ7nyZs5r-M5CtZV2XMiF78YXDYsjk",
            mysql={
                'user': 'wicitelebot',  # mysql user
                'passwd': 'wicipass',  # mysql password
                'host': '192.168.1.30',  # mysql host
                'db': 'RankingPOGO',  # mysql database
                'port': 3306,  # mysql port
                'unix_socket': '/var/run/mysqld/mysqld.sock',  # mysql unix socket file
            },
            telegram_api=3818151,
            telegram_hash="52a698395ad88ac99841a5b7a8a0ccf3",
            phone="+34610931373")
