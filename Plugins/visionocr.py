import os
import logging
import numpy as np
import re
import cv2 as cv
from time import time

from Modelo import TypeRankTranslator
from Modelo import LevelsTranslator
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
RATIO_CHECK = 80
RATIO_AMOUNT = 90
RATIO_AMOUNT_EXP = 100

xml_lang_selector = "es"
translator = TypeRankTranslator.TypeRankTranslator()
lv_translator = LevelsTranslator.LevelsTranslator()

def trasform_image(filepath, bitwise, blur, threshold_type, tparam1, tparam2, showimg):
    # config = {"bitwise": False, "blur": 3, "threshold_type": 0,
    #           "tparam1": 7, "tparam2": 7, "showimg": 0}

    img = cv.imread(filepath, 0)
    start_time = time()
    if bitwise:
        img = cv.bitwise_not(img)
    img = cv.medianBlur(img, blur)

    if threshold_type == 0:
        # print("threshold_type %s" % ("ADAPTIVE_THRESH_GAUSSIAN_C"))
        img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,
                                   tparam1, tparam2)
    else:
        # print("threshold_type %s" % ("ADAPTIVE_THRESH_MEAN_C"))
        img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,
                                   tparam1, tparam2)

    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    cv.imwrite("out2.tiff", img)
    img = cv.imread("out2.tiff", 0)

    if showimg:
        cv.imshow('img', cv.resize(img, (480, 720)))
        cv.waitKey(0)
    elapsed_time = time() - start_time
    # print("gauss1=%d gauss2=%d time: %.5f seconds" % (tparam1, tparam2, elapsed_time))
    return img
# ocr_register v1
# def ocr_register2(photo_file, nick):
#     user = UserData()
#     aux = "--psm %s %s" % (11, " ")
#     config = {"bitwise": False, "blur": 3, "threshold_type": 0,
#               "tparam1": 7, "tparam2": 7, "psm": aux, "showimg": 0}
#
#     filepath = os.path.expanduser('~') + '/' + str(photo_file.file_id)
#     # print(filepath)
#     photo_file.download(filepath)
#
#     img = trasform_image(filepath, bitwise=config["bitwise"], blur=config["blur"], threshold_type=config["threshold_type"],
#                          tparam1=config["tparam1"], tparam2=config["tparam2"], showimg=config["showimg"])
#
#     ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, config=config["psm"])
#
#     logger.info("OCR Start - Register")
#
#     user.nick = ocrRegister_Nick(nick, ocr_data)
#     user.jogger = ocrRegister_Distance(ocr_data)
#     user.collector = ocrRegister_Pokemon(ocr_data)
#     user.backpaker = ocrRegister_Pokestops(ocr_data)
#     user.totalxp = ocr_Experience(filepath)
#
#     # ocr_pattern_data = ocr_pattern(img, str(data_p['totalxp']))
#     # print("ocr_pattern_data", ocr_pattern_data)
#     # logger.info("Ocr_pattern_data %s", str(ocr_pattern_data))
#
#     os.remove(filepath)
#
#     print("ocr_registro return ", str(user))
#     logger.info("OCR End - Register User Data %s", str(user))
#
#     return user

def ocr_register(photo_file, nick):
    logger.info("OCR Start - Register")
    user = UserData()

    filepath = os.path.expanduser('~') + '/Fotos_RankingPOGO' + str(photo_file.file_id)
    photo_file.download(filepath)
    # print(filepath)

    user.nick = ocrRegister_Nick(filepath, nick)
    os.remove(filepath)
    print("ocr_registro return ", str(user))

    logger.info("OCR End - Register User Data %s", str(user))
    return user


def ocrRegister_Nick (filepath, nick):
    """Recibe la direccion a una imagen que se usa para validar el nick y
    devuelve el nick si se puede encontrar en la imagen, sino devuelve None"""

    config = {"bitwise": False, "blur": 3, "threshold_type": 0,
              "tparam1": 7, "tparam2": 7, "psm": "--psm %s %s" % (11, " "), "showimg": 0}

    img = trasform_image(filepath, bitwise=config["bitwise"], blur=config["blur"],
                         threshold_type=config["threshold_type"],
                         tparam1=config["tparam1"], tparam2=config["tparam2"], showimg=config["showimg"])

    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, config=config["psm"])

    np_text = np.array(ocr_data['text'])

    if nick is not None and arraycmp_string(np_text, nick, RATIO_NICK):
        nickname = nick
    else:
        nickname = None
        logger.info("Nick No valido")

    logger.info("Nickname %s", nickname)
    return nickname


