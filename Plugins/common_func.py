import time

def string_cleaner_for_num(word):
    ret = ""

    for i in filter(str.isdigit, word):
        ret = ret + i
    return ret

def delay():
    time.sleep(3)


