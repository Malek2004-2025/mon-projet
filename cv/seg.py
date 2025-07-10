from sentence_transformers import SentenceTransformer
from lecture_pdf import extraire_blocs_avec_positions
import joblib
import json

embedding_model, svm_model = joblib.load("classif_cvvv.joblib")
model = embedding_model

def ajouter_embedding(bloc):
    bloc["embedding"] = model.encode(bloc["texte"])
    return bloc

def est_titre_bloc(bloc):
    texte = bloc["texte"].strip()
    mots = texte.lower().replace(":","").split()
    mots_cles = {
        "Expérience":["expérience", "expériences", "expérience professionnelle", "expérience pro", 
        "parcours professionnel", "stages", "stage", "emplois", "emploi", 
        "vie professionnelle", "carrière", "expériences professionnelles"],
        "Formation":["formation", "formations", "éducation", "études", "parcours académique", 
        "scolarité", "diplômes", "diplôme", "université", "école", "bac", "baccalauréat"],
        "Compétences techniques":["compétences", "compétence", "compétences techniques", "technologies", 
        "outils", "outils informatiques", "informatique", "langages", "langages informatiques"],
        "Langues":["langues", "langue", "compétences linguistiques", "langues parlées", 
        "niveau linguistique"],
        "Soft Skills":["soft skills", "compétences personnelles", "savoir-être", "qualités", 
        "aptitudes", "compétences relationnelles", "compétences comportementales"],
        "Informations personnelles":["contact", "coordonnées", "informations personnelles", "informations de contact", 
        "adresse", "email", "e-mail", "numéro", "téléphone", "linkedin", "profil"],
        "Autres":["autres", "divers", "centres d’intérêt", "hobbies", "loisirs", 
        "bénévolat", "associatif", "projets", "certifications", "références", "Intérêts"]
    }

    if len(mots) <= 4:
        for categorie, liste in mots_cles.items():
            if any(m in liste for m in mots):
                bloc["categorie"] = categorie
                return True
    
    # Si tout le texte est en majuscules
    if texte.isupper():
        return True
    
    return False
    
def filtre_blocs(blocs):
    blocs_titres = []
    blocs_contenu = []

    for bloc in blocs:
        if est_titre_bloc(bloc):
            blocs_titres.append(bloc)
        else:
            blocs_contenu.append(bloc)
    return blocs_titres, blocs_contenu

#associe à chaque bloc de contenu la catégorie du titre le plus proche verticalement au-dessus de lui (sur la même page),
def propager_categorie_dpuis_titres(blocs_titres, blocs_contenu, distance_seuil=100):
    for bloc_c in blocs_contenu:
        y_c_h = bloc_c["y0"]
        page_c = bloc_c.get("page", 0)
        titre_plus_proche = None
        distance_ver_min = float("inf")

        for bloc_t in blocs_titres : #il va comparer un bloc avec tout les titres afin de trouver le titre ayant la distance la plus petite en dessus du contenu
            page_t = bloc_t.get("page", 0)
            y_t_b = bloc_t["y1"]
            if page_c == page_t:
                distance = y_c_h - y_t_b #(haut du contenu - bas du titre)
                if 0 < distance < distance_ver_min and distance < distance_seuil:
                    distance_ver_min = distance
                    titre_plus_proche = bloc_t

        if titre_plus_proche is not None and "categorie" in titre_plus_proche: 
            bloc_c["categorie"] = titre_plus_proche["categorie"]
        else:
            bloc_c["categorie"] = "sans_categorie"

    return blocs_contenu 


def classifier_blocs_sans_categorie(blocs):
    for bloc in blocs:
        if bloc.get("categorie") == "sans_categorie":
            vecteur = bloc["embedding"].reshape(1, -1)
            prediction = svm_model.predict(vecteur)[0]
            bloc["categorie"] = prediction
    return blocs



def construire_json_structuré(blocs):
    from collections import defaultdict
    json_result = defaultdict(list)
    mapping = {
        "expérience": "Expérience",
        "formation": "Formation",
        "langues": "Langues",
        "soft skills": "Soft Skills",
        "compétences techniques": "Compétences techniques",
        "informations personnelles": "Informations personnelles",
        "autres": "Autres",
        "a propos de moi": "Soft Skills"
    }
    for bloc in blocs:
        cat = bloc.get("categorie", "Autres")
        texte = bloc.get("texte", "").strip()
        # Convertir vers un nom propre
        nom_final = mapping.get(cat, cat)
        json_result[nom_final].append(texte)

    return json_result





