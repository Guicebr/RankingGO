import operator

import pytesseract
from pytesseract import Output
from pytesseract import pytesseract
import cv2 as cv
from time import time
from xml.dom import minidom

import numpy as np
from Plugins import visionocr
from Modelo.TypeRanking import *
from Plugins import common_func as c_func
from functools import reduce

from Modelo import LevelsTranslator
from Modelo import TypeRankTranslator

CONFIGBOXDIR = 'Config/Box_OCR.xml'
SHOW_IMG = 0

carpeta = '/home/guillermocs/PycharmProjects/RankingGO/Imagenes/'

sel_img =0

ficheros_nick = ['mi8-es-nick-Wicisian-N.jpg', 'mi8t-es-nick-S1ckwhale-N.jpg', 'i11max-es-nick-PabloLuis94-N.jpg']

#0-6 mi8-es
ficheros_mi8 = ["mi8-es-battlegirl-38146-Y.jpg", "mi8-es-battle_legend-942-N.jpg", "mi8-es-champion-553-N.jpg",
                "mi8-es-collector-89891-Y.jpg", "mi8-es-jogger-120701-Y.jpg", "mi8-es-pokemon_ranger-3311-Y.jpg",
                "mi8-es-sightseer-1746-N.jpg"]

ficheros_8t = ["mi8t-es-battle_girl-10335-Y.jpg", "mi8t-es-battle_legend-646-N.jpg", "mi8t-es-champion-368-N.jpg",
               "mi8t-es-collector-34945-N.jpg", "mi8t-es-jogger-47252-N.jpg","mi8t-es-pokemon_ranger-1400-N.jpg",
               "mi8t-es-sightseer-712-N.jpg"]

ficheros_i11max = ["i11max-es-battle_girl-34582-Y.jpg", "i11max-es-battle_legend-383-N.jpg",
                   "i11max-es-champion-517-N.jpg", "i11max-es-collector-68657-Y.jpg", "i11max-es-jogger-122240-Y.jpg",
                   "i11max-es-pokemon_ranger-4053-Y.jpg", "i11max-es-sightseer-678-N.jpg"]

ficheros_iPad = ["iPad-es-battle_girl-3095-N.jpg", "iPad-es-battle_legend-487-N.jpg", "iPad-es-champion-277-N.jpg",
                 "iPad-es-collector-14021-N.jpg", "iPad-es-collector-90534-Y.jpg", "iPad-es-jogger-19701-N.jpg",
                 "iPad-es-pokemon_ranger-886-N.jpg", "iPad-es-sightseer-668-N.jpg"]
#7-13 mi8-en
#14-20 i11max-es
#ficheros = ficheros_mi8 + ficheros_8t + ficheros_i11max + ficheros_iPad
# ficheros = ficheros_mi8[5:6]

ficheros = ficheros_mi8[4:5]
print(ficheros)


def getValores(arr_names):
    arr_val = []
    for name in arr_names:
        arr_val.append([name.split("-")[3]])
    return arr_val

valores = getValores(ficheros)

# for i in range(len(valores)):
#     print(ficheros[i], valores[i])

def print_ocr_dict(d):
    n_text = len(d['text'])
    head = ("text", "par_num", "block_num", "line_num", "word_num", "config")
    conf = 0
    if n_text > 0:
        print((str(d['text'])))

        print("%20s\t %s\t %s\t %s\t %s\t %s" % head)
        for i in range(n_text):
        #if int(d['conf'][i]) > 50:
            if d['text'][i]:
                print("%20s\t %7s\t %9s\t %8s\t %8s\t %6s" %
                      (str(d['text'][i]), str(d['par_num'][i]), str(d['block_num'][i]),
                       str(d['line_num'][i]), str(d['word_num'][i]), str(d['conf'][i])))

def img_to_hOCR(sel_img, gauss1, gauss2, psmi):

    print(ficheros[sel_img])
    img = cv.imread(str(carpeta + ficheros[sel_img]), 0)
    img = cv.bitwise_not(img)
    img = cv.medianBlur(img, 3)
    img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, gauss1, gauss2)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    config = "--psm " + str(psmi) + " -c tessedit_create_hocr=1"
    print(config)

    # pytesseract.run_tesseract(img, output_filename_base="output_hocr", extension="jpg", config=config, lang="None")
    #pytesseract.run_tesseract('image.png', 'output', lang=None, boxes=False, config="hocr")
    pytesseract.run_tesseract(str(carpeta + ficheros[sel_img]), 'output', extension="jpg", lang=None, config="hocr")

