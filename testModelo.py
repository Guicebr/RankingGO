from Modelo.TypeRankTranslator import TypeRankTranslator
from Modelo.LevelsTranslator import LevelsTranslator
from Modelo.LangTranslator import LangTranslator

# test TypeRankTranslator
# tr = TypeRankTranslator()
# print(tr.getlist_TypeRank("en"), "\n -> ['Totalxp', 'Collector', 'Jogger',..]")
# print(tr.translate_DBidtoHUMAN("en", "9"), "-> Scientist")
# print(tr.translate_DBtoHUMAN("es", "scientist"), "-> Científico")

# test LevelsTranslator
# lvtrasnlator = LevelsTranslator()
# print(lvtrasnlator.getLV_EXP(79825637), "-> [[44,26325637],[45,200...],...]")

# Test LangTranslator
langtranslator = LangTranslator()
# text = langtranslator.getWordLang('START_STRING', 'pollo')
text = langtranslator.getWordLang('HELP_PRIVATE_STRING', "en")
print(langtranslator.xml_translate_dict.keys())