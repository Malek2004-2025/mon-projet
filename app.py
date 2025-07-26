from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
import os
import json
from cv.main import pipeline_cv_ats
from score.main import generer_rapport
from cv.lecture_pdf import est_pdf_scanné, extraire_texte_pdf_scanné, extraire_blocs_avec_positions







# Initialiser l'application Flask
app = Flask(__name__)

# Définir dossier d'upload temporaire
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/analyse", methods=["POST"])
def analyser_cv_offre():
    try:
        cv_file = request.files.get("cv_file")
        offre_file = request.files.get("offre_file")

        if not cv_file or not offre_file:
            raise BadRequest("Les fichiers 'cv_file' et 'offre_file' sont requis.")
        
        if not cv_file.filename.lower().endswith(".pdf"):
            raise BadRequest("Le fichier CV doit être un PDF.")
        
        filename_cv = secure_filename(cv_file.filename)
        chemin_cv = os.path.join(app.config["UPLOAD_FOLDER"], filename_cv)
        cv_file.save(chemin_cv)

        # Lecture du PDF et extraction
        cv_json = pipeline_cv_ats(chemin_cv)
        
        try:
            offre_data = json.load(offre_file)
        except json.JSONDecodeError:
            raise BadRequest("Le fichier offre doit être un JSON valide.")
        
        rapport = generer_rapport(cv_json, offre_data)
        return jsonify(rapport)
    
    except BadRequest as e:
        return jsonify({"erreur": str(e)}),400
    except Exception as e:
        return jsonify({"erreur": "Erreur interne du serveur", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