# img_to_hOCR(0, 7, 7, 11)

def cmp_vec_i(arr1, arr2, posfin):

    if(len(arr1)>=len(arr2)):
        for i in range(len(arr2)):
            if arr1[i] != arr2[i] and i < posfin:
                return False
        return True
    else:
        for i in range(len(arr1)):
            if arr1[i] != arr2[i] and i < posfin:
                return False
        return True

def ocr_num_psm(psmi, crop_img, value):
    ratioval = 100

    value = value[0]
    #config = "--psm " + str(psmi)
    #custom_config = r'--oem 3 --psm 6 outputbase digits'
    config = "--oem 3 --psm " + str(psmi) +' outputbase digits'
    #print(config)
    z = pytesseract.image_to_data(crop_img, output_type=Output.DICT, config=config)
    # print_ocr_dict(z)
    # print(z)
    z = np.array(z['text'])

    for i in range(len(z)):
        z[i] = c_func.string_cleaner_for_num(z[i])
    x = np.chararray.isnumeric(z)

    # Define vectorizer, that apply function len to vector
    length_checker = np.vectorize(len)

    # Apply len_checker np_text and compare with nicktam to obtain an array.

    if len(z[x]):
        y = z[x][np.where(length_checker(z[x]) > 0)]
        return y
    else:
        return None

def get_OCRbox_for(device, name):

    ret = ()
    # parse an xml file by name
    mydoc = minidom.parse(CONFIGBOXDIR)
    items = mydoc.getElementsByTagName(device)
    for node in items:
        alist = node.getElementsByTagName(name)
        for a in alist:
            data = a.firstChild.data
    # (x, y, w, h) = (400, 665, 350, 555) #mixto

    (x, y, w, h) = (int(data.split(" ")[0]), int(data.split(" ")[1]), int(data.split(" ")[2]), int(data.split(" ")[3]))
    return (x, y, w, h)

def getNUM_from_freq(len_num_freq_arr, num_freq_arr):
    """ Devolver un string, de los caracteres que más se repiten para cada posicion
    num_freq_arr:Es un vector de vectores que contiene caracteres
    len_num_freq_array: Es la longitud del vector anterior """

    percentage = 0.90
    ret = ""
    tam_word = 0
    tot = 0
    arr_lens = []


    for i in range(len_num_freq_arr):
        length = len(num_freq_arr[i])
        arr_lens.append(length)
        tot += length
    print("Tamaño arrays de frecuencias %s, Suma %d" % (str(arr_lens), tot))


    sum = 0
    for i in range(len_num_freq_arr):
        sum += arr_lens[len_num_freq_arr-i-1]
        print(sum / tot)
        if(sum/tot >= percentage):
            tam_word = i+1
            break


    print("Tamaño de número =", tam_word)

    # Usamos Direcciones relativas para reducir el tamaño del array

    for i in range(tam_word):
        x = np.array(num_freq_arr[len_num_freq_arr-tam_word+i]).astype(np.int)
        # print(x)
        # print(np.bincount(x).argmax())
        # np.bincount(x).argmax() entero que aparece mas frecuentemente en el vector x
        ret += str(np.bincount(x).argmax())
    # print(ret)
    return ret

