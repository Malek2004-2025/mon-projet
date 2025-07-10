from fuzzywuzzy import fuzz



def compare_listes(liste_cv: list[str],
                   liste_offre: list[str],
                   mode: str =  "strict",
                   seuil_fuzzy: int = 80
                   ):
    matches = []
    manquants = []

    # Normalisation en minuscules
    liste_cv_lower = [val.lower().strip() for val in liste_cv]

    for exigence in liste_offre:
        trouve = False
        exigence_norm = exigence.lower().strip()
        if mode == "strict":
            # Correspondance directe (égalité exacte)
            trouve = exigence_norm in liste_cv_lower
        elif mode == "fuzzy":
            for valeur_cv in liste_cv_lower:
                similarite = fuzz.partial_ratio(exigence_norm, valeur_cv)
                if similarite >= seuil_fuzzy:
                    trouve = True
                    break # dès qu'on a un match, on arrête
        else:
            raise ValueError(f"Mode de comparaison invalide : {mode}")
        
        if trouve:
            matches.append(exigence)
        else:
            manquants.append(exigence)
    
    score = (len(matches) / len(liste_offre)) * 100 if liste_offre else 0

    return {
        "score": round(score, 1),
        "matches" : matches,
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
        resultats[categorie] = resultat
    
    return {
        "scores": resultats
    }

def calcul_score_global(resultats_par_categorie, poids_personnalise=None):
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

    return round(total, 1)

