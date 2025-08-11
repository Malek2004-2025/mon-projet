from fuzzywuzzy import fuzz
from collections import Counter
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
syn_path = os.path.join(BASE_DIR, "synonymes.json")

with open(syn_path, "r", encoding="utf-8") as f:

    synonymes = json.load(f)

# Fonction de normalisation ( remplace certains mots dans une liste (liste) par leur équivalent plus "standard")
def normaliser(liste, dic):
    resultat = []
    for mot in liste:
        mot_norm = mot.lower().strip()
        trouve = False
        for mot_prin, synonymes in dic.items():
            # Vérifie si le mot est égal au mot principal ou à un synonyme
            if mot_norm == mot_prin.lower().strip() or mot_norm in [s.lower().strip() for s in synonymes]:
                resultat.append(mot_prin.lower().strip())
                trouve = True
                break
        if not trouve:  # si on n’a rien trouvé, on garde le mot tel quel
            resultat.append(mot_norm)
    return resultat

def calcul_bonus_frequence(freq, bonus_par_occurrence=2):
    if freq > 1:
        return (freq -1) * bonus_par_occurrence
    else:
        return 0

def compare_listes(liste_cv, liste_offre, seuil_fuzzy=80):
    liste_cv_norm = normaliser(liste_cv, synonymes)
    liste_offre_norm = normaliser(liste_offre, synonymes)

    compteur = Counter(liste_cv_norm)

    matches, manquants = [], []
    frequences_utiles = {}  

    score_brut = 0
    score_max = len(liste_offre_norm)*100

    for exigence, orig in zip(liste_offre_norm, liste_offre):
        trouve = False
        for valeur_cv in liste_cv_norm:
            if fuzz.partial_ratio(exigence, valeur_cv) >= seuil_fuzzy:
                trouve = True
                break
        if trouve:
            matches.append(orig)
            freq = compteur[exigence]
            frequences_utiles[orig] = freq
            bonus = calcul_bonus_frequence(freq, bonus_par_occurrence=2)
            score_brut += 100 + bonus
        else:
            manquants.append(orig)

    score = (len(matches) / len(liste_offre_norm)) * 100 if liste_offre_norm else 0

    score_avec_bonus = (score_brut / score_max) * 100 if score_max else 0

    return {
    "score_sans_bonus": round(score, 1),
    "score_avec_bonus": round(score_avec_bonus, 1),
    "matches": matches,
    "manquants": manquants,
    "frequences_supp": frequences_utiles
    }


def comparer_cv_et_offre(cv_std, offre_std):
    modes = {
        "competences": ("fuzzy", 80),
        "soft_skills": ("fuzzy", 80),
        "formations": ("fuzzy", 70),
        "ecoles": ("fuzzy", 85)
    }
    resultats = {}

    for categorie in ["competences", "soft_skills", "formations", "ecoles"]:
        valeurs_cv = cv_std.get(categorie, [])
        valeurs_offre = offre_std.get(categorie, [])
        _, seuil = modes[categorie]
        resultat = compare_listes(
            liste_cv=valeurs_cv,
            liste_offre=valeurs_offre,
            seuil_fuzzy=seuil
        )
        resultats[categorie] = resultat
    return {"scores": resultats}


def calcul_score_global(resultats_par_categorie, poids_personnalise=None, valeurs_cv=None, valeurs_offre=None):
    poids = poids_personnalise or {
       "competences": 0.5,
       "soft_skills": 0.2,
       "formations": 0.2,
       "ecoles": 0.1
    }
    score_original = 0.0
    score_finale = 0.0
    
    for cat, infos in resultats_par_categorie.items():
        score_sans_bonus = infos.get("score_sans_bonus", 0)
        score_avec_bonus = infos.get("score_avec_bonus", score_sans_bonus)
        poids_cat = poids.get(cat, 0)

        score_original += poids_cat * score_sans_bonus
        score_finale += poids_cat * score_avec_bonus

       

    return {
        "score_original": round(score_original, 2),
        "score_finale": round(score_finale, 2)
    }

    



def calculer_frequences_utiles(valeurs_cv, liste_offre):
    valeurs_cv_norm = normaliser(valeurs_cv, synonymes)
    liste_offre_norm = normaliser(liste_offre, synonymes)
    compteur = Counter(valeurs_cv_norm)
    return {exig: compteur[exig] for exig in liste_offre_norm if compteur[exig] > 0}
