from os import listdir
from os.path import isfile, join
import re
import fitz
import unidecode
from deep_translator import GoogleTranslator

def loadURL(repertoire):
    """
    Fonction permettant d'extraire une liste de fichier d'un repertoire
    @params:
        repertoire  - Required : Repertoire depuis lequel on veut extraire les fichiers
    """
    URL = [f for f in listdir(repertoire) if isfile(join(repertoire, f))]
    return URL

def cleanText(text):
    output = re.sub(r'(?<=\b[a-zA-ZÉ]) (?=[a-zA-Z]\b)', '', text) #colle les lettre qui sont seul 'a b ' devient 'ab'
    output = re.sub(r'(?<=\b[0-9]) (?=[0-9]\b)', '', output) #colle les chiffres qui sont seul '1 2 ' devient '12'
    output = output.replace('  ', ' ') # remplace tous les double espace par un espace simple
    return output

def extract_text_pdf(storage_file, pdf_files):
    """
    Fonction permettant de gérer l'extraction d'information des PDF
    @params:
        storage_file    - Required : Le fichier de stockage des PDF
        pdf_files       - Required : La liste des fichiers PDF

    """
    taille = len(pdf_files)
    compteur = 1

    for pdf_file in pdf_files:
        #Ouverture du CV
        doc = fitz.open(storage_file + pdf_file)
        #Pour chaque page du CV, on recupère tout le texte
        text = ""
        for page in doc:
            text = text + str(page.getText())
        tx = " ".join(text.split('\n'))
        tx = unidecode.unidecode(tx)
        #On traduit le texte en francais par ex: United Kingdom -> Royaume-Unis)
        tx = GoogleTranslator(source='auto', target='fr').translate(tx)
        #Extraction des informations des CV
        parsExtract.parser_text(storage_file,pdf_file,tx)
        #Progress bar pour voir l'évolution du processus
        compteur = compteur + 1

