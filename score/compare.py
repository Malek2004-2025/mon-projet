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

def compare_listes(liste_cv, liste_offre, mode="strict", seuil_fuzzy=80):
    # Normalisation via synonymes
    liste_cv_norm = normaliser(liste_cv, synonymes)
    liste_offre_norm = normaliser(liste_offre, synonymes)

    matches, manquants = [], []

    for exigence, orig in zip(liste_offre_norm, liste_offre):
        trouve = False
        for valeur_cv in liste_cv_norm:
            if mode == "strict" and exigence == valeur_cv:
                trouve = True
                break
            elif mode == "fuzzy":
                if fuzz.partial_ratio(exigence, valeur_cv) >= seuil_fuzzy:
                    trouve = True
                    originale = orig
                    break
        if trouve:
            matches.append(orig)
        else:
            manquants.append(orig)

    score = (len(matches) / len(liste_offre_norm)) * 100 if liste_offre_norm else 0
    return {
        "score": round(score, 1),
        "matches": matches,
        "manquants": manquants
    }
                

def comparer_cv_et_offre(cv_std, offre_std) : #standardisé
    modes = {
        "competences": ("fuzzy", 80), #mode + seuil
        "soft_skills": ("fuzzy", 80),
        "formations": ("fuzzy", 70),
        "ecoles": ("fuzzy", 85)
    }
    resultats = {}

    for categorie in ["competences", "soft_skills", "formations", "ecoles"]:
        #On récupère les listes de mots dans le CV et l’offre pour chaque catégorie
        valeurs_cv = cv_std.get(categorie, [])
        valeurs_offre = offre_std.get(categorie, [])
        mode, seuil =modes[categorie] #On récupère le mode (strict ou fuzzy) et le seuil à appliquer
        resultat = compare_listes(
            liste_cv=valeurs_cv,
            liste_offre=valeurs_offre,
            mode=mode,
            seuil_fuzzy=seuil
        )
        
        resultat_final = resultat.copy()

        resultats[categorie] = resultat_final
    return {
        "scores": resultats
    }

def calculer_bonus_frequence(valeurs_cv, liste_offre, score_categorie):
    # Étape 1 : normalisation des deux listes
    valeurs_cv_norm = normaliser(valeurs_cv, synonymes)
    liste_offre_norm = normaliser(liste_offre, synonymes)

    # Étape 2 : compteur de la fréquence des compétences normalisées du CV
    compteur = Counter(valeurs_cv_norm)

    # Étape 3 : calcul des répétitions pour chaque compétence présente à la fois dans le CV et l’offre
    total_repetitions = 0
    for exigence in liste_offre_norm:
        freq = compteur.get(exigence, 0)
        if freq > 1:
            total_repetitions += (freq - 1)  # on ignore la première apparition

    # Étape 4 : calcul du bonus
    bonus_brut = total_repetitions * 0.5
    bonus_max = 0.2 * score_categorie
    bonus = min(bonus_brut, bonus_max)

    # Étape 5 : retourner aussi les fréquences utiles uniquement
    frequences_utiles = {exig : compteur[exig] for exig in liste_offre_norm if compteur[exig] > 0}

    return round(bonus, 2), frequences_utiles


def calcul_score_global(resultats_par_categorie, poids_personnalise=None, valeurs_cv=None):
    poids = poids_personnalise or {
       "competences": 0.5,
        "soft_skills": 0.2,
        "formations": 0.2,
        "ecoles": 0.1
    }
    total = 0.0
    for cat, infos in resultats_par_categorie.items():
        score_cat = infos.get("score", 0)
        poids_cat = poids.get(cat, 0)
        total += score_cat * poids_cat

    # Bonus uniquement pour compétences techniques
    if valeurs_cv is not None:
        scores = resultats_par_categorie.get("competences", {})
        score_comp = scores.get("score", 0)

        liste_cv = valeurs_cv.get("competences", [])
        liste_offre = valeurs_cv.get("offre_competences", [])

        bonus, frequences = calculer_bonus_frequence(liste_cv, liste_offre, score_comp)
        total += bonus
        resultats_par_categorie["competences"]["frequences"] = frequences


    return round(total, 1)

