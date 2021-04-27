from Database import dbhelper
import xml.etree.cElementTree as ET

BASE = "Config/tr_lang/type_ranking_"
DIR = "Config/tr_lang"
LANG = "en"

dbconn = dbhelper.DBHelper()

def refreshDBwithTypeRankXML() -> None:
    """ Recorre el fichero type_ranking_en.xml y añade cada typerank al la tabla tranking de la BD"""
    # Obtenemos el nombre sel fichero con el directorio y el idioma
    file = BASE + str(LANG) + ".xml"
    tree = ET.ElementTree(file=file)

    # Obtenemos la raiz
    root = tree.getroot()

    try:
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

            dbconn.add_ranking_types(dict_typerank_i["id"], dict_typerank_i["name"], dict_typerank_i["description"])
    except Exception as e:
        print(e)
    finally:
        if dbconn.conn:
            dbconn.close()
            print("MySQL cursor is closed")