def ocr_Experience(filepath):
    aux = "--psm %s %s" % (11, " ")
    config = {"bitwise": False, "blur": 3, "threshold_type": 0,
              "tparam1": 7, "tparam2": 7, "psm": aux, "showimg": 0}

    img = trasform_image(filepath, bitwise=config["bitwise"], blur=config["blur"], threshold_type=config["threshold_type"],
                         tparam1=config["tparam1"], tparam2=config["tparam2"], showimg=config["showimg"])

    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, config=config["psm"])

    arr_to_nums = np.vectorize(int)
    exp = ocr_type(ocr_data, "totalxp")

    print(exp)

    if len(exp) > 1 or len(exp) < 1:
        logger.info("Obtaining Exp with Data_pattern")
        try:
            exp = str(np.max(arr_to_nums(ocr_pattern(img, data_p['totalxp']))))
        except ValueError:
            logger.error("Obtaining Exp with Data_pattern and Error with Empty Array")
            return None
    else:
        # len == 1
        exp = str(exp[0])

    logger.info("Experience %s", exp)
    return exp


def ocr_Experience2(filepath):
    aux = "--psm %s %s" % (11, " ")
    config = {"bitwise": False, "blur": 3, "threshold_type": 0,
              "tparam1": 7, "tparam2": 7, "psm": aux, "showimg": 0}

    img = trasform_image(filepath, bitwise=config["bitwise"], blur=config["blur"], threshold_type=config["threshold_type"],
                         tparam1=config["tparam1"], tparam2=config["tparam2"], showimg=config["showimg"])

    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, config=config["psm"])

    arr_to_nums = np.vectorize(int)
    exp = ocr_type(ocr_data, "totalxp")
    print(exp)

    if len(exp) > 1 or len(exp) < 1:
        logger.info("Obtaining Exp with Data_pattern")
        try:

            # exp = str(np.max(arr_to_nums(ocr_pattern(img, data_p['totalxp']))))
            exp_dpattern = ocr_pattern(img, data_p['totalxp'])
            print("ocr_pattern(img, data_p['totalxp']) %s -> %s" % (str(exp_dpattern), np.max(arr_to_nums(exp_dpattern))))
            exp_num_psm = ocr_num_psm(11, img)
            print("ocr_num_psm(11, img) %s -> %s" % (str(exp_num_psm), np.max(arr_to_nums(exp_num_psm))))
            exp = 0
            print(exp)
        except ValueError:
            logger.error("Obtaining Exp with Data_pattern and Error with Empty Array")
            return None
    else:
        # len == 1
        exp = str(exp[0])

    logger.info("Experience %s", exp)
    return exp


def ocrRegister_Pokestops(ocr_data):
    pokestops = ocr_type(ocr_data, "backpaker")

    if len(pokestops) == 1:
        pokestops = str(pokestops[0])
    else:
        logger.info("Pokestops cannot be obtained")
        return None

    logger.info("Pokestops %s", pokestops)
    return pokestops


def ocrRegister_Pokemon(ocr_data):
    pokemon = ocr_type(ocr_data, "collector")

    if len(pokemon) == 1:
        pokemon = str(pokemon[0])
    else:
        logger.info("Not pokemon or not value")
        return None

    logger.info("Pokemon %s", pokemon)
    return pokemon


def ocrRegister_Distance(ocr_data):
    distance = ocr_type(ocr_data, "jogger")

    if len(distance) == 1:
        distance = str(distance[0])
        distance = float(str(distance[0:len(distance) - 1]) + "." + str(str(distance[len(distance) - 1:])))
        logger.info("Distance %s", distance)
    else:
        logger.info("Not distance or not value")
        return None

    return distance





# TODO: Modo auto
# def ocr_screenshot(photo_file):
#     """ Comment"""
#
#     logger.info("OCR Start - Screenshot Data")
#     #Añadir variable idioma/lang
#
#     #ImageData Screenshot
#     filepath = photo_file
#
#     filepath = os.path.expanduser('~') + '/' + str(photo_file.file_id)
#     photo_file.download(filepath)
#
#     img = cv.imread(filepath, 0)
#     img = cv.medianBlur(img, 3)
#     img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 3)
#     img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
#     ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 3")
#     # Comparar ocr_data[text] con typeranking -> Tipo/Type
#     # Obtener con data pattern el valor -> Cantidad/Amount
#
#     os.remove(filepath)
#
#     #print("ocr_registro return ", str(user))
#     logger.info("OCR End - Screenshot Data")
#     pass

