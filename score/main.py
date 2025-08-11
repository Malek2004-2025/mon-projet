from .extraiire import extraire_listes_cv, extraire_listes_offre, open_json
from .compare import comparer_cv_et_offre, calcul_score_global
from pprint import pprint

def generer_rapport(cv_json, offre_json):
    cv_std = extraire_listes_cv(cv_json)
    offre_std = extraire_listes_offre(offre_json)

    compare_result = comparer_cv_et_offre(cv_std, offre_std)
    scores = calcul_score_global(
        compare_result["scores"],
        poids_personnalise=None,
        valeurs_cv=cv_std,
        valeurs_offre=offre_std
    )
    
    rapport = {
        "details": compare_result["scores"],
        "score_original": scores["score_original"],
        "score_finale": scores["score_finale"]
    }
    return rapport




if __name__ == "__main__" :
    cv_json = open_json("cv.json")
    offre_json = open_json("offre.json")
    rapport = generer_rapport(cv_json, offre_json)
    pprint(rapport)


