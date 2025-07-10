import csv

def generer_corpus_csv(nom_fichier="corpus.csv"):
    data = [
    ("Jean Dupont", "Informations personnelles"),
    ("Adresse : 15 rue des Lilas, 75020 Paris", "Informations personnelles"),
    ("Téléphone : +33 6 12 34 56 78", "Informations personnelles"),
    ("Email : jean.dupont@email.com", "Informations personnelles"),
    ("LinkedIn : linkedin.com/in/jeandupont", "Informations personnelles"),

    ("Développeur Python – Safran, Paris", "Expérience"),
    ("Janvier 2023 – Juin 2024", "Expérience"),
    ("Développement de scripts RPA pour automatiser l'extraction de données techniques.", "Expérience"),
    ("Utilisation de Python, PyMuPDF, Tesseract OCR et Flask pour construire une API interne.", "Expérience"),
    ("Travail en équipe Agile (Scrum) avec 6 développeurs.", "Expérience"),

    ("Stagiaire en systèmes embarqués – Thales, Paris", "Expérience"),
    ("Juillet 2022 – Décembre 2022", "Expérience"),
    ("Réalisation d’un prototype IoT basé sur ESP32.", "Expérience"),
    ("Communication via MQTT et intégration de capteurs (I2C/SPI).", "Expérience"),
    ("Déploiement d'une interface de supervision via Node-RED.", "Expérience"),

    ("Licence Professionnelle en IoT – ISTIC, Université de Carthage", "Formation"),
    ("2022 – 2024", "Formation"),
    ("Projets en systèmes embarqués, réseaux et cybersécurité.", "Formation"),
    ("Réalisation d’un mini-projet : système de contrôle de température avec alerte mail.", "Formation"),
    ("Baccalauréat Scientifique – Lycée Pilote Ariana", "Formation"),
    ("2022 - Mention Bien", "Formation"),

    ("Python, C, C++", "Compétences techniques"),
    ("RPA, OCR, Flask", "Compétences techniques"),
    ("Protocoles : UART, I2C, SPI, MQTT", "Compétences techniques"),
    ("Git, Linux, VS Code", "Compétences techniques"),
    ("Lecture de schémas électroniques", "Compétences techniques"),
    ("Modélisation Proteus / ARES", "Compétences techniques"),
    ("Langages web : HTML, JavaScript (bases)", "Compétences techniques"),

    ("Français : Langue maternelle", "Langues"),
    ("Anglais : B2 – Conversation professionnelle", "Langues"),
    ("Allemand : A2 – Niveau scolaire", "Langues"),

    ("Travail en équipe", "Soft Skills"),
    ("Créativité et autonomie", "Soft Skills"),
    ("Présentation orale fluide", "Soft Skills"),
    ("Participation au Hackathon IoT 2023 (2e place)", "Expérience"),
    ("Titulaire du permis B", "Autres"),
]

    with open(nom_fichier, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["categorie", "texte"])
        writer.writerows(data)
    
if __name__ == "__main__":
    generer_corpus_csv()