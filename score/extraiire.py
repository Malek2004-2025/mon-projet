import os
import re
import json
import joblib
from sentence_transformers import SentenceTransformer

# Charger le modèle sauvegardé (encodeur + classifieur)
BASE_DIR = os.path.dirname(__file__)  # le dossier où se trouve extraiire.py
model_path = os.path.join(BASE_DIR, "classif_softskills.joblib")
model_soft, clf_soft = joblib.load(model_path)
                                   
def open_json(nom_fichier_json):
    with open(nom_fichier_json, "r", encoding="utf-8") as f:
        donnees = json.load(f)
    return donnees

soft_keywords = [
    # Communication et relations interpersonnelles
    "communication", "écoute", "aisance relationnelle", "relationnel", "assertivité", "négociation",
    "diplomatie", "présentation orale", "capacité à convaincre", "clarté d’expression", "feedback constructif",

    #  Esprit d’équipe & collaboration
    "travail en équipe", "esprit d'équipe", "coopération", "collaboration", "partage", "entraide",
    "intelligence collective", "respect des autres", "facilité à travailler en groupe",

    #  Leadership & management
    "leadership", "prise d’initiative", "gestion de projet", "motivation", "faculté à motiver", 
    "sens des responsabilités", "gestion des conflits", "délégation", "supervision", "encadrement",
    "prise de décision", "gestion d’équipe",

    #  Adaptabilité & autonomie
    "autonomie", "adaptabilité", "polyvalent", "polyvalence", "flexibilité", "capacité à s’adapter",
    "gestion du changement", "résilience", "proactivité", "initiative", "réactivité",

    #  Rigueur & organisation
    "rigueur", "rigoureux", "organisé", "structure", "gestion du temps", "priorisation",
    "ponctualité", "minutie", "respect des délais", "suivi", "anticipation",

    #  Résolution de problèmes & pensée critique
    "résolution", "résolution de problèmes", "analyse", "esprit critique", "esprit d’analyse",
    "problèmes complexes", "logique", "pragmatisme", "prise de recul", "jugement", "capacité de synthèse",

    #  Créativité & innovation
    "créatif", "créativité", "innovation", "pensée originale", "curiosité", "imagination",
    "esprit d’initiative", "esprit entrepreneurial", "vision",

    #  Méthodologies & outils collaboratifs
    "scrum", "agile", "kanban", "design thinking", "lean", "méthodes agiles",
    "gestion agile", "sprint planning", "daily meeting", "rétrospective"
    ]
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
            if any (mot in cles.lower() or mot in texte for mot in ["compétences techniques","logiciels"]):# ajouter dans le liste si on change le mot dans .csv ou mots_cles
                result["competences"].append(texte)
            elif any(mot in cles.lower() or mot in texte for mot in ["soft", "comport", "relation", "qualite","profil"]):
                result["soft_skills"].append(texte)
            elif any(mot in cles.lower() or mot in texte for mot in ["formation", "etude", "education", "diplome"]):
                result["formations"].append(texte)
                if any(m in texte for m in ["ecole", "univ", "iset", "institut", "esprit", "polytechnique"]):
                    result["ecoles"].append(texte)
                    extraire_entre_parenth(texte, "ecoles", result)
            elif any(mot in cles.lower() for mot in ["formation", "ecole", "institut", "univ"]) and \
                any(mot in texte for mot in ["ecole", "univ", "iset", "institut","polytechnique"]):
                result["ecoles"].append(texte)

    # soft skills:
    # Construire un texte complet du CV pour chercher les soft skills globalement
    texte_complet = " ".join(" ".join(v) if isinstance(v, list) else (v if isinstance(v, str) else "") for v in cv_structuré.values()).lower()
    # Extraction des soft skills depuis tout le texte
    result["soft_skills"].extend(extraire_soft_skills_depuis_texte_model(texte_complet))
    result["soft_skills"] = list(set(result["soft_skills"]))

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

# Obtenir le chemin absolu du fichier actuel (extraiire.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construire le chemin vers le fichier joblib
MODEL_PATH = os.path.join(BASE_DIR, "classif_softskills.joblib")
# Charger le modèle
model_soft, clf_soft = joblib.load(MODEL_PATH)

def est_phrase_valide(phrase):
    phrase = phrase.strip().lower()

    if not phrase or len(phrase.split()) < 3:
        return False
    
    # Email
    if re.search(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b", phrase):
        return False
    
    # Numéro de téléphone (international ou local)
    if re.search(r"(\+?\d[\d\s\-]{6,})", phrase):
        return False
    
    # URLs ou usernames (github, linkedin, etc.)
    if re.search(r"(github|linkedin|http|www\.|@\w+)", phrase):
        return False
    
    # Phrase avec trop de chiffres / symboles
    if sum(c.isdigit() for c in phrase) > len(phrase) * 0.4:
        return False
    
    # Phrase avec peu de lettres (souvent du bruit technique)
    if sum(c.isalpha() for c in phrase) < 5:
        return False
    
    return True

def extraire_soft_skills_depuis_texte_model(texte, seuil=0.3, afficher_rang=True):
    soft_skills = set()
    phrases = re.split(r'[.!?;\n]\s*', texte.lower())

    for phrase in phrases:
        phrase = phrase.strip()
        if not phrase or not est_phrase_valide(phrase):
            continue

        # Encodage de la phrase
        emb = model_soft.encode([phrase])

        # Obtenir les probabilités de prédiction
        probas = clf_soft.predict_proba(emb)[0]
        classes = clf_soft.classes_
        max_proba = max(probas)
        skill_pred = clf_soft.classes_[probas.argmax()]

        if max_proba >= seuil:
            soft_skills.add(skill_pred)
            print(f" Phrase : {phrase}")
            print(f"→ Skill prédit : {skill_pred} (confiance : {max_proba:.2f})")
        else:
            print(f" Phrase : {phrase}")
            print(f"→ Aucune soft skill retenue (max confiance : {max_proba:.2f})")

        # Affichage du classement des soft skills pour la phrase
        if afficher_rang:
            classement = sorted(zip(classes, probas), key=lambda x: x[1], reverse=True)
            print(" Classement complet :")
            for skill, score in classement:
                print(f"   - {skill:<20} : {score:.4f}")
            print("-" * 50)



    return list(soft_skills)






  

