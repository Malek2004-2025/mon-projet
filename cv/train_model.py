#from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import joblib
import csv
from sentence_transformers import SentenceTransformer



def charger_depuis_csv(fichier_csv):
    corpus = []
    labels = []
    with open(fichier_csv, encoding='utf-8') as f:
        lecteur = csv.reader(f, delimiter=';')  # change delimiter si besoin
        for ligne in lecteur:
            if len(ligne) < 2:
                continue  # ignorer les lignes mal formées
            texte, label = ligne[0].strip(), ligne[1].strip()
            if texte and label:
                corpus.append(texte)
                labels.append(label)
    return corpus, labels


corpus, labels = charger_depuis_csv("corpus_cv.csv")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
corpus_embeddings = model.encode(corpus)
#vectorizer = TfidfVectorizer() # On crée un "traducteur" de texte vers chiffres.
clf = LinearSVC() # crées un classifieur (= un petit "cerveau") basé sur une méthode appelée SVM linéaire.(vide)
#X = vectorizer.fit_transform(corpus) #  transforme une liste de textes (corpus) en vecteurs numériques
clf.fit(corpus_embeddings, labels) # entraîne le modèle SVM (clf) à reconnaître les catégories de chaque texte.
joblib.dump((model, clf), "classif_cvvv.joblib") # sauvegarder le modèle entraîné 