def gauss_Pruebas(sel_img, gaussParam, psm, bitwisebit):
    print(str(carpeta + ficheros[sel_img]))
    save = []
    num_freq_dict = {}
    tmp_max = [0,1,2] # Vector donde se almacenan las cadenas mas frecuentes
    n_max = 5 # Numero que indica cuantas cadenas frecuentes se deben almacenar

    device = ficheros[sel_img].split("-")[0]

    medal = str(ficheros[sel_img].split("-")[4].split(".")[0])
    nameocr = "medal" + str(medal)

    for gauss1 in gaussParam[0]:
        for gauss2 in gaussParam[1]:
            #print(str(carpeta + ficheros[sel_img]))
            img = cv.imread(str(carpeta + ficheros[sel_img]), 0)

            (x, y, w, h) = get_OCRbox_for(device, name=nameocr)
            img = img[y:y + h, x:x + w]

            if bitwisebit:
                img = cv.bitwise_not(img)

            img = cv.medianBlur(img, 3)
            start_time = time()
            img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, gauss1, gauss2)
            # img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, gauss1, gauss2)
            elapsed_time = time() - start_time
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

            if SHOW_IMG:
                cv.imshow('img', img)
                cv.waitKey(0)

            #retval, buf = cv.imencode(".tiff", img)

            cv.imwrite("out2.tiff", img)
            img = cv.imread("out2.tiff", 0)

            print("gauss1=%d gauss2=%d time: %.5f seconds" % (gauss1, gauss2, elapsed_time))

            for psmi in psm:

                # ret = ocr_num_psm(psmi, img, valores[sel_img])
                ret = ocr_num_psm(psmi, img, [""])
                if ret is not None:
                    for value in ret:
                        if value in num_freq_dict.keys():
                            num_freq_dict[value] += 1
                        else:
                            num_freq_dict[value] = 1
                    #save.append([gauss1, gauss2, psmi, ret, elapsed_time, sel_img])

                    tmp_max = []
                    arr_cpy = num_freq_dict.copy()

                    for i in range(n_max):
                        if len(arr_cpy):
                            a = max(arr_cpy, key=lambda key: arr_cpy[key])
                            tmp_max.append(a)
                            arr_cpy.pop(a)

                    save.append([gauss1, gauss2, psmi, tmp_max, elapsed_time, sel_img])

    print("Number Frequency", str(num_freq_dict))


    if(len(num_freq_dict) > 0):
        # Hallamos la longitud maxima de la cadena
        len_num_freq_arr = len(max(num_freq_dict.keys(), key=len))

        num_freq_arr = []

        for i in range(len_num_freq_arr):
            num_freq_arr.append([])

        for key in num_freq_dict:
            for num in range(num_freq_dict[key]):
                for char_index in range(len(key)):
                    index = len_num_freq_arr-len(key)+char_index
                    num_freq_arr[index].append(key[char_index])
        for arr in num_freq_arr:
            print("%s, %d" % (str(arr), len(arr)))


        ret_num_freq = getNUM_from_freq(len_num_freq_arr, num_freq_arr)
        print(ret_num_freq)
        # print(tmp_max)
        # save.append([0, 0, 0, [tmp_max], 0.000, sel_img])
        save.append([0, 0, 0, [ret_num_freq], 0.000, sel_img])
    return save

def print_save(results):

    for result in results:
        for save in result:
            s_img = save[5]
            print("%s;%s;%d;%d;%d;%s;%.5f" % (ficheros[s_img], valores[s_img],
                                              save[0], save[1], save[2], str(save[3]), save[4]))
        #print("Resultados Obtenidos %d" % (len(result)))


def trasform_image(filepath, bitwise, blur, threshold_type, tparam1, tparam2, showimg):
    # config = {"bitwise": False, "blur": 3, "threshold_type": 0,
    #           "tparam1": 7, "tparam2": 7, "showimg": 0}

    img = cv.imread(filepath, 0)
    if bitwise:
        img = cv.bitwise_not(img)
    img = cv.medianBlur(img, blur)
    if threshold_type == 0:
        print("threshold_type %s" % ("ADAPTIVE_THRESH_GAUSSIAN_C"))
        img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,
                                   tparam1, tparam2)
    else:
        print("threshold_type %s" % ("ADAPTIVE_THRESH_MEAN_C"))
        img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,
                                   tparam1, tparam2)

    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    cv.imwrite("out2.tiff", img)
    img = cv.imread("out2.tiff", 0)

    if showimg:
        cv.imshow('img', cv.resize(img, (480, 720)))
        cv.waitKey(0)

    return img


def image_to_rectangle(filepath, bitwise, blur, threshold_type, tparam1, tparam2, psmi, extrapsmi):

    aux = "--psm %s %s" % (str(psmi), str(extrapsmi))
    config = {"psm": aux}

    # crop-img
    # (x, y, w, h) = (400, 670, 275, 390)
    # img = img[y:y + h, x:x + w]

    img = trasform_image(filepath, bitwise, blur, threshold_type, tparam1, tparam2, showimg=0)

    d = pytesseract.image_to_data(img, output_type=Output.DICT, config=config["psm"])
    n_boxes = len(d['level'])
    n_text = len(d['text'])
    for box in range(n_boxes):
        (x, y, w, h) = (d['left'][box], d['top'][box], d['width'][box], d['height'][box])
        c = cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        print("%10s %4s %4s %4s %4s" % (d['text'][box], x, y, w, h))
    #print_ocr_dict(d)

    # (x, y, w, h) = (400, 900, 280, 200)
    # crop_img = img[y:y + h, x:x + w]

    cv.imshow('img', cv.resize(img, (480, 720)))
    cv.waitKey(0)

