from flask import Flask, request, render_template, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
import os
import json
from cv.main import pipeline_cv_ats
from score.main import generer_rapport
from models import Candidature, Offre, TypeStage, Statut, CompetenceTechnique, CompetenceComportementale, FormationAcademique, PropositionEcole
from extensions import db
from datetime import datetime







# Initialiser l'application Flask
app = Flask(__name__)
app.secret_key = "vraiment-secret"  # Obligatoire pour utiliser flash

# Définir dossier d'upload temporaire
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # évite un warning
db.init_app(app)




# accueil
@app.route("/")
def acceuil():
    return render_template("accueil.html")

# Candidat
@app.route("/candidat")
def candidat():
    return render_template("candidat.html")

# Offre (afficher les offres)
@app.route("/offre")
def afficher_offres():
    offres = Offre.query.all()  # Récupère toutes les offres de la base de données
    return render_template("offres.html", offres=offres)

# postuler
@app.route("/postuler/<int:offre_id>", methods=["GET", "POST"])
def postuler(offre_id):
    offre = Offre.query.get_or_404(offre_id)

    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        message = request.form.get("message")
        date_candidature_str = request.form.get("date_candidature")
        cv_file = request.files.get("cv")

        if not nom or not email or not cv_file:
            return render_template("postuler.html", offre=offre, error="Tous les champs sont requis.")

        if not cv_file.filename.lower().endswith(".pdf"):
            return render_template("postuler.html", offre=offre, error="Le CV doit être au format PDF.")

        filename_cv = secure_filename(cv_file.filename)
        chemin_cv = os.path.join(app.config["UPLOAD_FOLDER"], filename_cv)
        cv_file.save(chemin_cv)

        try:
            cv_json = pipeline_cv_ats(chemin_cv)
            rapport = generer_rapport(cv_json, offre.to_dict())
            score = rapport.get("score_global", 0)
        except Exception as e:
            return render_template("postuler.html", offre=offre, error=f"Erreur d'analyse du CV : {str(e)}")
        try:
            date_candidature = datetime.strptime(date_candidature_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            date_candidature = datetime.utcnow()

        nouvelle_candidature = Candidature(
        offre_id=offre_id,
        nom=nom,
        prenom=prenom,
        email=email,
        message=message,
        date_candidature=date_candidature,  # attention au format, doit être datetime
        cv_filename=filename_cv,
        statut="En attente",
        score=score
        # tu peux aussi ajouter score si ta classe le prévoit
)


        
        db.session.add(nouvelle_candidature)
        db.session.commit()

        return render_template("postuler.html", offre=offre, success="Votre candidature a été envoyée avec succès.")

    return render_template("postuler.html", offre=offre)

# rh
@app.route("/admin", methods=["GET"])
def admin():
    return render_template("admin.html")

# afficher les offres
@app.route("/admin/offres")
def admin_offres():
    offres = Offre.query.all()
    return render_template("admin_offres.html", offres=offres)

# ajouter une offre
@app.route("/admin/offres/ajouter", methods=["POST", "GET"])
def ajouter_offre():
    if request.method == "POST":
        # 1. Récupérer les champs simples
        intituleProjet = request.form.get("intituleProjet")
        descriptionProjet = request.form.get("descriptionProjet")
        risquesProjet = request.form.get("risquesProjet")
        objectifsProjet = request.form.get("objectifsProjet")
        descriptionLivrables = request.form.get("descriptionLivrables")
        effortEstime = request.form.get("effortEstime")
        dureeEstime = int(request.form.get("dureeEstime", 0))
        nombreStagiaires = int(request.form.get("nombreStagiaires", 0))
        reference = request.form.get("reference")

        # Fonction utilitaire pour récupérer ou créer une instance en base
        def get_or_create(model, champ, valeur):
            instance = model.query.filter(getattr(model, champ) == valeur).first()
            if not instance:
                instance = model(**{champ: valeur})
                db.session.add(instance)
                db.session.flush()  # Permet d'avoir l'id avant commit
            return instance

        # 2. Récupérer les listes des champs multiples (texte séparé par virgule)
        competences_technique_text = request.form.get("competencestechnique", "")
        competences_technique_noms = [c.strip() for c in competences_technique_text.split(",") if c.strip()]
        competences_technique = [get_or_create(CompetenceTechnique, "nomExigence", nom) for nom in competences_technique_noms]

        competences_comportementale_text = request.form.get("competencescomportementale", "")
        competences_comportementale_noms = [c.strip() for c in competences_comportementale_text.split(",") if c.strip()]
        competences_comportementale = [get_or_create(CompetenceComportementale, "nomCompetence", nom) for nom in competences_comportementale_noms]

        formation_academique_text = request.form.get("formationacademique", "")
        formation_academique_noms = [c.strip() for c in formation_academique_text.split(",") if c.strip()]
        formations_academiques = [get_or_create(FormationAcademique, "nomFormation", nom) for nom in formation_academique_noms]

        propecole_text = request.form.get("propecole", "")
        propecole_noms = [c.strip() for c in propecole_text.split(",") if c.strip()]
        propositions_ecole = [get_or_create(PropositionEcole, "nomEcole", nom) for nom in propecole_noms]

        # 3. Récupérer le typeStage et le statut (existant ou nouveau)
        type_stage_id = int(request.form.get("typeStage_id", 1))
        type_stage = TypeStage.query.get(type_stage_id)
        if not type_stage:
            type_stage = TypeStage(id=type_stage_id, nomTypeStage="PFE", dureeStage=6)
            db.session.add(type_stage)

        statut = Statut.query.get(1)
        if not statut:
            statut = Statut(id=1, nomStatut="en attente")
            db.session.add(statut)

        # 4. Créer l’offre
        offre = Offre(
            intituleProjet=intituleProjet,
            descriptionProjet=descriptionProjet,
            risquesProjet=risquesProjet,
            objectifsProjet=objectifsProjet,
            descriptionLivrables=descriptionLivrables,
            effortEstime=effortEstime,
            dureeEstime=dureeEstime,
            nombreStagiaires=nombreStagiaires,
            reference=reference,
            nombreStagiairesAffectes=0,
            typeStage=type_stage,
            statut=statut,
            workflowInstance=None
        )

        # 5. Associer les listes récupérées à l’offre
        offre.competencestechnique = competences_technique
        offre.competencescomportementale = competences_comportementale
        offre.formationacademique = formations_academiques
        offre.propecole = propositions_ecole

        # 6. Sauvegarder en base
        db.session.add(offre)
        db.session.commit()

        return redirect(url_for("admin_offres"))

    # En GET, afficher le formulaire avec les types/stats
    types_stages = TypeStage.query.all()
    statuts = Statut.query.all()
    return render_template("admin_ajouter_offre.html", types_stages=types_stages, statuts=statuts)



# modifier une offre
@app.route("/admin/offres/<int:id>/modifier", methods=["GET", "POST"])
def modifier_offre(id):
    offre = Offre.query.get_or_404(id)

    if request.method == "POST":
        # Modifier les champs simples
        offre.intituleProjet = request.form["intituleProjet"]
        offre.descriptionProjet = request.form["descriptionProjet"]
        offre.risquesProjet = request.form["risquesProjet"]
        offre.objectifsProjet = request.form["objectifsProjet"]
        offre.descriptionLivrables = request.form["descriptionLivrables"]
        offre.effortEstime = request.form["effortEstime"]
        offre.dureeEstime = int(request.form["dureeEstime"])
        offre.nombreStagiaires = int(request.form["nombreStagiaires"])
        offre.reference = request.form["reference"]

        # Modifier type_stage (en relation)
        type_stage_id = int(request.form.get("typeStage_id", 1))
        type_stage = TypeStage.query.get(type_stage_id)
        if not type_stage:
            type_stage = TypeStage(id=type_stage_id, nomTypeStage="PFE", dureeStage="6")
            db.session.add(type_stage)
        offre.type_stage = type_stage

        # Modifier statut
        statut_id = int(request.form.get("statut_id", 1))
        statut = Statut.query.get(statut_id)
        if not statut:
            statut = Statut(id=statut_id, nomStatut="en attente")
            db.session.add(statut)
        offre.statut = statut

        # Modifier compétences comportementales
        competences_noms = request.form.getlist('competencescomportementale_nom[]')
        competences_ids = request.form.getlist('competencescomportementale_id[]')

        for comp_id, nom in zip(competences_ids, competences_noms):
            if nom.strip():
                if comp_id:
                    # Mettre à jour compétence existante
                    comp = CompetenceComportementale.query.get(int(comp_id))
                    if comp:
                        comp.nomCompetence = nom.strip()
                else:
                    # Ajouter nouvelle compétence
                    nouvelle_comp = CompetenceComportementale(nomCompetence=nom.strip())
                    db.session.add(nouvelle_comp)
                    offre.competencescomportementale.append(nouvelle_comp)

        db.session.commit()
        return redirect(url_for("admin_offres"))

    return render_template("admin_modifier_offre.html", offre=offre)


# supprimer une offre
@app.route("/admin/offres/<int:id>/supprimer")
def supprimer_offre(id):
    offre = Offre.query.get_or_404(id)
    db.session.delete(offre)
    db.session.commit()
    return redirect(url_for("admin_offres"))


# Voir les candidatures d’une offre
@app.route("/admin/offres/<int:id>/candidatures")
def voir_candidatures_par_offre(id):
    offre = Offre.query.get_or_404(id)

    tri = request.args.get('tri')

    # Récupérer les candidatures liées
    candidatures_pour_offre = offre.candidatures  

     # Appliquer le tri selon paramètre
    if tri == 'score_desc':
        candidatures = sorted(candidatures_pour_offre, key=lambda c: c.score or 0, reverse=True)
    elif tri == 'score_asc':
        candidatures = sorted(candidatures_pour_offre, key=lambda c: c.score or 0)
    elif tri == 'date_desc':
        candidatures = sorted(candidatures_pour_offre, key=lambda c: c.date_candidature or datetime.min, reverse=True)
    elif tri == 'date_asc':
        candidatures = sorted(candidatures_pour_offre, key=lambda c: c.date_candidature or datetime.min)
    elif tri == 'statut':
        ordre_statuts = {'Acceptée': 1, 'En attente': 2, 'Refusée': 3}
        candidatures = sorted(candidatures_pour_offre, key=lambda c: ordre_statuts.get(c.statut, 99))

    return render_template("admin_candidatures.html", candidatures=candidatures_pour_offre, offre=offre)

# telecharger cv 
@app.route("/admin/candidature/<int:candidature_id>/telecharger_cv")
def telecharger_cv(candidature_id):
    candidature = Candidature.query.get_or_404(candidature_id)
    filename_cv = candidature.cv_filename

    if not filename_cv:
        return "Aucun CV pour cette candidature", 404
    
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename_cv, as_attachment=True)


