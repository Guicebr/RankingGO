import os
import logging
import numpy as np
from fuzzywuzzy import fuzz

BASE = "Config/lang/type_ranking_"
DIR = "Config/lang"

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO, filename='../Logs/translate.log')
# logger = logging.getLogger(__name__)

import xml.etree.cElementTree as ET
class TypeRankTranslator:
    """Clase encargaada de almacenar los datos de los distintos XML, que contienen la información de
     los Tipos de Ranking en diferentes idiomas."""

    xml_translate_dict = dict() # Estructura que almacena los idiomas
    xml_lang_pool = []          # Array que almacena los idiomas disponibles

    def __init__(self):
        files = os.listdir(DIR)
        self.xml_lang_pool = self.getLangfromFiles(files)
        self.xml_translate_dict = self.parseXMLtoDict()

    def getLangfromFiles(self, arrfiles):
        """Lee un array con nombres de ficheros con la forma 'type_ranking_es.xml' y devuelve un array con los
         diferentes idiomas de los ficheros"""

        arrlang = []
        for file in arrfiles:
            # Formato -> type_ranking_es.xml
            lang = file.split("_")[2]
            lang = lang.split(".")[0]
            arrlang.append(lang)

        return arrlang

    def parseXMLtoDict(self):
        """Crea un diccionario que almacena los ditintos idiomas, cada uno con su Id y TipoRanking
        almacenando el nombre"""
        rootdict = dict()

        for lang in self.xml_lang_pool:
            #Creamos un nuevo diccionario y lo añadimos al diccionario root, con otros dos diccionarios 'id' y 'tr'
            dict_lang_i = {"id": dict(), "tr": dict()}
            rootdict[lang] = dict_lang_i

            # Obtenemos el nombre sel fichero con el directorio y el idioma
            file = BASE + str(lang) + ".xml"
            tree = ET.ElementTree(file=file)

            # Obtenemos la raiz
            root = tree.getroot()

            # Recorremos el árbol
            typerranks = list(root)
            for typerank in typerranks:
                list_typerank = list(typerank)
                #print(list_typerank)

                # Creeamos un diccionario y almacenamos los datos
                dict_typerank_i = dict()
                for typerank_i in list_typerank:
                    dict_typerank_i[typerank_i.tag] = typerank_i.text
                    #print("%s=%s" % (typerank_i.tag, typerank_i.text))
                # print(dict_typerank_i)

                # Almacenamos en nuestro diccionario final las ids y los trs
                dict_lang_i["id"][dict_typerank_i["id"]] = dict_typerank_i["text"]
                dict_lang_i["tr"][dict_typerank_i["name"]] = dict_typerank_i["text"]

        return rootdict

    def translate_HumantoSEL(self, lang, type_selector, type_rank):
        "Devuelve el id o el tipo_ranking del nombre pasado como parametro(type_rank)"

        seldict = self.xml_translate_dict[lang][type_selector]
        print(seldict)
        for key, value in seldict.items():
            if value == type_rank:
                return key

    def getlist_TypeRank(self, lang):
        """Devuelve una lista de todas las categorías disponibles, para el idioma pasado"""
        arr_type = []
        for id, name in self.xml_translate_dict[lang]["id"].items():
            arr_type.append(str(name))

        return arr_type

