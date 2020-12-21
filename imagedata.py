import operator

import pytesseract
from pytesseract import Output
from pytesseract import pytesseract
import cv2 as cv
from time import time

import numpy as np
from Plugins import visionocr
from Modelo.TypeRanking import *
from Plugins import common_func as c_func
from functools import reduce

carpeta = '/home/guillermocs/PycharmProjects/RankingGO/Imagenes/'







sel_img =0

#ficheros_nick = ['mi8-es-nick.jpg', '8t-en-nick.jpg', '8t-es-nick.jpg', 'i11max-es-nick.jpg']
#nick = ["Wicisian", "S1ckwhale", "S1ckwhale", "PabloLuis94"]

#0-6 mi8-es
ficheros_mi8 = ["mi8-es-battle_girl-38146-Y.jpg", "mi8-es-battle_legend-942-N.jpg", "mi8-es-champion-553-N.jpg",
                "mi8-es-collector-89891-Y.jpg", "mi8-es-jogger-120701-Y.jpg", "mi8-es-pokemon_ranger-3311-Y.jpg",
                "mi8-es-sightseer-1746-N.jpg"]
ficheros_8t = ["8t-es-battle_girl-10335-Y.jpg", "8t-es-battle_legend-646-N.jpg", "8t-es-champion-368-N.jpg",
               "8t-es-collector-34945-N.jpg", "8t-es-jogger-47252-N.jpg","8t-es-pokemon_ranger-1400-N.jpg",
               "8t-es-sightseer-712-N.jpg"]
ficheros_i11max = ["i11max-es-battle_girl-34582-Y.jpg", "i11max-es-battle_legend-383-N.jpg",
                   "i11max-es-champion-517-N.jpg", "i11max-es-collector-68657-Y.jpg", "i11max-es-jogger-122240-Y.jpg",
                   "i11max-es-pokemon_ranger-4053-Y.jpg", "i11max-es-sightseer-678-N.jpg"]
ficheros_iPad = ["iPad-es-battle_girl-3095-N.jpg", "iPad-es-battle_legend-487-N.jpg", "iPad-es-champion-277-N.jpg",
                 "iPad-es-collector-14021-N.jpg", "iPad-es-collector-90534-Y.jpg", "iPad-es-jogger-19701-N.jpg",
                 "iPad-es-pokemon_ranger-886-N.jpg", "iPad-es-sightseer-668-N.jpg"]
#7-13 mi8-en
#14-20 i11max-es

ficheros = ficheros_i11max[0:1]

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
    config = "--psm " + str(psmi)
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
    # This array have all words with the same length as nicktam


    """if visionocr.arraycmp_string(z[x], value[2], ratioval):
            print(config)
            print(str(z[x]))"""

    #if len(z[x]) >= 3:
    #   if z[x][0] == value[0] and z[x][1] == value[1] and z[x][2] == value[2]:
    #       print(config)
    #       print(str(z[x]))
    #print(str(z[x]), value)

    # if len(z[x]):
    #     #print(cmp_vec_i(z[x], value, len(value)))
    #     if visionocr.arraycmp_string(z[x], str(value), ratioval):
    #         print(config)
    #         print(str(z[x]))
    #
    #         return z[x]
    #     else:
    #         return None

    if len(z[x]):
        y = z[x][np.where(length_checker(z[x]) > 2)]

        # print("length_checker(z[x])", length_checker(z[x]))
        # print("np.where(length_checker(z[x]) > 1)", np.where(length_checker(z[x]) > 1))
        # print("y", y)
        return y
    else:
        return None


def image_to_rectangle(filepath, gauss1, gauss2, psmi):

    img = cv.imread(filepath, 0)

    # (x, y, w, h) = (400, 670, 275, 390)
    # img = img[y:y + h, x:x + w]

    img = cv.bitwise_not(img)
    img = cv.medianBlur(img, 3)
    img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, gauss1, gauss2)
    # img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    config = "--psm " + str(psmi)

    d = pytesseract.image_to_data(img, output_type=Output.DICT, config=config)
    n_boxes = len(d['level'])
    n_text = len(d['text'])
    for box in range(n_boxes):
        (x, y, w, h) = (d['left'][box], d['top'][box], d['width'][box], d['height'][box])
        c = cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        print("%10s %4s %4s %4s %4s" % (d['text'][box], x, y, w, h))
    #print_ocr_dict(d)

    # (x, y, w, h) = (400, 900, 280, 200)
    # crop_img = img[y:y + h, x:x + w]

    cv.imshow('img', cv.resize(img, (480,720)))
    cv.waitKey(0)


