from extraiire import extraire_listes_cv, extraire_listes_offre, open_json
from compare import comparer_cv_et_offre, calcul_score_global
from pprint import pprint

def generer_rapport(cv_json, offre_json):
    cv_std = extraire_listes_cv(cv_json)
    pprint(cv_std["ecoles"])
    offre_std = extraire_listes_offre(offre_json)
    compare_result = comparer_cv_et_offre(cv_std, offre_std)
    score_glob = calcul_score_global(compare_result["scores"], poids_personnalise=None)
    
    rapport = {
        "score_global": score_glob,
        "details": compare_result["scores"]
    }

    return rapport



if __name__ == "__main__" :
    cv_json = open_json("cv.json")
    offre_json = open_json("offre.json")
    rapport = generer_rapport(cv_json, offre_json)
    pprint(rapport)