# modifier statut 
@app.route('/admin/candidature/<int:candidature_id>/modifier_statut', methods=["GET", "POST"])
def modifier_statut_candidature(candidature_id):
    candidature = Candidature.query.get_or_404(candidature_id)

    if request.method == 'POST':
        nouveau_statut = request.form.get('statut')
        if nouveau_statut not in ['En attente', 'Acceptée', 'Refusée']:
            flash('Statut invalide.', 'danger')
            return redirect(url_for('modifier_statut_candidature', candidature_id=candidature_id))

        candidature.statut = nouveau_statut
        db.session.commit()
        flash('Statut mis à jour avec succès.', 'success')
        return redirect(url_for('voir_candidatures_par_offre', id=candidature.offre_id))

    statuts_possibles = ['En attente', 'Acceptée', 'Refusée']
    return render_template('modifier_statut.html', candidature=candidature, statuts=statuts_possibles)


# supprimer candidature 
@app.route('/admin/candidature/<int:candidature_id>/supprimer', methods=["POST", "GET"])
def supprimer_candidature(candidature_id):
    candidature = Candidature.query.get_or_404(candidature_id)
    offre_id = candidature.offre_id

    db.session.delete(candidature)
    db.session.commit()

    flash('Candidature supprimée avec succès.', 'success')
    return redirect(url_for('voir_candidatures_par_offre', id=offre_id))

    
with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True)

    