def ocrScreenshot_CheckTyp_Amount(photo_file, tr_type, amount, nick):
    filepath = os.path.expanduser('~') + '/Fotos_RankingPOGO' + str(photo_file.file_id)
    # print(filepath)
    photo_file.download(filepath)

    # TODO: Import Image Data algorithm OCR tr_type and OCR amount
    # img = cv.imread(filepath, 0)
    #
    # img = cv.medianBlur(img, 3)
    # img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 3)
    # img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    # cv.imwrite("out2.tiff", img)
    # img = cv.imread("out2.tiff", 0)
    #
    # ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 11")
    # logger.info("OCR Screenshot - Check Type Amount")
    # np_text = np.array(ocr_data['text'])
    # print(np_text)

    if tr_type is None or amount is None:
        print("Uno de los datos esta vacio")
        return False
    else:
        # Si Tr_type = EXP:amount_valid = ocrExp, Else amount_valid = ocrAmount
        tr_cat = translator.translate_HumantoSEL(xml_lang_selector, "tr", tr_type)
        print("tr_cat %s" % tr_cat)

        if tr_cat == "totalxp":
            rank_valid = ocrScreenshot_Type(filepath, nick)
        else:
            rank_valid = ocrScreenshot_Type(filepath, tr_type)

        if rank_valid:
            if tr_cat == "totalxp":
                amount_valid = ocrScreenshot_Amount_EXP(filepath, amount)
            else:
                amount_valid = ocrScreenshot_Amount(filepath, amount)
            if amount_valid:
                logger.info("TypeRanking %s Amount %s" % (str(tr_type), str(amount)))
                return True
            else:
                logger.info("No se pudo encontrar la cantidad")
                return False
        else:
            logger.info("No se pudo encontrar el tipo de ranking", )
            return False


def ocrScreenshot_Type(filepath, tr_type):
    config = {"bitwise": False, "blur": 3, "threshold_type": 0,
              "tparam1": 11, "tparam2": 3, "showimg": 0, "psm": "--psm 3"}

    img = trasform_image(filepath, bitwise=config["bitwise"], blur=config["blur"], threshold_type=config["threshold_type"],
                         tparam1=config["tparam1"], tparam2=config["tparam2"], showimg=config["showimg"])

    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, config=config["psm"])

    logger.info("OCR Screenshot - Check Type")
    np_text = np.array(ocr_data['text'])
    print(str(np_text))

    words_trtype = str(tr_type).split(" ")
    valid = True

    for word in words_trtype:
        valid_word = arraycmp_string(np_text, str(word), RATIO_CHECK)
        valid = valid and valid_word

    return valid


def ocrScreenshot_Amount(filepath, amount):
    psm = [11, 12]
    gaussParam = [[11, 13], range(7, 11, 1)]
    arrnums = ocrScreenshot_NumberFreq(filepath, gaussParam, psm, bitwise=True)
    print(arrnums)
    return arraycmp_string(list(arrnums), str(amount), RATIO_AMOUNT)

def ocrScreenshot_Amount_EXP(filepath, amount):
    """"""
    psm = [11, 12]
    gaussParam = [[11, 13], range(7, 11, 1)]

    validlv_exp = False
    validtotalexp = False

    arrnums = ocrScreenshot_NumberFreq(filepath, gaussParam, psm, bitwise=False)
    LV_EXP = lv_translator.getLV_EXP(int(amount))
    # print(arrnums, LV_EXP)

    if arraycmp_string(list(arrnums), str(amount), RATIO_AMOUNT_EXP):
        validtotalexp = True

    for lv in LV_EXP:
        lvvalid = arraycmp_string(list(arrnums), str(lv[0]), RATIO_AMOUNT)
        expvalid = arraycmp_string(list(arrnums), str(lv[1]), RATIO_AMOUNT_EXP)
        # print("lvvalid %d %s; expvalid %d %s" % (lv[0], str(lvvalid), lv[1], str(expvalid)))
        if lvvalid and expvalid:
            validlv_exp = True

    valid = validlv_exp or validtotalexp
    return valid

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
    # print("blp sin duplicados", b_pos, l_pos, par_n_pos)

    # Find all block, lines and par in each array for find positions
    # Then merge position values to get filtered array
    a = np.where(np.isin(np_block, b_pos))
    b = np.where(np.isin(np_line, l_pos))
    c = np.where(np.isin(np_par_num, par_n_pos))

    r = reduce(np.intersect1d, (a, b, c))

    # print("a,b,c,r", a, b, c, r)
    dist = np_text[r]
    # print("Salida", dist)
    logger.info("Salida %s", dist)

    # If dist exits, remove char for find numeric words
    try:
        for i in range(len(dist)):
            dist[i] = c_func.string_cleaner_for_num(dist[i])

        d = np.chararray.isnumeric(dist)
        ret = dist[d]

        # print("Return", dist, dist[d], ret)

        logger.info("Ocr_Type %s Result OK %s.", type, ret)

        return ret

    except IndexError:
        logger.info("Ocr_Type Error %s Result NOK %s.", type, str(dist))
        return None


