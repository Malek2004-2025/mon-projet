import os
from flask import Flask, request, jsonify
from cv.main import pipeline_cv_ats, generer_json  
from score.extraiire import extraire_listes_offre, extraire_listes_cv, open_json
from score.compare import  comparer_cv_et_offre, calcul_score_global
from werkzeug.exceptions import RequestEntityTooLarge

 
app = Flask(__name__)# instance de l’application Flask.(classe Flask)
app.config['UPLOAD_FOLDER'] = 'uploads' # dossier temporaire pour PDF
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
# Créer automatiquement le dossier 'uploads' s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.errorhandler(RequestEntityTooLarge)
def handle_413(e):
    return jsonify({
        "success": False,
        "error": "Fichier trop volumineux. La limite est de 200 Mo."
    }), 413


@app.route('/')
def home():
    return "Bienvenue sur l'API d'analyse de CV "


@app.route('/analyser_cv', methods=['POST'])
def analyser_cv():
    # Vérifier présence du fichier dans la requête
    if 'file' not in request.files: #request est l’objet Flask qui contient toutes les données de la requête HTTP envoyée par le client.
        return jsonify({"success": False, "error": "Aucun fichier envoyé"}), 400

    file = request.files['file']
    taille = len(file.read())
    file.seek(0)
    print(f"Fichier reçu : {file.filename}, taille = {taille} octets")


    # Vérifier que le fichier a un nom
    if file.filename == '':
        return jsonify({"success": False, "error": "Nom du fichier vide"}), 400
    
    # Vérifier que c’est bien un PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"success": False, "error": "Le fichier doit être un PDF"}), 400

    # Sauvegarder le fichier sur le disque temporairement
    chemin_fichier = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(chemin_fichier)

    try:
        # Étape 1 : Analyse du CV PDF avec ton pipeline
        json_structuré = pipeline_cv_ats(chemin_fichier)
        if not json_structuré:
            return jsonify({"success": False, "error": "Analyse du CV échouée"}), 500

        # Étape 2 : Charger l'offre stockée côté serveur
        offre_json = open_json("exemples/offre.json")

        # Étape 3 : Comparaison CV ↔ Offre
        cv_std = extraire_listes_cv(json_structuré)
        offre_std = extraire_listes_offre(offre_json)
        comparaison = comparer_cv_et_offre(cv_std, offre_std)

        # Étape 4 : Calcul score global
        score_global = calcul_score_global(comparaison["scores"])

        # Résultat final
        return jsonify({
            "success": True,
            "score_global": score_global,
            "details": comparaison["scores"]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur interne : {str(e)}"}), 500



    

    






if __name__ == "__main__":
    app.run(debug=True) #lance le serveur Flask en mode debug(pour les erreurs)