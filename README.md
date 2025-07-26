# CV Analyzer – Analyse intelligente de CV PDF

Ce projet est une solution intelligente d’analyse de CV au format PDF.  
Il extrait automatiquement les informations clés, identifie les soft skills à l’aide du NLP, et calcule un score de compatibilité avec une offre d’emploi ou de stage.

---

## Objectifs

- Automatiser l’analyse de CV PDF (même scannés)
- Extraire les sections clés : informations personnelles, expériences, formations, compétences
- Détecter les **soft skills implicites** via des modèles NLP
- Comparer le CV à une **offre d’emploi** pour générer un score de matching
- Fournir un **rapport JSON structuré**
- Exposer le système via une **API Flask**

---

## Fonctionnalités principales
- Prise en charge des CV texte et scannés (OCR avec Tesseract)
- Extraction intelligente des blocs de texte avec positions
- Détection automatique des soft skills via classification NLP
- Matching entre CV et offre (techniques, écoles, soft skills…)
- Génération d’un score global de compatibilité
- Export en JSON
- API REST via Flask pour intégration dans d’autres systèmes

                           --------------------------------------------------------------------------------

## (app.py) API Flask – Analyse CV vs Offre

Cette API permet d’analyser un **CV au format PDF** et de le comparer avec une **offre d’emploi en JSON**, pour générer un rapport de compatibilité.

### Fonctionnalités
- Upload d’un **CV (PDF)** et d’une **offre (JSON)**.
- Extraction des informations du CV (via `pipeline_cv_ats`).
- Comparaison avec l’offre (via `generer_rapport`).
- Retourne un **rapport complet au format JSON**.

### Structure liée
- **Imports clés** :
  - `pipeline_cv_ats` → Analyse du CV
  - `generer_rapport` → Comparaison avec l’offre
- **Dossier `uploads`** → stockage temporaire des fichiers.

### Endpoint disponible
### `POST /analyse`
- **Description** : Analyse un CV PDF et le compare à une offre JSON.
- **Content-Type** : `multipart/form-data`
- **Paramètres** :
  - `cv_file` : CV au format PDF (obligatoire).
  - `offre_file` : Offre au format JSON (obligatoire).

### Réponses
- **200 OK** → Retourne le rapport JSON.
- **400 Bad Request** → Erreur côté client (fichier manquant ou mauvais format).
- **500 Internal Server Error** → Erreur interne serveur.

### Lancer le serveur
python app.py

### L’API sera disponible sur 
http://127.0.0.1:5000/analyse

                           --------------------------------------------------------------------------------

## (CV) Module : `CV/lecture_pdf.py`

Ce module gère **l’analyse des fichiers PDF** (CV) et l’extraction du texte, même si le PDF est **scanné** (image).  
Il utilise **PyMuPDF**, **Pytesseract** et **Pillow**.

---

### Fonctionnalités
- Détection si un PDF est **scanné** ou **textuel**.
- Extraction du texte via **OCR** pour les PDF scannés.
- Extraction des **blocs de texte avec positions** pour préserver la structure.

---

### Fonctions principales

#### **1. `est_pdf_scanné(fichier_pdf)`**
Vérifie si un PDF contient du texte ou seulement des images.
- **Retourne :**
  - `False` → PDF textuel.
  - `True` → PDF scanné.

---

#### **2. `ocr_depuis_image(image_bytes)`**
Convertit une image extraite d’un PDF en texte via **OCR** (`pytesseract`).

---

#### **3. `extraire_texte_pdf_scanné(fichier_pdf)`**
Parcourt chaque page du PDF, récupère les images et applique l’OCR pour extraire le texte.

---

#### **4. `extraire_blocs_avec_positions(fichier_pdf)`**
Extrait les **blocs de texte** (coordonnées + texte) pour garder la structure originale du CV.

---

### Librairies utilisées
- `fitz` (PyMuPDF) → lecture des PDF.
- `pytesseract` → reconnaissance de texte (OCR).
- `PIL` → manipulation d’images.
- `io` → gestion des flux binaires.

---

### Rôle dans le pipeline
- Si le CV est textuel → extraction directe avec `get_text()`.
- Si scanné → `extraire_texte_pdf_scanné()` avec OCR.
- Pour segmentation → `extraire_blocs_avec_positions()` pour les blocs triés.

