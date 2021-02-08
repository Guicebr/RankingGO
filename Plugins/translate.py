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
    xml_translate_dict = dict()
    xml_lang_pool = []
    def __init__(self):
        files = os.listdir(DIR)
        self.getLangfromFiles(files)
        self.parseXMLtoDict()

    def getLangfromFiles(self, arrfiles):

        arrlang = []
        for file in arrfiles:
            # Formato -> type_ranking_es.xml
            lang = file.split("_")[2]
            lang = lang.split(".")[0]
            arrlang.append(lang)

        self.xml_lang_pool = arrlang

    def parseXMLtoDict(self):

        rootdict = dict()


        for lang in self.xml_lang_pool:
            #Creamos un nuevo diccionario y lo añadimos al diccionario root
            dict_lang_i_id = dict()
            dict_lang_i_tr = dict()
            dict_lang_i = {"id": dict_lang_i_id, "tr": dict_lang_i_tr}
            rootdict[lang] = dict_lang_i

            # parse an xml file by name
            file = BASE + str(lang) + ".xml"
            tree = ET.ElementTree(file=file)

            # obtenemos la raiz
            root = tree.getroot()

            # recorremos el árbol
            typerranks = list(root)
            for typerank in typerranks:
                list_typerank = list(typerank)
                #print(list_typerank)

                dict_typerank_i = dict()
                for typerank_i in list_typerank:
                    dict_typerank_i[typerank_i.tag] = typerank_i.text
                    #print("%s=%s" % (typerank_i.tag, typerank_i.text))
                print(dict_typerank_i)

                dict_lang_i["id"][dict_typerank_i["id"]] = dict_typerank_i["text"]
                dict_lang_i["tr"][dict_typerank_i["name"]] = dict_typerank_i["text"]

        self.xml_translate_dict = rootdict

    def translate_HumantoSEL(self, lang, type_selector, type_rank):
        "Devuelve el id o el tipo_ranking del nombre pasado como parametro(type_rank)"
        retsel = ""
        seldict = self.xml_translate_dict[lang][type_selector]
        for key, value in seldict.items():
            if value == type_rank:
                return retsel

    def getlist_TypeRank(self, lang):
        arr_type = []
        for id, name in self.xml_translate_dict[lang]["id"].items():
            arr_type.append(str(name))

        return arr_type

