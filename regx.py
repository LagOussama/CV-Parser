import re

from strsimpy import NormalizedLevenshtein

import soundex
import unidecode

MAIL_String = "[A-Za-z]+[A-Za-z0-9--\._]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,4}"
PHONE_String = "(?:(?:\+|00)33|0)\s?[1-9](?:[\s.-]?\d{2}){4}"
ADRESSE_String ="[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+"
AGE_String = "[0-9]{2,3} ANS"
DRIVER_LISENCE_String = "PERMIS ?(?:DE CONDUIRE|TYPE)? ?:? ?(?:AM|BSR|A|A1|A2|B|B1|B2|BE|BVA|C|C1|CE|C1E|D|D1|D2|DE|DE1)"
WEB_String = "(?:HTTP://|HTTPS://|HTTPS://)[A-Z0-9\.-=/]+"
PDF_String_Format = "2020-12-03(?:-|_)CV(?:-|_)[A-Z]+(?:-|_)[A-Za-zéïàèîôû_\-]+.pdf"

Name_String_Format = "2020-12-03(?:-|_)CV(?:-|_)([A-Z]+)(?:-|_)([A-Za-zéïàèîôû_\-]+).pdf"
FName_String_Format = '2020-12-03(?:-|_)CV(?:-|_)[A-Z]+(?:-|_)([A-Za-zéïàèîôû_\-]+).pdf'

MAIL = re.compile(MAIL_String)

PHONE = re.compile(PHONE_String)
ADRESSE = re.compile(ADRESSE_String)
AGE = re.compile(AGE_String)
DRIVER_LISENCE = re.compile(DRIVER_LISENCE_String)
WEB = re.compile(WEB_String)


def corr_prenom(prenom):
    prenom = unidecode.unidecode(prenom)
    prenom = prenom.replace('_', ' ')
    prenom = prenom.replace('-', ' ')
    listPrenom = prenom.split()
    prenom = ''
    for p in listPrenom:
        pre = p.capitalize()
        prenom = prenom + ' ' + pre
    prenom = prenom.strip()
    prenom = prenom.replace(' ', '-')
    return prenom



def findMail(text):
    mail = re.findall(MAIL, text)
    if mail != []:
        mail = mail[0]
        return '\'' + mail + '\''
    return 'NULL'

def findPhone(text):
    Phone = re.findall(PHONE, text)
    if Phone != []:
        Phone = Phone[0]
        Phone = Phone.replace(' ', '')
        Phone = Phone.replace('-', '')
        Phone = Phone.replace('.', '')
        return '\'' + Phone + '\''
    return 'NULL'

def findAdresse(text):
    adresse = re.findall(ADRESSE, text.upper())
    if adresse != []:
        return adresse[0]
    return 'NULL'

def findAge(text):
    age = re.findall(AGE, text.upper())
    if age != []:
        age = age[0]
        return re.sub('([0-9]{2,3}) ANS', '\g<1>', age)
    return  'NULL'

def findDriverlicence(text):
    listPermis = re.findall(DRIVER_LISENCE, text.upper())
    DLISENCE = []
    for p in listPermis:
        if re.match(DRIVER_LISENCE_String,p):
            per = re.sub(
                'PERMIS ?(?:DE CONDUIRE|TYPE)? ?:? ?((?:AM|BSR|A|A1|A2|B|B1|B2|BE|BVA|C|C1|CE|C1E|D|D1|D2|DE|DE1))',
                '\g<1>', p)
            DLISENCE.append(per)
    return DLISENCE

def findSites(text):
    return re.findall(WEB, text.upper())

def findName(pdf_file):
    nom = 'NULL'
    if re.match(PDF_String_Format, pdf_file):
        nom = re.sub(Name_String_Format, '\g<1>', pdf_file)
        nom = '\'' + nom + '\''
    return nom


def findFirstName_sexe(pdf_file,mail):
    prenom = 'NULL'
    sexe = 'NULL'
    if re.match(PDF_String_Format, pdf_file):
        prenom = re.sub(FName_String_Format, '\g<1>', pdf_file)
        prenom = prenom.strip().capitalize()
        fichier = open("Prenoms.csv", "r")
        for line in fichier:
            if line.lower().split(';')[0].lower() == prenom.lower():
                sexe = line.lower().split(';')[1].upper()
                sexe = '\'' + sexe[0] + '\''
                break
        fichier.close()
        # Si le prénom n'est pas dans la base de données
        # On va essayer de trouver le sexe en fonction des sons (soundex) et de la distance (Levenshtein) entre les prénoms
        # Ainsi, on va prendre un autre prénom proche phonétiquement et grammatiquement et on va prendre le sexe de ce prénom
        if sexe == 'NULL':
            dict_similitude = dict()
            fichier = open("Prenoms.csv", "r")
            for line in fichier:
                # Si le prénom produit le même son
                # On ajoute son score Levenshtein et le sexe associé
                if soundex.get_soundex_code(line.lower().split(';')[0].lower()) == soundex.get_soundex_code(
                        prenom.lower()):
                    normalized_levenshtein = NormalizedLevenshtein()
                    dict_similitude[
                        normalized_levenshtein.similarity(line.lower().split(';')[0].lower(), prenom.lower())] = \
                    line.lower().split(';')[1]
            # On associe le sexe du prénom qui maximise la similarité entre les prénoms  (si le dictionnaire n'est pas vide)
            if bool(dict_similitude):
                sexe = dict_similitude[max(dict_similitude, key=dict_similitude.get)].upper()
                sexe = '\'' + sexe[0] + '\''
            fichier.close()
        prenom = corr_prenom(prenom)
        prenom = '\'' + prenom.strip() + '\''
    # Si le pdf n'est pas de la forme souhaité (dans un but d'élargissement à d'autre CV)
    # Dans notre Projet, si notre base de CV est bien construite, on ne tombe pas dans ce cas
    else:
        fichier = open("Prenoms.csv", "r")
        for line in fichier:
            # On cherche dans chaque PDF est ce que un mot (un prénom) apparait dans la base des prénoms
            if line.lower().split(';')[0] in text.lower().split():
                prenom = line.lower().split(';')[0]
                prenom = corr_prenom(prenom)

                sexe = line.split(';')[1].upper()
                sexe = '\'' + sexe[0] + '\''

                # Si le mot qu'on a désigné comme étant un prénom est présent dans le titre du pdf ou le mail du condidat, il y a de forte probabilité que ça soit bien le prénom
                for adr in mail:
                    if adr.lower().find(prenom.lower()) >= 0:
                        prenom = corr_prenom(prenom)
                        prenom = '\'' + prenom.strip() + '\''
                        break
                if pdf_file.lower().find(prenom.lower()) >= 0:
                    prenom = corr_prenom(prenom)
                    prenom = '\'' + prenom.strip() + '\''
                    break
            else:
                # Si le prénom ne se trouve pas dans la base de données, on fonctionne avec la phonétique du nom du fichier
                for mot in pdf_file.split('_'):
                    mot = mot.replace('.', ' ')
                    if soundex.get_soundex_code(line.lower().split(';')[0]) == soundex.get_soundex_code(mot):
                        prenom = mot
                        prenom = corr_prenom(prenom)
                        prenom = '\'' + prenom.strip() + '\''
                        break
        fichier.close()
    return prenom,sexe