def gauss_Pruebas(sel_img, gaussParam, psm, bitwisebit):


    save = []
    num_freq_dict = {}
    tmp_max = [0,1,2]

    for gauss1 in gaussParam[0]:
        for gauss2 in gaussParam[1]:
            # print(str(carpeta + ficheros[sel_img]))
            img = cv.imread(str(carpeta + ficheros[sel_img]), 0)

            #(x, y, w, h) = (400, 670, 275, 390) #mi8
            #(x, y, w, h) = (510, 665, 240, 555) #i11
            # (x, y, w, h) = (400, 665, 350, 555) #mixto
            (x, y, w, h) = (215, 325, 428, 707)  # mixto v2
            img = img[y:y + h, x:x + w]

            if bitwisebit:
                img = cv.bitwise_not(img)

            img = cv.medianBlur(img, 3)
            start_time = time()
            img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, gauss1, gauss2)
            # img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, gauss1, gauss2)
            elapsed_time = time() - start_time
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

            # cv.imshow('img', img)
            # cv.waitKey(0)

            #retval, buf = cv.imencode(".tiff", img)

            cv.imwrite("out2.tiff", img)
            img = cv.imread("out2.tiff", 0)

            # cv.imshow('img', img)
            # cv.waitKey(0)

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

                    for i in range(10):
                        if len(arr_cpy):
                            a = max(arr_cpy, key=lambda key: arr_cpy[key])
                            tmp_max.append(a)
                            arr_cpy.pop(a)



                    save.append([gauss1, gauss2, psmi, tmp_max, elapsed_time, sel_img])

            #print("Number Frequency", str(num_freq_dict))
            #print(tmp_max)
    save.append([0, 0, 0, [tmp_max[1]], 0.000, sel_img])
    return save



if __name__ == '__main__':

    img = cv.imread(str(carpeta + ficheros[sel_img]), 0)

    img = cv.bitwise_not(img)
    img = cv.medianBlur(img, 3)

    # [[3,5,7,9,11,13],[1,2,3]]
    img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    #img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)

    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)


    #print(str(carpeta + ficheros[sel_img]))
    #visionocr.ocr_register(str(carpeta + ficheros[sel_img]), nick[sel_img])

    #visionocr.ocr_screenshot(str(carpeta + ficheros[sel_img]))

    d = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 3")




    (x, y, w, h) = (400, 900, 280, 200)
    #(x, y, w, h) = (460, 965, 160, 50)
    crop_img = img[y:y + h, x:x + w]
    #crop_img = img

    #psm = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    gaussParam = [[3, 5, 7, 9, 11, 13], range(2, 11, 2)]

    psm = [11, 12]
    #gaussParam = [[13], [4]]
    results1 = []

    for index_img in range(len(ficheros)):
        print(index_img)
        result = gauss_Pruebas(index_img, gaussParam, psm, 1)
        results1.append(result)

    #gaussParam = [[11], [6]]

    print("RESULTS NOTBITWISE")
    print("Valores esperados", str(valores[sel_img]))
    for result in results1:
        for save in result:
            s_img = save[5]
            print("%s;%s;%d;%d;%d;%s;%.5f" % (ficheros[s_img], valores[s_img],
                                              save[0], save[1], save[2], str(save[3]), save[4]))
            #print("Resultados Obtenidos %d" % (len(result)))


    #print(str(visionocr.ocr_pattern(img, datapattern["totalxp"])))

    #(x, y, w, h) = (d['left'][i]-10, d['top'][i]-10, d['width'][i]+20, d['height'][i]+20)

    # #sel_img = 8
    # #print(str(ficheros[sel_img]))
    # image_to_rectangle(str(carpeta + ficheros[sel_img]), 7, 7, 11)