def ocr_pattern(img, pattern):
    match = []
    logger.info("Ocr_Pattern %s start.", pattern)
    # print("Pattern ", pattern)
    config = {"psm": "--psm 11"}

    d = pytesseract.image_to_data(img, output_type=Output.DICT, config=config["psm"])

    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            if re.match(pattern, d['text'][i]):
                (x, y, w, h) = (d['left'][i] - 10, d['top'][i] - 10, d['width'][i] + 20, d['height'][i] + 20)
                crop_img = img[y:y + h, x:x + w]
                match.append(str(pytesseract.image_to_string(crop_img, config=config["psm"])))

    # cv.imshow("cropped", crop_img)
    # print(str(match))

    for i in range(len(match)):
        match[i] = c_func.string_cleaner_for_num(match[i])

    logger.info("Ocr_Pattern %s Result OK %s.", pattern, str(match))

    return match


def arraycmp_string(arr, s, ratioval):
    """Compare a word with each string in array, if both are similar greater than RATIO_NICK ret TRUE"""
    max_ratio = 0
    i_max = 0
    for i in range(len(arr)):
        ratio = fuzz.ratio(arr[i], s)
        # print("%s cmp %s == %s\n"% (arr[i], s, ratio))
        if ratio > max_ratio:
            i_max = i
            max_ratio = ratio

    print("%s cmp %s == %s\n" % (arr[i_max], s, max_ratio))
    logger.info("%s cmp %s == %s\n", arr[i_max], s, max_ratio)
    if max_ratio > ratioval:
        # logger.info("%s cmp %s == %s\n", arr[i_max], s, max_ratio)
        return True
    else:
        return False


def ocr_num_psm(psmi, img):
    """Hace OCR a una imagen pasada, con el psmi dado, aplicando la busqueda de números
    Devuelve None o un Array de Numeros obtenidos"""

    # custom_config = r'--oem 3 --psm 6 outputbase digits'
    config = "--psm " + str(psmi)
    z = pytesseract.image_to_data(img, output_type=Output.DICT, config=config)
    z = np.array(z['text'])

    for i in range(len(z)):
        z[i] = c_func.string_cleaner_for_num(z[i])
    x = np.chararray.isnumeric(z)

    # Define vectorizer, that apply function len to vector
    length_checker = np.vectorize(len)

    # Comprueba que los valores devueltos tenga longitud mayor que 0
    if len(z[x]):
        y = z[x][np.where(length_checker(z[x]) > 0)]
        return y
    else:
        return None


def ocrScreenshot_NumberFreq(filepath, gaussParam, psm, bitwise):
    num_freq_dict = {}

    config = {"bitwise": bitwise, "blur": 3, "threshold_type": 0,
              "tparam1": 7, "tparam2": 7, "showimg": 0}

    for gauss1 in gaussParam[0]:
        for gauss2 in gaussParam[1]:

            img = trasform_image(filepath, bitwise=config["bitwise"], blur=config["blur"],
                                 threshold_type=config["threshold_type"],
                                 tparam1=gauss1, tparam2=gauss2, showimg=config["showimg"])

            for psmi in psm:
                ret = ocr_num_psm(psmi, img)
                if ret is not None:
                    for value in ret:
                        if value in num_freq_dict.keys():
                            num_freq_dict[value] += 1
                        else:
                            num_freq_dict[value] = 1

    # print("Number Frequency", str(num_freq_dict))
    return num_freq_dict