---

## (CV) Module : `CV/seg.py`

Ce module s’occupe de la **segmentation et classification des blocs de texte** extraits du CV.  
Il permet d’identifier les **titres de sections** (Expérience, Formation, Compétences, etc.) et d’associer chaque bloc de contenu à une catégorie.

---

### Fonctionnalités principales

- Charger les modèles **embedding** et **SVM** (`classif_cv.joblib`) pour la classification.
- Détecter si un bloc de texte est un **titre de section** grâce à une liste de mots-clés.
- Séparer les blocs en **titres** et **contenus**.
- Découper les blocs multilignes en plusieurs blocs simples.
- Associer à chaque bloc de contenu la catégorie du titre verticalement le plus proche au-dessus.
- Classifier les blocs non catégorisés avec le modèle SVM basé sur l’**embedding**.
- Construire un JSON structuré regroupant les contenus par catégorie.

---

### Description des fonctions

#### `ajouter_embedding(bloc)`
- Calcule et ajoute un vecteur d’**embedding** au bloc à partir de son texte.

#### `est_titre_bloc(bloc)`
- Détermine si un bloc est un titre de section en comparant son texte à une liste de mots-clés.  
- Retourne `True` si c’est un titre, sinon `False`.

#### `filtre_blocs(blocs)`
- Sépare la liste des blocs en deux listes :  
  - `blocs_titres` : blocs identifiés comme titres.  
  - `blocs_contenu` : blocs de contenu.

#### `decouper_blocs_multilignes(bloc)`
- Divise un bloc contenant plusieurs lignes en plusieurs blocs, un par ligne, en gardant la position et la page.

#### `propager_categorie_dpuis_titres(blocs_titres, blocs_contenu, distance_seuil=50)`
- Associe à chaque bloc de contenu la catégorie du titre le plus proche verticalement (au-dessus, sur la même page) dans une distance donnée.

#### `classifier_blocs_sans_categorie(blocs)`
- Pour les blocs dont la catégorie est "sans_categorie", utilise un modèle SVM pour prédire leur catégorie à partir de leur embedding.

#### `construire_json_structuré(blocs)`
- Agrège les blocs en un dictionnaire JSON où chaque clé est une catégorie (ex: Expérience, Formation, Langues) et chaque valeur est la liste des textes correspondants.

---

### Bibliothèques et fichiers utilisés
- `joblib` pour charger les modèles pré-entraînés.
- `re` pour expressions régulières.
- Fichier `classif_cv.joblib` contenant les modèles embedding et SVM.

---

### Rôle dans le pipeline
- Après extraction des blocs, segmentation en titres/contenus.
- Classification automatique ou manuelle des blocs.
- Construction d’une structure JSON lisible pour la suite du traitement.

---

## (CV) Module : `CV/main.py`

Ce module orchestre l’ensemble du **pipeline d’analyse du CV**.  
Il combine les fonctions d’extraction du texte (texte direct ou OCR), la segmentation, la classification, et la génération d’une structure JSON finale.

---

### Fonctionnalités principales

#### `pipeline_cv_ats(fichier_pdf)`
- Point d’entrée principal pour analyser un CV PDF.  
- Détecte si le PDF est scanné ou textuel via `est_pdf_scanné()`.  
- Si scanné → applique l’OCR (`extraire_texte_pdf_scanné`) et crée des blocs ligne par ligne.  
- Si textuel → extrait les blocs avec positions (`extraire_blocs_avec_positions`) et découpe les blocs multilignes en blocs simples.  
- Ajoute un **embedding** à chaque bloc (via `ajouter_embedding`).  
- Sépare les blocs en titres et contenu (`filtre_blocs`).  
- Associe les catégories des titres aux blocs de contenu proches (`propager_categorie_dpuis_titres`).  
- Classifie les blocs non catégorisés avec un modèle SVM (`classifier_blocs_sans_categorie`).  
- Construit un JSON structuré par catégories (`construire_json_structuré`).  
- Affiche et retourne ce JSON.

---

#### `generer_json(fichier_json, json_structuré)`
- Sauvegarde la structure JSON résultante dans un fichier `.json` pour exploitation ultérieure.  
- Affiche un message de confirmation.

