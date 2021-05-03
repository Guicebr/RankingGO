import os
import logging
import numpy as np
from fuzzywuzzy import fuzz

BASE = "Config/lang/"
DIR = "Config/lang/langtranslator.xml"
LANGS = ["es", "en"]
DEFAULT_LANG = "es"

logger = logging.getLogger(__name__)

import Modelo.Translator as Translator
import xml.etree.cElementTree as ET

class LangTranslator:
    """Clase encargaada de almacenar los datos de los distintos XML, que contienen la información de
     los Tipos de Ranking en diferentes idiomas."""

    xml_translate_dict = dict() # Estructura que almacena los idiomas
    xml_lang_pool = LANGS       # Array que almacena los idiomas disponibles

    def __init__(self):
        self.xml_translate_dict = self.parseXMLtoDict

    @property
    def parseXMLtoDict(self):
        """Crea un diccionario que almacena los ditintos idiomas, cada uno con su Id y TipoRanking
        almacenando el nombre"""
        rootdict = dict()

        # Obtenemos el nombre sel fichero con el directorio y el idioma

        tree = ET.parse(DIR)
        root = tree.getroot()

        # Creeamos un diccionario y almacenamos los datos
        list_words = Translator.XmlListConfig(root)

        # print(list_words)
        # for typerank_i in list_typerank:
        #     # Almacenamos en nuestro diccionario final las ids y los trs
        #     dict_lang_i[self.ID][typerank_i["id"]] = typerank_i["text"]
        #     dict_lang_i[self.TR][typerank_i["name"]] = typerank_i["text"]

        for word in list_words:
            rootdict[word['name']] = dict()
            # print(word)
            for key in word.keys():
                rootdict[word['name']][key] = word[key]

        return rootdict

    def getWordLang(self, name, lang):
        try:
            return self.xml_translate_dict[name][lang]
        except KeyError:
            return self.xml_translate_dict[name][DEFAULT_LANG]



