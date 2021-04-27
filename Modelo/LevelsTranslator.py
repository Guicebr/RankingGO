from typing import List
import logging
import Modelo.Translator as Translator

PROJECT_DIR = "/home/guillermocs/PycharmProjects/RankingGO/"
DIR = "Config/"
FILE = "XP_Level.xml"

logger = logging.getLogger(__name__)

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
        # Creeamos un diccionario y almacenamos los datos
        list_levels = Translator.XmlListConfig(root)

        for level_atr in list_levels:
            rootdict.append(0)
            rootdict[int(level_atr["level"]) - 1] = {"exptoup": int(level_atr["exptoup"]),
                                                     "totalxp": int(level_atr["totalxp"])}

        return rootdict

    def getLV_EXP (self, exp):
        """Metodo que recibe una cantidad de experiencia de tipo int, y devuelve una lista de pares clave valor
        con los niveles posibles y la experiencia que se tendría en cada uno de ellos [Nivel, Experiencia]
        IN: 79825637
        OUT: [[44,26325637],[45,200...],...]"""

        LV40EXP = int(self.level_dict[40-1]['totalxp'])
        if exp < LV40EXP:
            lv = self.getLevel_XP(exp)
            return [[lv, self.getExpLV(exp, lv)]]
        else:
            lv_exp = []
            levels = self.getLevels_XP(exp)
            for leveli in levels:
                lv_exp.append([leveli, self.getExpLV(exp, leveli)])
            return lv_exp
        return None


    def getExpLV(self, exp, lv):
        return exp - self.level_dict[lv - 1]['totalxp']

    def getLevel_XP(self, exp):
        """Encuentra el nivel de un jugador dada la experiencia.
        IN: Int Experiencia
        OUT: Int Nivel"""

        for leveli in range(len(self.level_dict)):
            if(exp - self.level_dict[leveli]['totalxp']) < 0:
                return leveli

    def getLevels_XP(self, exp):
        """Encuentra el nivel de un jugador dada la experiencia.
                IN: Int Experiencia
                OUT: List[Int] Nivel"""
        lvposibles = []
        for leveli in range(40-1, len(self.level_dict)):
            # print(leveli)
            if (exp - self.level_dict[leveli]['totalxp']) > 0:
                lvposibles.append(leveli+1)
        print(lvposibles)
        return lvposibles
