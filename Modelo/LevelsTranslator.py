import os
import logging
from typing import List, Any

import numpy as np
from fuzzywuzzy import fuzz

DIR = "Config/"
FILE = "XP_Level.xml"

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO, filename='../Logs/translate.log')
# logger = logging.getLogger(__name__)

import xml.etree.cElementTree as ET
class LevelsTranslator:
    """Clase encargaada de almacenar"""

    level_dict: List[int]

    def __init__(self):
        self.level_dict = self.parseXMLtoDict()

    def parseXMLtoDict(self):
        """"""
        rootdict: List[int] = []

        # Obtenemos el nombre sel fichero con el directorio y el idioma
        file = DIR + FILE
        tree = ET.ElementTree(file=file)

        # Obtenemos la raiz
        root = tree.getroot()

        # Recorremos el árbol
        cols = list(root)
        for row in cols:
            # Creeamos un diccionario y almacenamos los datos
            rootdict.append(0)
            temp_dict = dict()

            list_rows = list(row)
            for level_atr in list_rows:
                temp_dict[level_atr.tag] = level_atr.text
                #print("%s=%s" % (level_atr.tag, level_atr.text))
            # print(temp_dict)

            rootdict[int(temp_dict["level"])-1] = {"exptoup": int(temp_dict["exptoup"]), "totalxp": int(temp_dict["totalxp"])}
        return rootdict


