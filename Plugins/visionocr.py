import os
import logging
import numpy as np
import re
import cv2 as cv

from Plugins import common_func as c_func
from Modelo.TypeRanking import typeranking as tr
from Modelo.TypeRanking import datapattern as data_p
from Modelo.UserData import UserData

from pytesseract import pytesseract
from pytesseract import Output
from functools import reduce
from fuzzywuzzy import fuzz

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='example.log')

logger = logging.getLogger(__name__)

RATIO_NICK = 80

def ocr_register(photo_file, nick):

    user = UserData()

    filepath = os.path.expanduser('~') + '/' + str(photo_file.file_id)
    #print(filepath)
    photo_file.download(filepath)

    img = cv.imread(filepath, 0)

    img = cv.medianBlur(img, 3)
    img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 3)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 3")

    logger.info("OCR Start")

    user.data["nick"] = ocrRegister_Nick(nick, ocr_data)
    user.data["jogger"] = ocrRegister_Distance(ocr_data)
    user.data["collector"] = ocrRegister_Pokemon(ocr_data)
    user.data["backpaker"] = ocrRegister_Pokestops(ocr_data)
    user.data["totalxp"] = ocrRegister_Experience(ocr_data, img)

    logger.info("User Data Register %s", str(user))
    #os.remove(filepath)

    print("ocr_registro return ", str(user))

    return str(user)


def ocrRegister_Experience(ocr_data, img):
    exp = None
    try:
        exp = ocr_type(ocr_data, "totalxp")
        # print(experience, len(experience))
        if len(exp) == 0:
            logger.info("Obtaining Exp with Data_pattern")
            exp = str(np.max(ocr_pattern(img, data_p['totalxp'])))
        else:
            exp = str(np.max(exp))

        # print("Exp", experience)
        logger.info("Experience %s", exp)
    except:
        logger.warning("Exp cannot be obtained")
    return exp


def ocrRegister_Pokestops(ocr_data):
    pokestops = None
    try:
        pokestops = ocr_type(ocr_data, "backpaker")[-1]
        logger.info("Pokestops %s", pokestops)
    except IndexError:
        logger.info("Pokestops cannot be obtained")
    return pokestops


def ocrRegister_Pokemon(ocr_data):
    pokemon = None
    try:
        pokemon = ocr_type(ocr_data, "collector")[-1]
        logger.info("Pokemon %s", pokemon)
    except IndexError:
        logger.info("Pokemon cannot be obtained")
    return pokemon


def ocrRegister_Distance(ocr_data):
    distance = None
    try:
        distance = ocr_type(ocr_data, "jogger")[-1]
        distance = float(str(distance[0:len(distance) - 1]) + "." + str(str(distance[len(distance) - 1:])))
        logger.info("Distance %s", distance)
    except IndexError:
        logger.info("Not distance or not value")
    return distance


def ocrRegister_Nick(nick, ocr_data):
    nickname = None
    np_text = np.array(ocr_data['text'])

    if arraycmp_string(np_text, nick) and nick is not None:
        nickname = nick
    else:
        nickname = None
        logger.info("Nick No valido")

    logger.info("Nickname %s", nickname)
    return nickname


def ocr_type(ocr_data, type):
    logger.info("Ocr_Type %s start.", type)

    # Prepare numpy arrays
    np_text = np.array(ocr_data['text'])
    np_block = np.array(ocr_data['block_num'])
    np_line = np.array(ocr_data['line_num'])
    np_par_num = np.array(ocr_data['par_num'])

    b_pos = []
    l_pos = []
    par_n_pos = []

    search_chars = tr[type]

    logging.info(search_chars)
    # print(tr["totalxp"])
    # Find experience keywords in ocr_text
    # to obtain block,line nums
    for i in search_chars:
        t_pos = np.where(np.chararray.lower(np_text) == i.lower())
        b_pos = np.append(b_pos, np_block[t_pos])
        l_pos = np.append(l_pos, np_line[t_pos])
        par_n_pos = np.append(par_n_pos, np_par_num[t_pos])
        logging.info("t,b,l %s %s %s %s %s", str(t_pos), str(np_text[t_pos]), str(b_pos), str(l_pos), str(par_n_pos))

    # Remove duplicates
    b_pos = np.unique(b_pos)
    l_pos = np.unique(l_pos)
    par_n_pos = np.unique(par_n_pos)
    #print("blp sin duplicados", b_pos, l_pos, par_n_pos)

    # Find all block, lines and par in each array for find positions
    # Then merge position values to get filtered array
    a = np.where(np.isin(np_block, b_pos))
    b = np.where(np.isin(np_line, l_pos))
    c = np.where(np.isin(np_par_num, par_n_pos))

    r = reduce(np.intersect1d, (a, b, c))

    #print("a,b,c,r", a, b, c, r)
    dist = np_text[r]
    #print("Salida", dist)
    logger.info("Salida %s", dist)

    #If dist exits, remove char for find numeric words
    try:
        for i in range(len(dist)):
            dist[i] = c_func.string_cleaner_for_num(dist[i])

        d = np.chararray.isnumeric(dist)
        ret = dist[d]

        #print("Return", dist, dist[d], ret)

        logger.info("Ocr_Type %s Result OK %s.", type, ret)

        return ret

    except IndexError:
        logger.info("Ocr_Type Error %s Result NOK %s.", type, str(dist))
        return None


def ocr_pattern(img, pattern):

    match = []
    logger.info("Ocr_Pattern %s start.", pattern)
    # print("Pattern ", pattern)
    d = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 3")

    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            if re.match(pattern, d['text'][i]):
                (x, y, w, h) = (d['left'][i]-10, d['top'][i]-10, d['width'][i]+20, d['height'][i]+20)
                crop_img = img[y:y + h, x:x + w]
                match.append(str(pytesseract.image_to_string(crop_img, config="--psm 3")))

    #cv.imshow("cropped", crop_img)
    #print(str(match))

    for i in range(len(match)):
        match[i] = c_func.string_cleaner_for_num(match[i])

    logger.info("Ocr_Pattern %s Result OK %s.", pattern, str(match))

    return match

###
# Compare a word with each string in array, if both are similar greater than RATIO_NICK ret TRUE
#
def arraycmp_string(arr, s):
    for i in range(len(arr)):
        ratio = fuzz.ratio(arr[i], s)

        if ratio >= RATIO_NICK:
            logger.info("%s cmp %s == %s\n", arr[i], s, ratio)
            return True

    return False

"""def nickOCR(ocr_data, nick):
    # Declare variables
    nicktam = len(nick)
    np_text = np.array(ocr_data['text'])

    # Define vectorizer, that apply function len to vector
    length_checker = np.vectorize(len)

    # Apply len_checker np_text and compare with nicktam to obtain an array.
    # This array have all words with the same length as nicktam
    np_nick = np_text[np.where(length_checker(np_text) == nicktam)]
    print(np_nick)

    return arraycmp_string(np_nick, nick) """


