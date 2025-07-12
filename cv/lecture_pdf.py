import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def est_pdf_scanné(fichier_pdf):
    doc = fitz.open(fichier_pdf)
    for page in doc:
        if page.get_text().strip():
            return False  # du texte est détecté → PDF textuel
    return True 

def ocr_depuis_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("L")  # niveau de gris
    return pytesseract.image_to_string(image, lang="fra")  # l’OCR (= lecture automatique du texte sur une image)

def extraire_texte_pdf_scanné(fichier_pdf):
    doc = fitz.open(fichier_pdf)
    texte = ""
    for page in doc:
        for img in page.get_images(full=True): # cherche les photos (images) sur chaque page.
            xref = img[0] #identifiant de l’image dans le PDF
            base_image = doc.extract_image(xref) # extrait l’image complète (en binaire) à partir de son xref.
            image_bytes = base_image["image"] #On ne garde que la partie qui nous intéresse : le contenu de l’image. car le resultat precedente est un dictionnaire ("image",....)
            texte += ocr_depuis_image(image_bytes) + "\n" #assemble tout le texte trouvé sur toutes les images du PDF
    return texte

def extraire_blocs_avec_positions(fichier_pdf):
    doc = fitz.open(fichier_pdf)
    all_blocks = []
    for page_num, page in enumerate(doc):
        blocs = page.get_text("blocks")  # chaque bloc contient (x0, y0, x1, y1, texte, ...)
        for b in blocs:
            x0, y0, x1, y1, texte = b[:5]
            all_blocks.append({
                "page": page_num + 1,
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "texte": texte.strip()
            })
    return sorted(all_blocks, key=lambda b: (b['page'], b['y0']))  # du haut vers le bas(necessaire car l'ordinateur peut les lire dans n'importe quel ordre)(triés du haut vers le bas (y0 croissant).)

"""def extraire_blocs_ocr_avec_positions(fichier_pdf):
    doc = fitz.open(fichier_pdf)
    blocs = []
    for page_num, page in enumerate(doc, start=1):
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes)).convert("L")
            data = pytesseract.image_to_data(image, lang="fra", output_type=pytesseract.Output.DICT)
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    blocs.append({
                        "page": page_num,
                        "x0": x,
                        "y0": y,
                        "x1": x + w,
                        "y1": y + h,
                        "texte": text
                    })
    return sorted(blocs, key=lambda b: (b['page'], b['y0'], b['x0']))
"""