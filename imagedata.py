import pytesseract
from pytesseract import Output
from pytesseract import pytesseract
import cv2 as cv

import numpy as np
from Plugins import visionocr
from Modelo import TypeRanking

from functools import reduce

carpeta = 'Imagenes/'

sel_img = 0
ficheros = ['nickphotoesmi8.jpg', 'nickphotoen8t.jpg', 'nickphotoes8t.jpg', 'nickphotnesiphone11max.jpg']
nick = ["Wicisian", "S1ckwhale", "S1ckwhale", "PabloLuis94"]


img = cv.imread(str(carpeta + ficheros[sel_img]), 0)

img = cv.medianBlur(img, 3)
##img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
img = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 3)
img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
d = pytesseract.image_to_data(img, output_type=Output.DICT, config="--psm 3")

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

"""for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    c = cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)"""

# print("Busqueda nick")
# print(visionocr.nickOCR(d,"S1ckwhale"))


# print(visionocr.expOCR(d))

# print("Busqueda Distancia")
# print(visionocr.expDist(d))
nickname, exp, distance, pokestops, pokemon = range(5)

print("Validación del Nick")
try:
    if visionocr.nickOCR(d, nick[sel_img]):
        nickname = nick[sel_img]
except:
    print("Nick No valido")

print("Busqueda Distancia")
try:
    distance = visionocr.ocr_type(d, "jogger")
    distance = float(str(distance[0:len(distance) - 1]) + "." + str(str(distance[len(distance) - 1:])))
    print(distance)
except:
    print("Not distance or not value")

print("Busqueda Atrapados")
try:
    pokemon = visionocr.ocr_type(d, "collector")
    print(pokemon)
except:
    print("Pokemon cannot be obtained")

print("Busqueda Pokeparadas")
try:
    pokestops = visionocr.ocr_type(d, "backpaker")
    print(pokestops)
except:
    print("Pokestops cannot be obtained")

print("Busqueda Exp")
try:
    #experience = visionocr.ocr_type(d, "totalxp")
    exp = None
    if exp is None:
        print("try2")
        exp = visionocr.ocr_pattern(img, TypeRanking.datapattern['totalxp'])

    print("Exp", exp)
except:
    print("Exp cannot be obtained")

print(nickname, distance, pokemon, pokestops, exp)

# cv.imshow('img', img)
cv.waitKey(0)

""" Syntax: cv2.rectangle(image, start_point, end_point, color, thickness)

    Parameters:
    image: It is the image on which rectangle is to be drawn.
    start_point: It is the starting coordinates of rectangle. The coordinates are represented as tuples of two values i.e. (X coordinate value, Y coordinate value).
    end_point: It is the ending coordinates of rectangle. The coordinates are represented as tuples of two values i.e. (X coordinate value, Y coordinate value).
    color: It is the color of border line of rectangle to be drawn. For BGR, we pass a tuple. eg: (255, 0, 0) for blue color.
    thickness: It is the thickness of the rectangle border line in px. Thickness of -1 px will fill the rectangle shape by the specified color.

    Return Value: It returns an image. """
