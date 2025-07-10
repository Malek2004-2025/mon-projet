import re
import json

def open_json(nom_fichier_json):
    with open(nom_fichier_json, "r", encoding="utf-8") as f:
        donnees = json.load(f)
    return donnees

def extraire_listes_cv(cv_structuré):
    result = {
        "competences": [],
        "soft_skills": [],
        "formations": [],
        "ecoles": []
    }

    for cles, val in cv_structuré.items():
        elements_extraits = []

        # cas 1 : liste de chaines simples
        if isinstance(val, list) and all(isinstance(v, str) for v in val):
            elements_extraits = val

        # Cas 2 : liste de dictionnaires
        elif isinstance(val, list) and all(isinstance(v, dict) for v in val):
            for obj in val:
                texte= " ".join(str(v) for v in obj.values())
                elements_extraits.append(texte)
        
        # Cas 3 : une simple chaîne de texte
        elif isinstance(val, str):
            elements_extraits = [val]

        for element in elements_extraits:
            texte = element.strip().lower()
            if any (mot in cles.lower() or mot in texte for mot in ["compétences techniques"]):# ajouter dans le liste si on change le mot dans .csv ou mots_cles
                result["competences"].append(texte)
            elif any(mot in cles.lower() or mot in texte for mot in ["soft", "comport", "relation", "qualite","profil"]):# dans mon cas j'ai que profil
                result["soft_skills"].append(texte)
            elif any(mot in cles.lower() or mot in texte for mot in ["formation", "etude", "education", "diplome"]):
                result["formations"].append(texte)
                if any(m in texte for m in ["ecole", "univ", "iset", "institut", "esprit"]):
                    result["ecoles"].append(texte)
                    extraire_entre_parenth(texte, "ecoles", result)
            elif any(mot in texte for mot in ["ecole", "univ", "iset", "institut"]):
                result["ecoles"].append(texte)
                

    
    for cat in result:
        result[cat] = nettoyer_et_split(result[cat])

    return result

def extraire_listes_offre(offre_json):
    def nettoyer(texte):
        return texte.lower().strip()
    
    competences = [nettoyer(c["nomExigence"]) for c in offre_json.get("competencestechnique", [])]
    soft_skills = [nettoyer(c["nomCompetence"]) for c in offre_json.get("competencescomportementale", [])]
    formations = [nettoyer(f["nomFormation"]) for f in offre_json.get("formationacademique", [])]
    ecoles = [nettoyer(e["nomEcole"]) for e in offre_json.get("propecole", [])]

    return {
        "competences": competences,
        "soft_skills": soft_skills,
        "formations": formations,
        "ecoles": ecoles
    }


def nettoyer_et_split(liste):
    result = []
    for item in liste:
        if not isinstance(item, str):
            # Affiche un message d'erreur clair
            print(f"Warning: élément non-string détecté dans la liste : {item} ({type(item)})")
            # Convertir en chaîne pour éviter l'erreur
            item = str(item)
        # Split par , ; / \n
        morceaux = re.split(r'[,;/\n]', item)
        # Nettoyage de chaque morceau
        morceaux_nettoyes = [m.strip().lower() for m in morceaux if m.strip()]
        result.extend(morceaux_nettoyes)
    return list(set(result))  # Supprime les doublons

def extraire_entre_parenth(texte, cles, result):
    sigle_match = re.search(r'\(([^)]+)\)', texte)
    if sigle_match:
        sigle = sigle_match.group(1).strip().lower()
        if sigle and sigle.isalpha():
            result[cles].append(sigle)