def main():
    if False:
        img = cv.imread(str(carpeta + ficheros[sel_img]), 0)

        img = cv.bitwise_not(img)
        img = cv.medianBlur(img, 3)

        # [[3,5,7,9,11,13],[1,2,3]]
        img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
        # img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)

        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        cv.imwrite("out2.tiff", img)
        img = cv.imread("out2.tiff", 0)

    #print(str(carpeta + ficheros[sel_img]))
    #visionocr.ocr_register(str(carpeta + ficheros[sel_img]), nick[sel_img])

    #visionocr.ocr_screenshot(str(carpeta + ficheros[sel_img]))

    # d = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 3")

    if False:

        (x, y, w, h) = (400, 900, 280, 200)
        # (x, y, w, h) = (460, 965, 160, 50)
        crop_img = img[y:y + h, x:x + w]
        # crop_img = img

        # psm = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        # gaussParam = [[3, 5, 7, 9, 11, 13], range(1, 11, 1)]

        psm = [11, 12]
        gaussParam = [[11, 13], range(7, 11, 1)]
        # gaussParam = [[11], [6]]
        results1 = []
        results2 = []

        for index_img in range(len(ficheros)):
            print(index_img)
            result = gauss_Pruebas(index_img, gaussParam, psm, 1)
            results1.append(result)

            # result = gauss_Pruebas(index_img, gaussParam, psm, 0)
            # results2.append(result)

        print("BITWISE_NOT ON")
        print_save(results1)
        print("BITWISE_NOT OFF")
        print_save(results2)


        # print(str(visionocr.ocr_pattern(img, datapattern["totalxp"])))

        # (x, y, w, h) = (d['left'][i]-10, d['top'][i]-10, d['width'][i]+20, d['height'][i]+20)

        print(str(ficheros[sel_img]))
        # (filepath, bitwise, blur, threshold_type, tparam1, tparam2, psmi, extrapsmi)
        image_to_rectangle(str(carpeta + ficheros[sel_img]), False, 3, 0, 7, 7, 11, "")

        # custom_config = r'--oem 3 --psm 6 outputbase digits'
        # print(pytesseract.image_to_string(img, config=custom_config))



        ficheros = ficheros_nick
        sel_img = 0
        print(str(ficheros[sel_img]))
        filepath = str(carpeta + ficheros[sel_img])
        # lv_translator = LevelsTranslator.LevelsTranslator()
        exp = 79825637
        # exp = 3556
        # f = lv_translator.getLV_EXP(exp)
        # print(f)
        amount = visionocr.ocrScreenshot_Amount_EXP(filepath, exp)
        print(amount)

def fichnameToDict(name):
    """i11max-es-battle_girl-34582-Y.jpg
     device-lang-med_al-value-gold.jpg"""
    dic = dict()
    dic['device'] = name.split("-")[0]
    dic['lang'] = name.split("-")[1]
    dic['tranking'] = name.split("-")[2]
    dic['value'] = name.split("-")[3]
    dic['medal'] = name.split("-")[4].split(".")[0]
    # print(str(dic))
    return dic

if True:

    tr_translator = TypeRankTranslator.TypeRankTranslator()
    xml_lang_sel = "es"
    ficheros = ficheros_mi8

    for index_img in range(len(ficheros)):
        filepath_user = carpeta + str(ficheros[index_img])
        # print(str(ficheros[index_img]))
        dic_fich = fichnameToDict(ficheros[index_img])
        cat_user = tr_translator.translate_DBtoHUMAN(xml_lang_sel, dic_fich["tranking"])
        amount_user = dic_fich["value"]

        cat = visionocr.ocrScreenshot_Type(filepath_user, cat_user)
        amount = visionocr.ocrScreenshot_Amount(filepath_user, amount_user)
        valid_data = cat and amount
        
        print("Fichero: %s \n Cat %s %s \n Amount %s %s\n ocrScreenshot: %s \n\n\n" %
              (filepath_user, cat_user, cat, amount_user, amount, valid_data))

if __name__ == '__main__':
    main()