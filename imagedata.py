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

sel_img = 14

#ficheros = ['mi8-es-nick.jpg', '8t-en-nick.jpg', '8t-es-nick.jpg', 'i11max-es-nick.jpg']
nick = ["Wicisian", "S1ckwhale", "S1ckwhale", "PabloLuis94"]

#0-6 mi8-es
#7-13 mi8-en
#14-20 i11max-es
ficheros = ['mi8-es-battle_girl.jpg', 'mi8-es-battle_legend.jpg', 'mi8-es-champion.jpg', 'mi8-es-collector.jpg',
            'mi8-es-jogger.jpg', 'mi8-es-pokemon_ranger.jpg', 'mi8-es-sightseer.jpg',
            'mi8-en-battle_girl.jpg', 'mi8-en-battle_legend.jpg', 'mi8-en-champion.jpg', 'mi8-en-collector.jpg',
            'mi8-en-jogger.jpg', 'mi8-en-pokemon_ranger.jpg', 'mi8-en-sightseer.jpg',
            'i11max-es-battle_girl.png', 'i11max-es-battle_legend.png', 'i11max-es-champion.png', 'i11max-es-collector.png',
            'i11max-es-jogger.png', 'i11max-es-pokemon_ranger.png', 'i11max-es-sightseer.png'
            ]

valores = [["1204", "4000", "38146"], ["1205", "1000", "942"], ["1205", "1000", "553"], ["1204", "50000", "89891"],
            ["1157", "10000", "120701"], ["1157", "2500", "3311"], ["1157", "2000", "1746"],
            ["1214", "4000", "38146"], ["1214", "1000", "942"], ["1214", "1000", "553"], ["1214", "50000", "89892"],
            ["1214", "10000", "120703"], ["1214", "2500", "3314"], ["1215", "2000", "1746"],
            ["4000", "34582"], ["1000", "383"], ["1000", "517"], ["50000", "68657"],
            ["10000", "122240"], ["2500", "4053"], ["1000", "678"]
           ]
#ficheros = ['mi8-en-battle_girl.jpg', 'mi8-en-battle_legend.jpg', 'mi8-en-champion.jpg', 'mi8-en-collector.jpg','mi8-en-jogger.jpg', 'mi8-en-pokemon_ranger.jpg', 'mi8-en-sightseer.jpg']

def print_ocr_dict(d):
    n_text = len(d['text'])
    conf = 0
    if n_text > 0:
        print((str(d['text'])))
        print("text\t par_num\t block_num\t line_num\t word_num\t config")
        for i in range(n_text):
        #if int(d['conf'][i]) > 50:
            if d['text'][i]:
                print(str(d['text'][i]) + "\t" +
                      str(d['par_num'][i]) + "\t" +
                      str(d['block_num'][i]) + "\t" +
                      str(d['line_num'][i]) + "\t" +
                      str(d['word_num'][i]) + "\t" +
                      str(d['conf'][i]))

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

    config = "--psm " + str(psmi)
    #print(config)
    z = pytesseract.image_to_data(crop_img, output_type=Output.DICT, config=config)
    # print_ocr_dict(z)
    # print(z)
    z = np.array(z['text'])

    for i in range(len(z)):
        z[i] = c_func.string_cleaner_for_num(z[i])
    x = np.chararray.isnumeric(z)

    """if visionocr.arraycmp_string(z[x], value[2], ratioval):
            print(config)
            print(str(z[x]))"""

    #if len(z[x]) >= 3:
    #   if z[x][0] == value[0] and z[x][1] == value[1] and z[x][2] == value[2]:
    #       print(config)
    #       print(str(z[x]))
    print(str(z[x]))
    if len(z[x]) >= len(value):
        print(cmp_vec_i(z[x], value, len(value)))
        if cmp_vec_i(z[x], value, len(value)):
            print(config)
            print(str(z[x]))

            return z[x]
        else:
            return None







if __name__ == '__main__':

    img = cv.imread(str(carpeta + ficheros[sel_img]), 0)

    img = cv.bitwise_not(img)
    img = cv.medianBlur(img, 3)

    # [[3,5,7,9,11,13],[1,2,3]]
    img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    #img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)

    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)


    print(str(carpeta + ficheros[sel_img]))
    #visionocr.ocr_register(str(carpeta + ficheros[sel_img]), nick[sel_img])

    #visionocr.ocr_screenshot(str(carpeta + ficheros[sel_img]))

    d = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 3")




    (x, y, w, h) = (400, 900, 280, 200)
    #(x, y, w, h) = (460, 965, 160, 50)
    crop_img = img[y:y + h, x:x + w]
    #crop_img = img

    psm = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    #psm = [11]

    save = []
    gaussParam = [[3, 5, 7, 9, 11, 13], range(1, 11, 1)]
    #gaussParam = [[3, 5], range(2, 12, 2)] #Corto
    for gauss1 in gaussParam[0]:
        for gauss2 in gaussParam[1]:
            img = cv.imread(str(carpeta + ficheros[sel_img]), 0)
            img = cv.bitwise_not(img)
            img = cv.medianBlur(img, 3)
            start_time = time()
            img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, gauss1, gauss2)
            #img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, gauss1, gauss2)
            elapsed_time = time() - start_time

            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            print("gauss1=%d gauss2=%d time: %.5f seconds" % (gauss1, gauss2, elapsed_time))
            #print("Elapsed time: %.10f seconds." % elapsed_time)
            for psmi in psm:
                ret = ocr_num_psm(psmi, img, valores[sel_img])
                if ret is not None:
                    save.append([gauss1, gauss2, psmi, ret, elapsed_time])

    print("SAVE")
    print("Valores esperados", str(valores[sel_img]))
    for i in save:
        print("%d;%d;%d;%s;%.5f" % (i[0], i[1], i[2], str(i[3]), i[4]))


    #print(str(visionocr.ocr_pattern(img, datapattern["totalxp"])))

    #(x, y, w, h) = (d['left'][i]-10, d['top'][i]-10, d['width'][i]+20, d['height'][i]+20)




    # a = pytesseract.image_to_boxes(img, output_type=Output.DICT)
    n_boxes = len(d['level'])
    n_text = len(d['text'])
    #print(d)
    # print(a)





    #print_ocr_dict(d)

    block = np.array(d['block_num'])
    line = np.array(d['line_num'])
    word = np.array(d['word_num'])


    """b=4
    l= 1
    w=1
    
    nick = reduce(np.intersect1d, (np.where(block == b), np.where(line == l), np.where(word == w)))
    print(nick)
    print(d['text'][nick[0]])"""

    for psmi in range(n_boxes):
        (x, y, w, h) = (d['left'][psmi], d['top'][psmi], d['width'][psmi], d['height'][psmi])
        c = cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

    #cv.imshow('img', crop_img)

    #print(z)
    #print_ocr_dict(z)
    cv.waitKey(0)