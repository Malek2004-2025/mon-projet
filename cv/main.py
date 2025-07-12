from cv.lecture_pdf import est_pdf_scanné, extraire_texte_pdf_scanné, extraire_blocs_avec_positions
from cv.seg import ajouter_embedding, filtre_blocs, propager_categorie_dpuis_titres, classifier_blocs_sans_categorie, construire_json_structuré
import json


def pipeline_cv_ats(fichier_pdf):
    if est_pdf_scanné(fichier_pdf):
        print("PDF scanné — OCR en cours...")
        texte = extraire_texte_pdf_scanné(fichier_pdf)
        blocs = [{"texte": t, "page": 1, "x0": 0, "y0": i*20} for i, t in enumerate(texte.split('\n')) if t.strip()]
    else:
        print("PDF textuel détecté.")
        blocs = extraire_blocs_avec_positions(fichier_pdf)
        blocs = [ajouter_embedding(bloc) for bloc in blocs]
        blocs_titres, blocs_contenu = filtre_blocs(blocs)

        # Propagation avant classification pour ne pas écraser catégories détectées par titres
        blocs_contenu = propager_categorie_dpuis_titres(blocs_titres, blocs_contenu, distance_seuil=100)

        # Ajouter classification SVM pour les blocs sans catégorie
        blocs_contenu = classifier_blocs_sans_categorie(blocs_contenu)
        
        blocs = blocs_titres + blocs_contenu
      
        # Construire JSON structuré
        json_structuré = construire_json_structuré(blocs)

        print(json.dumps(json_structuré, indent=2, ensure_ascii=False))

        return json_structuré

def generer_json(fichier_json,json_structuré):
    if json_structuré:
        with open(fichier_json, "w", encoding="utf-8") as f:
            json.dump(json_structuré, f, ensure_ascii=False, indent=4)
    
    print(f"Fichier JSON '{fichier_json}' généré avec succès.")
    
   




if __name__ == "__main__":
    json_structuré = pipeline_cv_ats("exemples/mcv.pdf")
    generer_json("cv.json",json_structuré)
    
        
    
    
    