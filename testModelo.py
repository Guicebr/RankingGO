from Modelo.TypeRankTranslator import TypeRankTranslator
from Modelo.LevelsTranslator import LevelsTranslator

# test TypeRankTranslator
# tr = TypeRankTranslator()
# print(tr.getlist_TypeRank("en"), "\n -> ['Totalxp', 'Collector', 'Jogger',..]")
# print(tr.translate_DBidtoHUMAN("en", "9"), "-> Scientist")
# print(tr.translate_DBtoHUMAN("es", "scientist"), "-> Científico")

# test LevelsTranslator
lvtrasnlator = LevelsTranslator()
print(lvtrasnlator.getLV_EXP(79825637), "-> [[44,26325637],[45,200...],...]")