---

### Exemple d’utilisation
Dans la partie `if __name__ == "__main__":`, on teste le pipeline sur un CV exemple `martin.pdf` et on génère un fichier `cv.json`.

---

### Rôle dans le pipeline global
- Point de convergence entre extraction brute (`lecture_pdf.py`) et segmentation/classification (`seg.py`).  
- Produit la sortie finale structurée qui sera utilisée pour la comparaison avec une offre dans la partie `score`.

---

### Librairies/fichiers utilisés
- `lecture_pdf.py` pour extraction texte et blocs.  
- `seg.py` pour classification et structuration.  
- `json` pour sauvegarde.

---

## (score)Module : `score/extraire.py`

Ce module gère l’**extraction et la normalisation des informations** provenant :
- du **CV structuré** (sortie du module `CV`),
- de l’**offre d’emploi** (fichier JSON).

Il prépare ces données pour la comparaison et le calcul de score dans le module `compare.py`.

---

### **Objectif**
- Extraire **compétences techniques**, **soft skills**, **formations**, **écoles** depuis :
  - Le CV structuré (analyse textuelle + modèles ML pour soft skills).
  - L’offre d’emploi (lecture directe du JSON).

- Utiliser un **modèle pré-entraîné** (embedding + classifieur SVM) pour identifier les soft skills implicites dans les phrases du CV.

---

### **Fonctionnalités principales**
- **Lecture d’un fichier JSON** d’offre (`open_json`).
- **Extraction des listes normalisées** :
  - `extraire_listes_cv()` → depuis le CV structuré.
  - `extraire_listes_offre()` → depuis l’offre d’emploi.
- **Détection intelligente des soft skills** :
  - Basée sur un modèle `classif_softskills.joblib` (SentenceTransformer + SVM).
- Nettoyage et **segmentation des textes** pour supprimer les doublons et normaliser.

---

### **Description des fonctions clés**

#### `open_json(nom_fichier_json)`
- Charge un fichier JSON et renvoie son contenu en dictionnaire.

#### `extraire_listes_cv(cv_structuré)`
- Analyse le dictionnaire structuré issu du CV.
- Identifie et sépare :
  - Compétences techniques.
  - Soft skills (via **keywords** + **modèle ML**).
  - Formations.
  - Écoles (détectées dans le texte ou entre parenthèses).
- Retourne un dictionnaire normalisé :
```json
{
  "competences": [...],
  "soft_skills": [...],
  "formations": [...],
  "ecoles": [...]
}

---

## (score) Module : `score/compare.py`

Ce module est chargé de **comparer les informations extraites du CV et de l’offre d’emploi**, puis de calculer un **score de compatibilité**.  
Il prend en compte plusieurs catégories : **compétences techniques**, **soft skills**, **formations**, et **écoles**.

---

### **Objectif**
- Évaluer la correspondance entre le CV et l’offre :
  - Exactitude (match strict).
  - Similarité (match flou via fuzzy matching).
- Calculer des scores par catégorie et un **score global pondéré**.
- Gérer un système de **synonymes** pour normaliser les termes.
- Appliquer un **bonus de fréquence** pour valoriser les compétences répétées.

---

### **Fonctionnalités principales**
- **Normalisation des listes** (CV / Offre) via dictionnaire de synonymes.
- **Comparaison stricte ou floue** (fuzzy matching).
- **Score par catégorie** avec détails :
  - Matches.
  - Exigences manquantes.
- **Score global pondéré** avec bonus.
- **Gestion des fréquences** (bonus pour compétences répétées).

---

### **Description des fonctions clés**

#### `normaliser(liste, dic)`
- Remplace les mots par leurs formes standard à partir d’un dictionnaire de synonymes (`synonymes.json`).
- Exemple : *"python3"* → *"python"*.

---

#### `compare_listes(liste_cv, liste_offre, mode="strict", seuil_fuzzy=80)`
- Compare deux listes d’éléments :
  - **Mode strict** → correspondance exacte.
  - **Mode fuzzy** → similarité (basée sur `fuzzywuzzy.partial_ratio`).
- Retourne :
```json
{
  "score": 85.0,
  "matches": ["python", "docker"],
  "manquants": ["aws", "kubernetes"]
}


