import csv
import joblib
from sklearn.utils import shuffle # mélanger aléatoirement des données 
from sklearn.linear_model import LogisticRegression #predire avec proba
from sklearn.metrics import classification_report # évaluer la performance d’un modèle de classification.
from sentence_transformers import SentenceTransformer

#  Fonction pour lire le corpus depuis un fichier CSV
def charger_depuis_csv(fichier_csv):
    corpus = []
    labels = []
    with open(fichier_csv, encoding='utf-8') as f:
        lecteur = csv.reader(f, delimiter=';')  # CSV format: phrase ; soft_skill
        for ligne in lecteur:
            if len(ligne) < 2:
                continue
            texte, label = ligne[0].strip(), ligne[1].strip()
            if texte and label:
                corpus.append(texte)
                labels.append(label)
    return corpus, labels

# Chargement et mélange aléatoire des données
corpus, labels = charger_depuis_csv("softskills_300.csv")
corpus, labels = shuffle(corpus, labels, random_state=42)

# Chargement du modèle d’embedding
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Transformation des phrases en vecteurs (encodage)
corpus_embeddings = model.encode(corpus)

# Classifieur LOGISTIC REGRESSION (remplace LinearSVC)
clf = LogisticRegression(max_iter=1000)

# Entraînement du modèle sur les embeddings
clf.fit(corpus_embeddings, labels)

# Sauvegarde du modèle (embeddings + classifieur)
joblib.dump((model, clf), "classif_softskills.joblib")

# Évaluation rapide
y_pred = clf.predict(corpus_embeddings)
print(classification_report(labels, y_pred))