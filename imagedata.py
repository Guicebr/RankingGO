import pytesseract
from pytesseract import Output
from pytesseract import pytesseract
import cv2 as cv

import numpy as np
from Plugins import visionocr
from Modelo.TypeRanking import *

from functools import reduce

carpeta = '/home/guillermocs/PycharmProjects/RankingGO/Imagenes/'

sel_img = 0
#ficheros = ['mi8-es-nick.jpg', '8t-en-nick.jpg', '8t-es-nick.jpg', 'i11max-es-nick.jpg']
nick = ["Wicisian", "S1ckwhale", "S1ckwhale", "PabloLuis94"]

ficheros = ['mi8-es-battle_girl.jpg', 'mi8-es-battle_legend.jpg', 'mi8-es-champion.jpg', 'mi8-es-collector.jpg',
             'mi8-es-jogger.jpg', 'mi8-es-pokemon_ranger.jpg', 'mi8-es-sightseer.jpg']

#ficheros = ['mi8-en-battle_girl.jpg', 'mi8-en-battle_legend.jpg', 'mi8-en-champion.jpg', 'mi8-en-collector.jpg','mi8-en-jogger.jpg', 'mi8-en-pokemon_ranger.jpg', 'mi8-en-sightseer.jpg']

img = cv.imread(str(carpeta + ficheros[sel_img]), 0)

img = cv.medianBlur(img, 3)
#img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

print(str(carpeta + ficheros[sel_img]))
#visionocr.ocr_register(str(carpeta + ficheros[sel_img]), nick[sel_img])

#visionocr.ocr_screenshot(str(carpeta + ficheros[sel_img]))

config = "--psm 3"
d = pytesseract.image_to_data(img, output_type=Output.DICT, config=config)

(x, y, w, h) = (235, 520, 40, 70)
crop_img = img[y:y + h, x:x + w]

pytesseract.image_to_string(crop_img, config="--psm 3")

#(x, y, w, h) = (d['left'][i]-10, d['top'][i]-10, d['width'][i]+20, d['height'][i]+20)


#z = visionocr.ocr_pattern(img, datapattern["totalxp"])

# a = pytesseract.image_to_boxes(img, output_type=Output.DICT)
n_boxes = len(d['level'])
n_text = len(d['text'])
print(d)
# print(a)

print("text\t par_num\t block_num\t line_num\t word_num")

for i in range(n_text):
    if d['text'][i]:
        print(str(d['text'][i]) + "\t" +
              str(d['par_num'][i]) + "\t" +
              str(d['block_num'][i]) + "\t" +
              str(d['line_num'][i]) + "\t" +
              str(d['word_num'][i]))

block = np.array(d['block_num'])
line = np.array(d['line_num'])
word = np.array(d['word_num'])


"""b=4
l= 1
w=1

nick = reduce(np.intersect1d, (np.where(block == b), np.where(line == l), np.where(word == w)))
print(nick)
print(d['text'][nick[0]])"""

for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    c = cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

cv.imshow('img', crop_img)

#print(z)
cv.waitKey(0)