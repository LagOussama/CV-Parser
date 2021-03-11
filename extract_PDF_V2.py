import sys, fitz
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import codecs
import re
import string
import unidecode
import soundex
from strsimpy.normalized_levenshtein import NormalizedLevenshtein
import operator
import uuid
from random import *
import pandas as pd
import cv2
from pdf2image import convert_from_path
from datetime import datetime
import locale
from deep_translator import GoogleTranslator


def loadURL(repertoire):
    """
    Fonction permettant d'extraire une liste de fichier d'un repertoire
    @params:
        repertoire  - Required : Repertoire depuis lequel on veut extraire les fichiers
    """
    return URL


def cleanText(text):
    output = re.sub(r'(?<=\b[a-zA-ZÉ]) (?=[a-zA-Z]\b)', '', text)  # colle les lettre qui sont seul 'a b ' devient 'ab'
    output = re.sub(r'(?<=\b[0-9]) (?=[0-9]\b)', '', output)  # colle les chiffres qui sont seul '1 2 ' devient '12'
    output = output.replace('  ', ' ')  # remplace tous les double espace par un espace simple
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
        # Ouverture du CV
        doc = fitz.open(storage_file + pdf_file)
        # Pour chaque page du CV, on recupère tout le texte
        text = ""
        for page in doc:
            text = text + str(page.getText())
        tx = " ".join(text.split('\n'))
        tx = unidecode.unidecode(tx)
        # On traduit le texte en francais par ex: United Kingdom -> Royaume-Unis)
        tx = GoogleTranslator(source='auto', target='fr').translate(tx)
        # Extraction des informations des CV
        parser_text(storage_file, pdf_file, tx)

        compteur = compteur + 1


def parser_text(storage_file, pdf_file, text):
    """
    Fonction d'extraire l'information d'un PDF
    @params:
        storage_file   - Required  : Le fichier de stockage des PDF
        pdf_file        - Required  : Le nom du fichier PDF
        text            - Required  : Le contenu du fichier PDF
    """

    # Enlever les accents du text extrait du pdf
    text = unidecode.unidecode(text)
    # Définition des regexp
    regexp_mail = re.compile("[A-Za-z]+[A-Za-z0-9--\._]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,4}")

    regexp_tel = re.compile('(?:(?:\+|00)33|0)\s?[1-9](?:[\s.-]?\d{2}){4}')
    regexp_adresse = re.compile(
        '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+')
    regexp_age = re.compile('[0-9]{2,3} ANS')
    regexp_permis = re.compile(
        'PERMIS ?(?:DE CONDUIRE|TYPE)? ?:? ?(?:AM|BSR|A|A1|A2|B|B1|B2|BE|BVA|C|C1|CE|C1E|D|D1|D2|DE|DE1)')
    regexp_site_res = re.compile('(?:HTTP://|HTTPS://|HTTPS://)[A-Z0-9\.-=/]+')
    # Récupération du mail, tel, adresse, age, permis, sexe, site
    # Mail
    mail = re.findall(regexp_mail, text)
    if mail != []:
        mail = mail[0]
        mail = '\'' + mail + '\''
    else:
        mail = 'NULL'

    # Tel
    tel = re.findall(regexp_tel, text)
    if tel != []:
        tel = tel[0]
        tel = tel.replace(' ', '')
        tel = tel.replace('-', '')
        tel = tel.replace('.', '')
        tel = '\'' + tel + '\''
    else:
        tel = 'NULL'
    # Adresse
    adresse = re.findall(regexp_adresse, text.upper())
    if adresse != []:
        adresse = adresse[0]
    else:
        adresse = 'NULL'
    # Age
    age = re.findall(regexp_age, text.upper())
    if age != []:
        age = age[0]
        age = re.sub('([0-9]{2,3}) ANS', '\g<1>', age)
    else:
        age = 'NULL'
    # Permis
    listPermis = re.findall(regexp_permis, text.upper())
    permis = []
    for p in listPermis:
        if re.match('PERMIS ?(?:DE CONDUIRE|TYPE)? ?:? ?(?:AM|BSR|A|A1|A2|B|B1|B2|BE|BVA|C|C1|CE|C1E|D|D1|D2|DE|DE1)',
                    p):
            per = re.sub(
                'PERMIS ?(?:DE CONDUIRE|TYPE)? ?:? ?((?:AM|BSR|A|A1|A2|B|B1|B2|BE|BVA|C|C1|CE|C1E|D|D1|D2|DE|DE1))',
                '\g<1>', p)
            permis.append(per)
    # Sites/Réseaux
    site_res = re.findall(regexp_site_res, text.upper())

    # Récuperation du nom
    nom = 'NULL'
    if re.match('2020-12-03(?:-|_)CV(?:-|_)[A-Z]+(?:-|_)[A-Za-zéïàèîôû_\-]+.pdf', pdf_file):
        nom = re.sub('2020-12-03(?:-|_)CV(?:-|_)([A-Z]+)(?:-|_)([A-Za-zéïàèîôû_\-]+).pdf', '\g<1>', pdf_file)
        nom = '\'' + unidecode.unidecode(nom) + '\''

    # Récupération du prénom et du sexe (grâce à la base de Prénoms.csv qui contient le sexe associé au prénom)
    prenom = 'NULL'
    sexe = 'NULL'
    if re.match('2020-12-03(?:-|_)CV(?:-|_)[A-Z]+(?:-|_)[A-Za-zéïàèîôû_\-]+.pdf', pdf_file):
        prenom = re.sub('2020-12-03(?:-|_)CV(?:-|_)[A-Z]+(?:-|_)([A-Za-zéïàèîôû_\-]+).pdf', '\g<1>', pdf_file)
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

    tabFormation = extraire_formation(text)
    listCompetence = extraire_competence(text)
    listLangues = extraire_langue(text)
    listCentreInteret = extraire_centreInteret(text)
    adresse = unidecode.unidecode(adresse)
    nom = unidecode.unidecode(nom)
    mail = unidecode.unidecode(mail)
    # Appelle de la fonction pour creer les requetes d'insertions
    create_requete(storage_file, pdf_file, mail, tel, adresse, age, prenom, nom, sexe, permis, site_res, 'NULL', 'NULL',
                   tabFormation, listCompetence, listLangues, listCentreInteret)


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


def extraire_formation(text):
    # clean le texte du cv
    s = cleanText(text)
    tabFormation = []
    # pour formation
    # on utilise 2 méthode pour extraire les formation soit on coupe les bloc par date (on arrete le bloc quand une 3e data apparait)
    # soit on coupe les bloc par les mots de niveau comme master, licence, etc et on arrete le bloc quand un autre de ces mot apparait
    # et sinon les 2 méthodes arrete le bloc si une longueur est dépasse ou si les mots experience apparaissent
    # on compare quelle méthode trouve le plus de formation
    regex = r"(20[0-2][0-9]|19[0-9][0-9]).{0,5}(20[0-2][0-9]|19[0-9][0-9]).{0,200}?(?=(master|licence|Baccalaureat|dut|lycee|universite|ecole))(.{0,400}?(?=(20[0-2][0-9]|19[0-9][0-9]|Expérience|EXPERIENCE|experience|experience))|(.{0,200}))"
    matches = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
    compteur1 = 0
    for matchNum, match in enumerate(matches, start=1):
        compteur1 = compteur1 + 1

    regex2 = r"(Master|master|MASTER|Licence|LICENCE|licence|Baccalaureat)(.{0,400}?(?=(Master|master|MASTER|Licence|LICENCE|licence|Experience|EXPERIENCES|experience|experience|COMPETENCES|Competence|competence|Baccalaureat|EXPERIENCES|EXPERIENCE))|.{0,200})"
    matches = re.finditer(regex2, s, re.MULTILINE | re.IGNORECASE)

    compteur2 = 0
    for matchNum, match in enumerate(matches, start=1):
        compteur2 = compteur2 + 1
    # on utilise le regexp le plus performant a chaque fois

    if compteur1 >= compteur2:
        regex = regex
    else:
        regex = regex2
    matches = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
    compteur1 = 0
    # on analyse chaque formation trouvé

    for matchNum, match in enumerate(matches, start=1):
        compteur1 = compteur1 + 1
        formation = match.group()

        # expression reguliere pour extraire le niveau de la formation
        regexFormation = r"(master ?[1-2])|(licence|L1|L2|L3)|(baccalaureat|baccalaureat)|(DUT)"
        matchesFormation = re.finditer(regexFormation, formation, re.IGNORECASE)
        niveau = 'NULL'
        for matchNumFormation, matchFormation in enumerate(matchesFormation, start=1):
            niveau = "'" + matchFormation.group().strip() + "'"

            # expression reguliere pour extraire le nom de l'ecole
        ecole = "NULL"
        regexEcole = r"(Universite|lycee|ecole|college)[ ][a-z]*?[ ][a-z0-9]*"
        matchesEcole = re.finditer(regexEcole, formation, re.IGNORECASE)
        for matchNumEcole, matchEcole in enumerate(matchesEcole, start=1):
            ecole = "'" + matchEcole.group().strip() + "'"
            # expression reguliere pour extraire la date de debut et de fin de la formation
        dateDebut = "NULL"
        dateFin = "NULL"
        regexDate = r"((janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)[ ])?(20[0-2][0-9]|19[0-9][0-9])"
        matchesDate = re.finditer(regexDate, formation, re.MULTILINE | re.IGNORECASE)
        compteurDate = 0
        for matchNumDate, matchDate in enumerate(matchesDate, start=1):
            if matchNumDate == 1:
                dateDebut = "'" + matchDate.group().strip() + "'"
            elif matchNumDate == 2:
                dateFin = "'" + matchDate.group().strip() + "'"
                # expression reguliere pour extraire la specialite de la formation
        specialite = "NULL"
        regexSpecialite = r"(informatique)"
        matchesSpecialite = re.finditer(regexSpecialite, formation, re.IGNORECASE)
        for matchNumEcole, matchSpecialite in enumerate(matchesSpecialite, start=1):
            specialite = "'" + matchSpecialite.group().strip() + "'"

            # out_file.write("EXEC INSERT_FORMATION("+ str(idFormation) +","+ niveau +","+ specialite +","+ ecole +","+  dateDebut +","+ dateFin +")\n")
        tabFormation.append([niveau, specialite, ecole, dateDebut, dateFin])

    return tabFormation


def extraire_competence(text):
    # clean le texte du cv
    s = cleanText(text)
    regex = r"(Communication|réseautage|Esprit d equipe|Travail autonome|Capacité à travailler sous pression|marketing|rédaction|développement de contenu|Gestion du temps|Photoshop|Joomia|Indesign|Graphisme|Illustration|Photographie|Images animéees|Vidéographie|Mise en page|Ruby|Microsoft ASP.NET MVC.Web API|C#|éco-responsables|processus de recyclage|Conceptualisation des espaces 3D|Gestion de marque|Analyse des concurrents|Marketing sur les réseaux sociaux|Optimisation du moteur de recherche|Marketing de contenu|Recherche de marché|Rédacteur publicitaire|notions juridiques et financières|Rigueur|diplomatie|Travailleur social agréé|Association|action sociale|Sens de responsabilités|Travail en équipe|Flexible|Facilité dintégration|Sens de responsabilité|Autodidaxie|Créativité et force de proposition|Ambitieux|Organisé|Appliqué|Désireux dapprendre|Dynamique|Communication|adaptation facile|nouvelles technologies|Bénévole|Organisé|autonome|assidu|curieux|Travail en équipe|Persévérant|Adaptable|Communicant|Curiosité|Sérieux|Motivé|rigoureux|organisé|autonome|Bonne capacité danalyse|traitements de problématiques|Bonnes qualités rédactionnel|bonne approche des clients|Sens  négociation|Capacité dadaptation|Compétences relationnelles|Esprit déquipe|Travail en équipe|Respect des délais|Établir un cahier des charges|Capacité à sorganiser|Déterminé|curieuse|rigoureuse|aventures|Relationnel|Adaptabilité|Apprentissage|Rigueur|Autonomie|Travail en groupe|Travail sous pression|Autonome|Organisé|Rigoureux|Eclipse|NetBeans|AndroidStudio|Code:Blocks|Dev\-C\+\+|VisualStudio|STVisualdevelop|IDE|SASSoftware|SASViya|Jupyter|Linux|Ubuntu|NASM|Anaconda|Spyder|Talend|Tableau|BusinessObjects|SAS|Jira|Trello|jupyter-notebook|pycharm|Oracle|SasStudio|Mangodb|PowerBI|Talend|Tableau|Excel|Jupyter|Anaconda|Jupyter|spyder|KNIME|PhpMyAdmin|Colab|Dynamic|Dynamique|collaborative work|Collaboratif|Analyse critique|Ponctualité|Travail en groupe|Gestion de temps|Esprit d’analyse|Méticulosité|communication|Agile|Waterfal|Python|SQL|PL/SQL|SAS|Java|C|SQL|MATLAB|Python|Sql|Java|OcamlMatlab|UML|Haskell|SQL3|SAS|JavaScript|PHP|J2E|Pascal|HTML|CSS|XML|R|Java/JEE|OCaml|Mysql|Html|VBA|DATA warehouse|DateWarehouse|PHP5|Symfony|Angular9|SpringBoot|JEE|HTML5|CSS3|JS|JavaScript|pandas|numpy|matplotlib|seaborn|PLSQL|Ocaml|Scala|SQL|PLSQL|NoSQL|Prolog|SAS|Oracle|MongoDB|MySQL|Talend|Tableau|BusinessObjects|TensorFlow|Keras|Scikit-learn|Scikit-Fuzzy|MicrosoftOfficeExcel|Prolog|Oracle|MongoDB|MySQL|DataBase|Talend|DataIntegration|DataQuality|SAS|Tableau|BusinessObjects|HADOOP|HDFS|MapReduce|HBASE|SPARK|RSTUDIO|WEKA|IBMSPSSMODELER|REDIS|MongoDB|JupyterNotebook|Eclipse|SAS|VisualStudioCode|Rstudio|AndroidStudio|Git|Oracle|SASViya|SAS9|MangoDB|MATLAB|Oracle|BusinessObjects|MéthodeAgile|SCRUM|Trello|GitHub|oracle|PLSQL|SQLserver|SSIS|Trello|Word|Excel|PowerPoint|make|git|Oracle|SasStudio|PowerBI|Excel|Jupyter|ApacheKakfa|Elasticsearch|Logstash|Kibana|FileBeat|Trello|MarvenApp|Git|UML|Docker|SpringBoot|SpringData|SpringSecurity|HTML|Thymeleaf|CSS|VB|UML|GRASPpattern|Merise|Proto.io|Axure|Internet des objets|IOT|Business intelligence|Représentation graphique de données statistiques|Domotique|meetup tafterworks|Statistiques)"
    matches = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
    listecompetences = []
    competence = "null"

    for matchNum, match in enumerate(matches, start=1):
        competence = "'" + match.group().lower().strip() + "'"
        listecompetences.append(competence)

    setCompetence = set(listecompetences)  # transforme en set pour enlever doublon
    listCompetence = list(setCompetence)  # remet en liste

    return (listCompetence)


def extraire_langue(text):
    s = cleanText(text)
    listLangue = []
    langue = "NULL"
    niveau = "NULL"
    regex = r"(français|francais|anglais|Allemand|Kabyle|Arabe|Chinois|mandarin|hindi|bengali|panjabi|Espagnol|Deutsch|Turc|Berbère|Wolof|Tamoul|italien|portuguais|russe|japonais|danois|polonais|javanais|telougou|malais|coreen|marathi|turc|vietnamien|tamoul|italien|persan|thai|gujarati|polonais|pachtou|kannada|malayalam|soundanais|oriya|birman|ukrainien|bhojpouri|filipino |yorouba|maithili|ouzbek|sindhi|amharique|peul|roumain|oromo|igbo |azéri|awadhi|visayan|neerlandais|kurde|malgache|saraiki|chittagonien|khmer|turkmène|assamais|madourais|somali|marwari|magahi|haryanvi|hongrois|chhattisgarhi|grec|chewa|deccan|akan|kazakh|sylheti|zoulou|tcheque)[ ](.*?[ ].*?[ ].*?[ ])"

    matches = re.finditer(regex, text, re.MULTILINE | re.IGNORECASE)

    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            if (groupNum == 1):
                langue = "'" + match.group(groupNum).strip() + "'"
            elif (groupNum == 2):
                regexNiveau = r"(A1|B1|B2|C1|C2|langue maternelle|bilingue|débutant|avancé|HSK 3)"
                matchesNiveau = re.finditer(regexNiveau, match.group(groupNum), re.IGNORECASE)
                for matchNumNiveau, matchNiveau in enumerate(matchesNiveau, start=1):
                    niveau = "'" + matchNiveau.group().strip() + "'"
        listLangue.append([langue, niveau])
    return (listLangue)


def extraire_centreInteret(text):
    # clean le texte du cv
    s = cleanText(text)

    regex = r"(Cyclisme|Patisserie|Lecture|Musique|Bricolages|Associations|Conférences|Mangas|Science|Jeux videos|Technologie|Physique|Philosophie|Travail Associatif|Planification|Entraînement physique|Transport et mobilité|technologies Web émergentes|Tennis de table|Bricolage|Voyage|Natation|handball|Engagement bénévole|Aviron|Boxe|Bénévolat|Photographie|Basketball|Football|cinéma|escalade|Photoshop|Tennis|SériesTV|Films|Art martiaux|musique|documentaire|Pâtisserie|volley-ball|bénévolat|Football|littérature|Cyclisme|Cuisiner|Hand-ball|Jeux cognitifs)"
    matches = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
    listeCentreInteret = []
    competence = "null"

    for matchNum, match in enumerate(matches, start=1):
        interet = "'" + match.group().lower().strip() + "'"
        listeCentreInteret.append(interet)

    setCentreInteret = set(listeCentreInteret)  # transforme en set pour enlever doublon
    listCentreInteret = list(setCentreInteret)  # remet en liste

    # print(listCentreInteret)
    return (listCentreInteret)


def create_requete(storage_file, pdf_file, mail, tel, adresse, age, prenom, nom, sexe, permis, site_res, date_naiss,
                   nationalite, tabFormation, listCompetence, listLangues, listCentreInteret):
    """
    Fonction permettant de créer les requêtes d'insertion dans le fichier .sql
    La fonction va se charger de faire les modifications des données pour qu'elles collent aux insertions
    @params:
        storage_file   -Require : Le fichier de stockage des PDF
        pdf_file        -Require : Le nom du fichier PDF que l'on traite
        mail            -Require : Le mail du candidat
        tel             -Require : Le numéro de téléphone du candidat
        adresse         -Require : L'adresse du candidat
        age             -Require : L'âge du candidat
        prenom          -Require : Le prénom du candidat
        nom             -Require : Le nom de famille du candidat
        sexe            -Require : Le sexe du candidat
        permis          -Require : La liste des permis du candidat
        site_res        -Require : La liste des sites internets du candidat
        date_naiss      -Require : La date de naissance du candidat
        nationalite     -Require : La nationalité du candidat
        tabFormation    -Require : La liste des formations du candidat
        listCompetence  -Require : La liste des compétences du candidat
        listLangues     -Require : La liste des langues
    """
    # Normalisation des attributs
    sexe = sexe.strip().upper()
    nationalite = nationalite.strip().upper()
    adresse = adresse.strip().upper()
    mail = mail.strip().lower()
    # Ouverture du fichier csv
    ids = pd.read_csv('./ids_tables.txt', delimiter=',')

    # Récupération des identifiants disponibles
    id_can = ids['id_can'][0]
    id_adr = ids['id_adr'][0]
    id_cv = ids['id_cv'][0]
    id_site = ids['id_site'][0]

    new_id_can = int(id_can) + 1
    new_id_cv = int(id_cv) + 1

    if adresse == 'NULL':
        new_id_adr = int(id_adr)
        id_adr = 'NULL'
    else:
        new_id_adr = int(id_adr) + 1
        id_adr = '\'' + str(id_adr) + '\''

    # Insertion des id (pour éviter la redondance)
    ids = pd.DataFrame(
        {'id_adr': [new_id_adr], 'id_can': [new_id_can], 'id_cv': [new_id_cv], 'id_site': [int(id_site)]})
    ids.to_csv('./ids_tables.txt', index=False, header=True, mode='w')

    # On écrit dans le fichier de sortie .sql
    out_file = open('./G1_InsertDon_CV.sql', 'a')

    # Insertion Adresses
    if adresse != 'NULL':
        num_adr, localite_adr, nomRue_adr, cp_adr, ville_adr, pays_adr, continent_adr = eclater_adresse(adresse)
        out_file.write('EXEC INSERT_ADRESSES(' + str(
            id_adr) + ',' + num_adr + ',' + localite_adr + ',' + nomRue_adr + ',' + cp_adr + ',' + ville_adr + ',' + pays_adr + ',' + continent_adr + ');\n')
    # Insertion Candidats
    out_file.write('EXEC INSERT_CANDIDATS(\'' + str(id_can) + '\',' + str(
        id_adr) + ',' + nom + ',' + prenom + ',' + sexe + ',' + age + ',' + date_naiss + ',' + mail + ',' + nationalite + ',' + tel + ');\n')
    # Insertion Permis
    for p in permis:
        p = p.strip().upper()
        date_obtention = 'NULL'
        out_file.write('EXEC INSERT_OBTENTIONPERMIS(\'' + p + '\',\'' + str(id_can) + '\',' + date_obtention + ');\n')
    # Insertion sites/Réseaux sociaux
    for s in site_res:
        id_site = ids['id_site'][0]
        new_id_site = int(id_site) + 1

        # Insertion des id (pour éviter la redondance)
        ids = pd.DataFrame(
            {'id_adr': [new_id_adr], 'id_can': [new_id_can], 'id_cv': [new_id_cv], 'id_site': [new_id_site]})
        ids.to_csv('./ids_tables.txt', index=False, header=True, mode='w')
        s = unidecode.unidecode(s)
        out_file.write('EXEC INSERT_SITES_RESEAUX(\'' + str(id_site) + '\',\'' + str(id_can) + '\',\'' + s + '\');\n')
    # Insertion des langues
    for langue, niveau in listLangues:
        langue = langue.strip().upper()
        niveau = niveau.strip().upper()
        out_file.write('EXEC INSERT_RELATION_LANG_CAN(' + langue + ',\'' + str(id_can) + '\',' + niveau + ');\n')
    # Insertion CV
    titre_cv = 'NULL'
    description_cv = 'NULL'
    posteRecherche_cv = 'NULL'
    typePoste_cv = 'NULL'
    dispo_cv = 'NULL'
    admis = '\'' + 'ACCEPTE' + '\''
    if storage_file.lower().find('refuse') >= 0:
        admis = '\'' + 'REFUSE' + '\''
    date_transmission = 'SYSDATE'
    nom_cv = unidecode.unidecode(pdf_file)

    out_file.write('EXEC INSERT_CV(\'' + str(id_cv) + '\',\'' + str(
        id_can) + '\',\'' + nom_cv + '\',' + titre_cv + ',' + description_cv + ',' + posteRecherche_cv + ',' + typePoste_cv + ',' + dispo_cv + ',' + admis + ',' + date_transmission+ ');\n')

    # Insertion Formations
    for formation in tabFormation:
        niveau = unidecode.unidecode(formation[0].strip().upper())
        specialite = unidecode.unidecode(formation[1].strip().upper())
        ecole = unidecode.unidecode(formation[2].strip().upper())
        out_file.write('EXEC INSERT_SUIT_FORMATIONS(' + ecole + ',' + niveau + ',' + specialite + ',\'' + str(
            id_can) + '\',' + convert_date(formation[3]) + ',' + convert_date(formation[4]) + ');\n')

    # Insertion Compétence
    for competence in listCompetence:
        competence = unidecode.unidecode(competence.strip().upper())
        catCpt = find_cat_cpt(competence)
        out_file.write('EXEC INSERT_RELATION_COMP_CAN(' + competence + ',' + catCpt + ',\'' + str(id_can) + '\');\n')

    # Insertion Centre d'interêts
    for centreInteret in listCentreInteret:
        centreInteret = unidecode.unidecode(centreInteret.strip().upper())
        out_file.write('EXEC INSERT_RELATION_CENTINT_CAN(' + centreInteret + ',\'' + str(id_can) + '\');\n')

    out_file.close()
    # print(mail,tel,adresse,age,prenom,nom,sexe,permis,site_res)


def find_cat_cpt(cpt):
    cpt = cpt[1:]
    cpt = cpt[:-1]
    cat_bdd = ['APPRENTISSAGE', 'SASSOFTWARE', 'SASVIYA', 'BUSINESS OBJECTS', 'BUSINESSOBJECTS', 'SQL', 'ORACLE',
               'JAVA/JEE', 'SQL3', 'MYSQL', 'DATA WAREHOUSE', 'PLSQL', 'NOSQL', 'MONGODB', 'DATABASE',
               'DATA INTEGRATION', 'DATAQUALITY', 'SQLSERVER', 'SPRINGBOOT', 'SPRINGDATA', 'SPRINGSECURITY',
               'BUSINESS INTELLIGENCE', 'TABLEAU', 'REPRESENTATION GRAPHIQUE DE DONNEES STATISTIQUES',
               'MEETUP TAFTERWORKS']
    cat_comp = ['INTERNET DES OBJETS', ' IOT']
    cat_web = ['DEVELOPPEMENT DE CONTENU', 'PHPMYADMIN', 'JAVASCRIPT', 'PHP', 'J2E', 'HTML', 'CSS', 'XML', 'PHP5',
               'SYMFONY', 'JS', 'CSS3', 'JAVASCRIPT']
    cat_lang = ['C', 'SAS', 'PYTHON', 'JAVA', 'R', 'C++', 'C#', 'MATLAB', 'OCAML', 'UML', 'HASKELL', 'SCALA']
    cat_crea = ['PHOTOSHOP', 'PHOTOGRAPHIE', 'VIDEOGRAPHIE', 'CREATIVITE']
    cat_se = ['LINUX', 'MACOS', 'WINDOWS', 'UBUNTU', 'DEBIAN']
    cat_outil = ['NETBEANS', 'ANDROIDSTUDIO', 'CODE:BLOCKS', 'VISUALSTUDIO', 'STVISUALDEVELOP', 'JUPYTER', 'ANACONDA',
                 'SPYDER', 'TALEND', 'JIRA', 'TRELLO', 'JUPYTER-NOTEBOOK', 'SASSTUDIO', 'EXCEL', 'KNIME', 'COLAB',
                 'MICROSOFTOFFICEEXCEL', 'PANDAS', 'NUMPY', 'SCIKIT-LEARN', 'SCIKIT-FUZZY', 'HADOOP', 'SPARK',
                 'RSTUDIO', 'JUPYTERNOTEBOOK', 'ECLIPSE', 'STUDIOCODE', 'GIT', 'SASVIYA', 'METHODEAGILE', 'GITHUB',
                 'POWERPOINT', 'APACHEKAKFA', 'DOMOTIQUE', 'WORD', 'EXCEL', 'MICROSOFT ASP.NET MVC.WEB API']
    cat_softSkill = ['BENEVOLE', 'ANALYSE DES CONCURRENTS', 'COMMUNICATION', 'RESEAUTAGE', 'ESPRIT D EQUIPE',
                     'TRAVAIL AUTONOME', 'CAPACITE A TRAVAILLER SOUS PRESSION', 'GESTION DU TEMPS',
                     'RECHERCHE DE MARCHE', 'FACILITE DINTEGRATION', 'DIPLOMATIE', 'TRAVAILLEUR SOCIAL AGREE',
                     'AUTODIDAXIE', 'ORGANISE', 'APPLIQUE', 'DYNAMIQUE', 'AGILE', 'ASSOCIATION', 'ACTION SOCIALE',
                     'SENS DE RESPONSABILITÉS', 'TRAVAIL EN EQUIPE', 'FLEXIBLE', 'COMMUNICATION', 'ADAPTATION FACILE',
                     'CAPACITE DADAPTATION', 'CURIEUX', 'TRAVAIL EN EQUIPE', 'ADAPTABLE', 'COMMUNICANT', 'SERIEUX',
                     'MOTIVE', 'RIGOUREUX', 'BONNE APPROCHE DES CLIENTS', 'SENS  NEGOCIATION',
                     'COMPETENCES RELATIONNELLES', 'ESPRIT DEQUIPE', 'TRAVAIL EN EQUIPE', ' RESPECT DES DELAIS',
                     'ETABLIR UN CAHIER DES CHARGES', 'CAPACITE À SORGANISER', 'DETERMINE', 'CURIEUSE', 'RIGOUREUSE',
                     'AVENTURES', 'RELATIONNEL', 'ADAPTABILITE', 'RIGUEUR', 'AUTONOMIE', 'TRAVAIL EN GROUPE',
                     'TRAVAIL SOUS PRESSION', 'ECLIPSE', 'DYNAMIC', 'DYNAMIQUE', 'COLLABORATIVE WORK', 'COLLABORATIF',
                     'PONCTUALITE', 'TRAVAIL EN GROUPE', 'GESTION DE TEMPS', 'ESPRIT D’ANALYSE']
    if cpt.upper() in cat_bdd:
        return '\'' + 'BASE DE DONNEES' + '\''
    elif cpt.upper() in cat_lang:
        return '\'' + 'LANGAGE DE PROGRAMMATION' + '\''
    elif cpt.upper() in cat_comp:
        return '\'' + 'ELECTRONIQUE' + '\''
    elif cpt.upper() in cat_crea:
        return '\'' + 'CREATIVITE' + '\''
    elif cpt.upper() in cat_web:
        return '\'' + 'WEB' + '\''
    elif cpt.upper() in cat_se:
        return '\'' + 'SYSTEME EXPLOITATION' + '\''
    elif cpt.upper() in cat_outil:
        return '\'' + 'OUTILS' + '\''
    elif cpt.upper() in cat_softSkill:
        return '\'' + 'SOFTSKILLS' + '\''
    else:
        return 'NULL'


def convert_date(date):
    """
    Fonction permettant de convertir les dates dans le format souhaité
    @params:
        date -Require : La date
    @return 
        date : La date dans le bon format
    """
    # On se met en français
    dateNorm = date[1:][:-1].lower()
    if re.match('(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre) ([0-9]{4})',
                dateNorm):
        if re.match('decembre [0-9]+', dateNorm):
            an = re.sub('decembre ([0-9]+)', '\g<1>', dateNorm)
            dateNorm = 'décembre ' + an
        elif re.match('fevrier [0-9]+', dateNorm):
            an = re.sub('fevrier ([0-9]+)', '\g<1>', dateNorm)
            dateNorm = 'février ' + an
        elif re.match('aout [0-9]+', dateNorm):
            an = re.sub('aout ([0-9]+)', '\g<1>', dateNorm)
            dateNorm = 'août ' + an
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        # On récupère convertie la date en format numrique en supprimant les apostrophes en début et fin de date
        dateConvert = datetime.strptime(dateNorm, '%B %Y')
        # On crée la date
        date = '\'' + str(dateConvert.day) + '/' + str(dateConvert.month) + '/' + str(dateConvert.year) + '\''
    elif re.match('([0-9]{4})', dateNorm):
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        # On récupère convertie la date en format numrique en supprimant les apostrophes en début et fin de date
        dateConvert = datetime.strptime(dateNorm, '%Y')
        # On crée la date
        date = '\'' + str(dateConvert.day) + '/' + str(dateConvert.month) + '/' + str(dateConvert.year) + '\''

    date = date.strip().upper()
    return date


# Fonction permettant de séprarer les différents attributs d'une adresse
def eclater_adresse(adresse):
    """
    Fonction permettant de scinder l'adresse 
    @params:
        adresse         - Required  : L'adresse à scinder 
    @return:
        num_adr         : Le numéro de la voie ou NULL
        localite_adr    : Le type de la voie ou NULL
        nomRue_adr      : Le nom de la rue ou NULL
        cp_adr          : Le code postal de la ville ou NULL
        ville_adr       : Le nom de la ville ou NULL
        pays_adr        : Le nom du pays
        continent_adr   : Le nom du contient
    """
    punctuation = ['(', ')', '?', ':', ';', ',', '.', '!', '/', '-', "_"]
    num_adr = 'NULL'
    localite_adr = 'NULL'
    nomRue_adr = 'NULL'
    cp_adr = 'NULL'
    ville_adr = 'NULL'
    pays_adr = 'FRANCE'
    continent_adr = 'EUROPE'
    if re.match(
            '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',
            adresse):
        num_adr = re.sub(
            '([0-9]+)(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',
            '\g<1>', adresse)
        cpl_adr = re.sub(
            '[0-9]+((?:BIS|TER)?),? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',
            '\g<1>', adresse)
        num_adr = num_adr + cpl_adr
        localite_adr = re.sub(
            '[0-9]+(?:BIS|TER)?,? ?((?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS)) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',
            '\g<1>', adresse)
        nomRue_adr = re.sub(
            '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) ([A-Z ]+),? ?(?:[0-9]{5}| )? [A-Z\-]+',
            '\g<1>', adresse)
        cp_adr = re.sub(
            '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?((?:[0-9]{5}| ))? [A-Z\-]+',
            '\g<1>', adresse)
        if cp_adr == '':
            cp_adr = 'NULL'
        else:
            cp_adr = '\'' + cp_adr.strip().upper() + '\''
        ville_adr = re.sub(
            '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? ([A-Z\-]+)',
            '\g<1>', adresse)

        while ville_adr[-1] in punctuation:
            ville_adr = ville_adr[:-1]
        while ville_adr[0] in punctuation:
            ville_adr = ville_adr[1:]

        num_adr = '\'' + num_adr.strip().upper() + '\''
        localite_adr = '\'' + localite_adr.strip().upper() + '\''
        nomRue_adr = '\'' + nomRue_adr.strip().upper() + '\''
        ville_adr = '\'' + ville_adr.strip().upper() + '\''
    pays_adr = '\'' + pays_adr.strip().upper() + '\''
    continent_adr = '\'' + continent_adr.strip().upper() + '\''
    return num_adr, localite_adr, nomRue_adr, cp_adr, ville_adr, pays_adr, continent_adr





# Fonction Main
if __name__ == '__main__':
    """
    Fonction Main
    """
    # Traitement des CV acceptés
    print('Traitement des CV acceptés')
    # Fichier de stockage des PDF que l'on veut traiter
    storage_file = './CV_ACCEPTE/'
    # Chargement des PDF

    import sys, fitz
    import numpy as np
    import os
    from os import listdir
    from os.path import isfile, join
    import codecs
    import re
    import string
    import unidecode
    import progress_bar
    import soundex
    from strsimpy.normalized_levenshtein import NormalizedLevenshtein
    import operator
    import uuid
    from random import *
    import pandas as pd
    import cv2
    from pdf2image import convert_from_path
    from datetime import datetime
    import locale
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
        output = re.sub(r'(?<=\b[a-zA-ZÉ]) (?=[a-zA-Z]\b)', '',
                        text)  # colle les lettre qui sont seul 'a b ' devient 'ab'
        output = re.sub(r'(?<=\b[0-9]) (?=[0-9]\b)', '', output)  # colle les chiffres qui sont seul '1 2 ' devient '12'
        output = output.replace('  ', ' ')  # remplace tous les double espace par un espace simple
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
            # Ouverture du CV
            doc = fitz.open(storage_file + pdf_file)
            # Pour chaque page du CV, on recupère tout le texte
            text = ""
            for page in doc:
                text = text + str(page.getText())
            tx = " ".join(text.split('\n'))
            tx = unidecode.unidecode(tx)
            # On traduit le texte en francais par ex: United Kingdom -> Royaume-Unis)
            tx = GoogleTranslator(source='auto', target='fr').translate(tx)
            # Extraction des informations des CV
            parser_text(storage_file, pdf_file, tx)
            # Progress bar pour voir l'évolution du processus
            progress_bar.print_progress_bar(compteur, taille,
                                            prefix='Extraction PDF : ' + str(compteur) + '/' + str(taille), suffix='')
            compteur = compteur + 1


    def parser_text(storage_file, pdf_file, text):
        """
        Fonction d'extraire l'information d'un PDF
        @params:
            storage_file   - Required  : Le fichier de stockage des PDF
            pdf_file        - Required  : Le nom du fichier PDF
            text            - Required  : Le contenu du fichier PDF
        """

        # Enlever les accents du text extrait du pdf
        text = unidecode.unidecode(text)
        # Définition des regexp
        regexp_mail = re.compile("[A-Za-z]+[A-Za-z0-9--\._]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,4}")

        regexp_tel = re.compile('(?:(?:\+|00)33|0)\s?[1-9](?:[\s.-]?\d{2}){4}')
        regexp_adresse = re.compile(
            '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+')
        regexp_age = re.compile('[0-9]{2,3} ANS')
        regexp_permis = re.compile(
            'PERMIS ?(?:DE CONDUIRE|TYPE)? ?:? ?(?:AM|BSR|A|A1|A2|B|B1|B2|BE|BVA|C|C1|CE|C1E|D|D1|D2|DE|DE1)')
        regexp_site_res = re.compile('(?:HTTP://|HTTPS://|HTTPS://)[A-Z0-9\.-=/]+')
        # Récupération du mail, tel, adresse, age, permis, sexe, site
        # Mail
        mail = re.findall(regexp_mail, text)
        if mail != []:
            mail = mail[0]
            mail = '\'' + mail + '\''
        else:
            mail = 'NULL'

        # Tel
        tel = re.findall(regexp_tel, text)
        if tel != []:
            tel = tel[0]
            tel = tel.replace(' ', '')
            tel = tel.replace('-', '')
            tel = tel.replace('.', '')
            tel = '\'' + tel + '\''
        else:
            tel = 'NULL'
        # Adresse
        adresse = re.findall(regexp_adresse, text.upper())
        if adresse != []:
            adresse = adresse[0]
        else:
            adresse = 'NULL'
        # Age
        age = re.findall(regexp_age, text.upper())
        if age != []:
            age = age[0]
            age = re.sub('([0-9]{2,3}) ANS', '\g<1>', age)
        else:
            age = 'NULL'
        # Permis
        listPermis = re.findall(regexp_permis, text.upper())
        permis = []
        for p in listPermis:
            if re.match(
                    'PERMIS ?(?:DE CONDUIRE|TYPE)? ?:? ?(?:AM|BSR|A|A1|A2|B|B1|B2|BE|BVA|C|C1|CE|C1E|D|D1|D2|DE|DE1)',
                    p):
                per = re.sub(
                    'PERMIS ?(?:DE CONDUIRE|TYPE)? ?:? ?((?:AM|BSR|A|A1|A2|B|B1|B2|BE|BVA|C|C1|CE|C1E|D|D1|D2|DE|DE1))',
                    '\g<1>', p)
                permis.append(per)
        # Sites/Réseaux
        site_res = re.findall(regexp_site_res, text.upper())

        # Récuperation du nom
        nom = 'NULL'
        if re.match('2020-12-03(?:-|_)CV(?:-|_)[A-Z]+(?:-|_)[A-Za-zéïàèîôû_\-]+.pdf', pdf_file):
            nom = re.sub('2020-12-03(?:-|_)CV(?:-|_)([A-Z]+)(?:-|_)([A-Za-zéïàèîôû_\-]+).pdf', '\g<1>', pdf_file)
            nom = '\'' + unidecode.unidecode(nom) + '\''

        # Récupération du prénom et du sexe (grâce à la base de Prénoms.csv qui contient le sexe associé au prénom)
        prenom = 'NULL'
        sexe = 'NULL'
        if re.match('2020-12-03(?:-|_)CV(?:-|_)[A-Z]+(?:-|_)[A-Za-zéïàèîôû_\-]+.pdf', pdf_file):
            prenom = re.sub('2020-12-03(?:-|_)CV(?:-|_)[A-Z]+(?:-|_)([A-Za-zéïàèîôû_\-]+).pdf', '\g<1>', pdf_file)
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

        tabFormation = extraire_formation(text)
        listCompetence = extraire_competence(text)
        listLangues = extraire_langue(text)
        listCentreInteret = extraire_centreInteret(text)
        adresse = unidecode.unidecode(adresse)
        nom = unidecode.unidecode(nom)
        mail = unidecode.unidecode(mail)
        # Appelle de la fonction pour creer les requetes d'insertions
        create_requete(storage_file, pdf_file, mail, tel, adresse, age, prenom, nom, sexe, permis, site_res, 'NULL',
                       'NULL', tabFormation, listCompetence, listLangues, listCentreInteret)


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


    def extraire_formation(text):

        # clean le texte du cv
        s = cleanText(text)
        tabFormation = []
        # pour formation
        # on utilise 2 méthode pour extraire les formation soit on coupe les bloc par date (on arrete le bloc quand une 3e data apparait)
        # soit on coupe les bloc par les mots de niveau comme master, licence, etc et on arrete le bloc quand un autre de ces mot apparait
        # et sinon les 2 méthodes arrete le bloc si une longueur est dépasse ou si les mots experience apparaissent
        # on compare quelle méthode trouve le plus de formation
        regex = r"(20[0-2][0-9]|19[0-9][0-9]).{0,5}(20[0-2][0-9]|19[0-9][0-9]).{0,200}?(?=(master|licence|Baccalaureat|dut|lycee|universite|ecole))(.{0,400}?(?=(20[0-2][0-9]|19[0-9][0-9]|Expérience|EXPERIENCE|experience|experience))|(.{0,200}))"
        matches = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
        compteur1 = 0
        for matchNum, match in enumerate(matches, start=1):
            compteur1 = compteur1 + 1

        regex2 = r"(Master|master|MASTER|Licence|LICENCE|licence|Baccalaureat)(.{0,400}?(?=(Master|master|MASTER|Licence|LICENCE|licence|Experience|EXPERIENCES|experience|experience|COMPETENCES|Competence|competence|Baccalaureat|EXPERIENCES|EXPERIENCE))|.{0,200})"
        matches = re.finditer(regex2, s, re.MULTILINE | re.IGNORECASE)

        compteur2 = 0
        for matchNum, match in enumerate(matches, start=1):
            compteur2 = compteur2 + 1
        # on utilise le regexp le plus performant a chaque fois

        if compteur1 >= compteur2:
            regex = regex
        else:
            regex = regex2
        matches = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
        compteur1 = 0
        # on analyse chaque formation trouvé

        for matchNum, match in enumerate(matches, start=1):
            compteur1 = compteur1 + 1
            formation = match.group()

            # expression reguliere pour extraire le niveau de la formation
            regexFormation = r"(master ?[1-2])|(licence|L1|L2|L3)|(baccalaureat|baccalaureat)|(DUT)"
            matchesFormation = re.finditer(regexFormation, formation, re.IGNORECASE)
            niveau = 'NULL'
            for matchNumFormation, matchFormation in enumerate(matchesFormation, start=1):
                niveau = "'" + matchFormation.group().strip() + "'"

                # expression reguliere pour extraire le nom de l'ecole
            ecole = "NULL"
            regexEcole = r"(Universite|lycee|ecole|college)[ ][a-z]*?[ ][a-z0-9]*"
            matchesEcole = re.finditer(regexEcole, formation, re.IGNORECASE)
            for matchNumEcole, matchEcole in enumerate(matchesEcole, start=1):
                ecole = "'" + matchEcole.group().strip() + "'"
                # expression reguliere pour extraire la date de debut et de fin de la formation
            dateDebut = "NULL"
            dateFin = "NULL"
            regexDate = r"((janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)[ ])?(20[0-2][0-9]|19[0-9][0-9])"
            matchesDate = re.finditer(regexDate, formation, re.MULTILINE | re.IGNORECASE)
            compteurDate = 0
            for matchNumDate, matchDate in enumerate(matchesDate, start=1):
                if matchNumDate == 1:
                    dateDebut = "'" + matchDate.group().strip() + "'"
                elif matchNumDate == 2:
                    dateFin = "'" + matchDate.group().strip() + "'"
                    # expression reguliere pour extraire la specialite de la formation
            specialite = "NULL"
            regexSpecialite = r"(informatique)"
            matchesSpecialite = re.finditer(regexSpecialite, formation, re.IGNORECASE)
            for matchNumEcole, matchSpecialite in enumerate(matchesSpecialite, start=1):
                specialite = "'" + matchSpecialite.group().strip() + "'"

                # out_file.write("EXEC INSERT_FORMATION("+ str(idFormation) +","+ niveau +","+ specialite +","+ ecole +","+  dateDebut +","+ dateFin +")\n")
            tabFormation.append([niveau, specialite, ecole, dateDebut, dateFin])

        return tabFormation


    def extraire_competence(text):
        # clean le texte du cv
        s = cleanText(text)
        regex = r"(Communication|réseautage|Esprit d equipe|Travail autonome|Capacité à travailler sous pression|marketing|rédaction|développement de contenu|Gestion du temps|Photoshop|Joomia|Indesign|Graphisme|Illustration|Photographie|Images animéees|Vidéographie|Mise en page|Ruby|Microsoft ASP.NET MVC.Web API|C#|éco-responsables|processus de recyclage|Conceptualisation des espaces 3D|Gestion de marque|Analyse des concurrents|Marketing sur les réseaux sociaux|Optimisation du moteur de recherche|Marketing de contenu|Recherche de marché|Rédacteur publicitaire|notions juridiques et financières|Rigueur|diplomatie|Travailleur social agréé|Association|action sociale|Sens de responsabilités|Travail en équipe|Flexible|Facilité dintégration|Sens de responsabilité|Autodidaxie|Créativité et force de proposition|Ambitieux|Organisé|Appliqué|Désireux dapprendre|Dynamique|Communication|adaptation facile|nouvelles technologies|Bénévole|Organisé|autonome|assidu|curieux|Travail en équipe|Persévérant|Adaptable|Communicant|Curiosité|Sérieux|Motivé|rigoureux|organisé|autonome|Bonne capacité danalyse|traitements de problématiques|Bonnes qualités rédactionnel|bonne approche des clients|Sens  négociation|Capacité dadaptation|Compétences relationnelles|Esprit déquipe|Travail en équipe|Respect des délais|Établir un cahier des charges|Capacité à sorganiser|Déterminé|curieuse|rigoureuse|aventures|Relationnel|Adaptabilité|Apprentissage|Rigueur|Autonomie|Travail en groupe|Travail sous pression|Autonome|Organisé|Rigoureux|Eclipse|NetBeans|AndroidStudio|Code:Blocks|Dev\-C\+\+|VisualStudio|STVisualdevelop|IDE|SASSoftware|SASViya|Jupyter|Linux|Ubuntu|NASM|Anaconda|Spyder|Talend|Tableau|BusinessObjects|SAS|Jira|Trello|jupyter-notebook|pycharm|Oracle|SasStudio|Mangodb|PowerBI|Talend|Tableau|Excel|Jupyter|Anaconda|Jupyter|spyder|KNIME|PhpMyAdmin|Colab|Dynamic|Dynamique|collaborative work|Collaboratif|Analyse critique|Ponctualité|Travail en groupe|Gestion de temps|Esprit d’analyse|Méticulosité|communication|Agile|Waterfal|Python|SQL|PL/SQL|SAS|Java|C|SQL|MATLAB|Python|Sql|Java|OcamlMatlab|UML|Haskell|SQL3|SAS|JavaScript|PHP|J2E|Pascal|HTML|CSS|XML|R|Java/JEE|OCaml|Mysql|Html|VBA|DATA warehouse|DateWarehouse|PHP5|Symfony|Angular9|SpringBoot|JEE|HTML5|CSS3|JS|JavaScript|pandas|numpy|matplotlib|seaborn|PLSQL|Ocaml|Scala|SQL|PLSQL|NoSQL|Prolog|SAS|Oracle|MongoDB|MySQL|Talend|Tableau|BusinessObjects|TensorFlow|Keras|Scikit-learn|Scikit-Fuzzy|MicrosoftOfficeExcel|Prolog|Oracle|MongoDB|MySQL|DataBase|Talend|DataIntegration|DataQuality|SAS|Tableau|BusinessObjects|HADOOP|HDFS|MapReduce|HBASE|SPARK|RSTUDIO|WEKA|IBMSPSSMODELER|REDIS|MongoDB|JupyterNotebook|Eclipse|SAS|VisualStudioCode|Rstudio|AndroidStudio|Git|Oracle|SASViya|SAS9|MangoDB|MATLAB|Oracle|BusinessObjects|MéthodeAgile|SCRUM|Trello|GitHub|oracle|PLSQL|SQLserver|SSIS|Trello|Word|Excel|PowerPoint|make|git|Oracle|SasStudio|PowerBI|Excel|Jupyter|ApacheKakfa|Elasticsearch|Logstash|Kibana|FileBeat|Trello|MarvenApp|Git|UML|Docker|SpringBoot|SpringData|SpringSecurity|HTML|Thymeleaf|CSS|VB|UML|GRASPpattern|Merise|Proto.io|Axure|Internet des objets|IOT|Business intelligence|Représentation graphique de données statistiques|Domotique|meetup tafterworks|Statistiques)"
        matches = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
        listecompetences = []
        competence = "null"

        for matchNum, match in enumerate(matches, start=1):
            competence = "'" + match.group().lower().strip() + "'"
            listecompetences.append(competence)

        setCompetence = set(listecompetences)  # transforme en set pour enlever doublon
        listCompetence = list(setCompetence)  # remet en liste

        return (listCompetence)


    def extraire_langue(text):
        s = cleanText(text)
        listLangue = []
        langue = "NULL"
        niveau = "NULL"
        regex = r"(français|francais|anglais|Allemand|Kabyle|Arabe|Chinois|mandarin|hindi|bengali|panjabi|Espagnol|Deutsch|Turc|Berbère|Wolof|Tamoul|italien|portuguais|russe|japonais|danois|polonais|javanais|telougou|malais|coreen|marathi|turc|vietnamien|tamoul|italien|persan|thai|gujarati|polonais|pachtou|kannada|malayalam|soundanais|oriya|birman|ukrainien|bhojpouri|filipino |yorouba|maithili|ouzbek|sindhi|amharique|peul|roumain|oromo|igbo |azéri|awadhi|visayan|neerlandais|kurde|malgache|saraiki|chittagonien|khmer|turkmène|assamais|madourais|somali|marwari|magahi|haryanvi|hongrois|chhattisgarhi|grec|chewa|deccan|akan|kazakh|sylheti|zoulou|tcheque)[ ](.*?[ ].*?[ ].*?[ ])"

        matches = re.finditer(regex, text, re.MULTILINE | re.IGNORECASE)

        for matchNum, match in enumerate(matches, start=1):
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                if (groupNum == 1):
                    langue = "'" + match.group(groupNum).strip() + "'"
                elif (groupNum == 2):
                    regexNiveau = r"(A1|B1|B2|C1|C2|langue maternelle|bilingue|débutant|avancé|HSK 3)"
                    matchesNiveau = re.finditer(regexNiveau, match.group(groupNum), re.IGNORECASE)
                    for matchNumNiveau, matchNiveau in enumerate(matchesNiveau, start=1):
                        niveau = "'" + matchNiveau.group().strip() + "'"
            listLangue.append([langue, niveau])
        return (listLangue)


    def extraire_centreInteret(text):
        # clean le texte du cv
        s = cleanText(text)

        regex = r"(Cyclisme|Patisserie|Lecture|Musique|Bricolages|Associations|Conférences|Mangas|Science|Jeux videos|Technologie|Physique|Philosophie|Travail Associatif|Planification|Entraînement physique|Transport et mobilité|technologies Web émergentes|Tennis de table|Bricolage|Voyage|Natation|handball|Engagement bénévole|Aviron|Boxe|Bénévolat|Photographie|Basketball|Football|cinéma|escalade|Photoshop|Tennis|SériesTV|Films|Art martiaux|musique|documentaire|Pâtisserie|volley-ball|bénévolat|Football|littérature|Cyclisme|Cuisiner|Hand-ball|Jeux cognitifs)"
        matches = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
        listeCentreInteret = []
        competence = "null"

        for matchNum, match in enumerate(matches, start=1):
            interet = "'" + match.group().lower().strip() + "'"
            listeCentreInteret.append(interet)

        setCentreInteret = set(listeCentreInteret)  # transforme en set pour enlever doublon
        listCentreInteret = list(setCentreInteret)  # remet en liste

        # print(listCentreInteret)
        return (listCentreInteret)


    def create_requete(storage_file, pdf_file, mail, tel, adresse, age, prenom, nom, sexe, permis, site_res, date_naiss,
                       nationalite, tabFormation, listCompetence, listLangues, listCentreInteret):
        """
        Fonction permettant de créer les requêtes d'insertion dans le fichier .sql
        La fonction va se charger de faire les modifications des données pour qu'elles collent aux insertions
        @params:
            storage_file   -Require : Le fichier de stockage des PDF
            pdf_file        -Require : Le nom du fichier PDF que l'on traite
            mail            -Require : Le mail du candidat
            tel             -Require : Le numéro de téléphone du candidat
            adresse         -Require : L'adresse du candidat
            age             -Require : L'âge du candidat
            prenom          -Require : Le prénom du candidat
            nom             -Require : Le nom de famille du candidat
            sexe            -Require : Le sexe du candidat
            permis          -Require : La liste des permis du candidat
            site_res        -Require : La liste des sites internets du candidat
            date_naiss      -Require : La date de naissance du candidat
            nationalite     -Require : La nationalité du candidat
            tabFormation    -Require : La liste des formations du candidat
            listCompetence  -Require : La liste des compétences du candidat
            listLangues     -Require : La liste des langues
        """
        # Normalisation des attributs
        sexe = sexe.strip().upper()
        nationalite = nationalite.strip().upper()
        adresse = adresse.strip().upper()
        mail = mail.strip().lower()
        # Ouverture du fichier csv
        ids = pd.read_csv('./ids_tables.txt', delimiter=',')

        # Récupération des identifiants disponibles
        id_can = ids['id_can'][0]
        id_adr = ids['id_adr'][0]
        id_cv = ids['id_cv'][0]
        id_site = ids['id_site'][0]

        new_id_can = int(id_can) + 1
        new_id_cv = int(id_cv) + 1

        if adresse == 'NULL':
            new_id_adr = int(id_adr)
            id_adr = 'NULL'
        else:
            new_id_adr = int(id_adr) + 1
            id_adr = '\'' + str(id_adr) + '\''

        # Insertion des id (pour éviter la redondance)
        ids = pd.DataFrame(
            {'id_adr': [new_id_adr], 'id_can': [new_id_can], 'id_cv': [new_id_cv], 'id_site': [int(id_site)]})
        ids.to_csv('./ids_tables.txt', index=False, header=True, mode='w')

        # On écrit dans le fichier de sortie .sql
        out_file = open('./G1_InsertDon_CV.sql', 'a')

        # Insertion Adresses
        if adresse != 'NULL':
            num_adr, localite_adr, nomRue_adr, cp_adr, ville_adr, pays_adr, continent_adr = eclater_adresse(adresse)
            out_file.write('EXEC INSERT_ADRESSES(' + str(
                id_adr) + ',' + num_adr + ',' + localite_adr + ',' + nomRue_adr + ',' + cp_adr + ',' + ville_adr + ',' + pays_adr + ',' + continent_adr + ');\n')
        # Insertion Candidats
        out_file.write('EXEC INSERT_CANDIDATS(\'' + str(id_can) + '\',' + str(
            id_adr) + ',' + nom + ',' + prenom + ',' + sexe + ',' + age + ',' + date_naiss + ',' + mail + ',' + nationalite + ',' + tel + ');\n')
        # Insertion Permis
        for p in permis:
            p = p.strip().upper()
            date_obtention = 'NULL'
            out_file.write(
                'EXEC INSERT_OBTENTIONPERMIS(\'' + p + '\',\'' + str(id_can) + '\',' + date_obtention + ');\n')
        # Insertion sites/Réseaux sociaux
        for s in site_res:
            id_site = ids['id_site'][0]
            new_id_site = int(id_site) + 1

            # Insertion des id (pour éviter la redondance)
            ids = pd.DataFrame(
                {'id_adr': [new_id_adr], 'id_can': [new_id_can], 'id_cv': [new_id_cv], 'id_site': [new_id_site]})
            ids.to_csv('./ids_tables.txt', index=False, header=True, mode='w')
            s = unidecode.unidecode(s)
            out_file.write(
                'EXEC INSERT_SITES_RESEAUX(\'' + str(id_site) + '\',\'' + str(id_can) + '\',\'' + s + '\');\n')
        # Insertion des langues
        for langue, niveau in listLangues:
            langue = langue.strip().upper()
            niveau = niveau.strip().upper()
            out_file.write('EXEC INSERT_RELATION_LANG_CAN(' + langue + ',\'' + str(id_can) + '\',' + niveau + ');\n')
        # Insertion CV
        titre_cv = 'NULL'
        description_cv = 'NULL'
        posteRecherche_cv = 'NULL'
        typePoste_cv = 'NULL'
        dispo_cv = 'NULL'
        admis = '\'' + 'ACCEPTE' + '\''
        if storage_file.lower().find('refuse') >= 0:
            admis = '\'' + 'REFUSE' + '\''
        date_transmission = 'SYSDATE'
        nom_cv = unidecode.unidecode(pdf_file)

        out_file.write('EXEC INSERT_CV(\'' + str(id_cv) + '\',\'' + str(
            id_can) + '\',\'' + nom_cv + '\',' + titre_cv + ',' + description_cv + ',' + posteRecherche_cv + ',' + typePoste_cv + ',' + dispo_cv + ',' + admis + ',' + date_transmission + ');\n')

        # Insertion Formations
        for formation in tabFormation:
            niveau = unidecode.unidecode(formation[0].strip().upper())
            specialite = unidecode.unidecode(formation[1].strip().upper())
            ecole = unidecode.unidecode(formation[2].strip().upper())
            out_file.write('EXEC INSERT_SUIT_FORMATIONS(' + ecole + ',' + niveau + ',' + specialite + ',\'' + str(
                id_can) + '\',' + convert_date(formation[3]) + ',' + convert_date(formation[4]) + ');\n')

        # Insertion Compétence
        for competence in listCompetence:
            competence = unidecode.unidecode(competence.strip().upper())
            catCpt = find_cat_cpt(competence)
            out_file.write(
                'EXEC INSERT_RELATION_COMP_CAN(' + competence + ',' + catCpt + ',\'' + str(id_can) + '\');\n')

        # Insertion Centre d'interêts
        for centreInteret in listCentreInteret:
            centreInteret = unidecode.unidecode(centreInteret.strip().upper())
            out_file.write('EXEC INSERT_RELATION_CENTINT_CAN(' + centreInteret + ',\'' + str(id_can) + '\');\n')

        out_file.close()
        # print(mail,tel,adresse,age,prenom,nom,sexe,permis,site_res)


    def find_cat_cpt(cpt):
        cpt = cpt[1:]
        cpt = cpt[:-1]
        cat_bdd = ['APPRENTISSAGE', 'SASSOFTWARE', 'SASVIYA', 'BUSINESS OBJECTS', 'BUSINESSOBJECTS', 'SQL', 'ORACLE',
                   'JAVA/JEE', 'SQL3', 'MYSQL', 'DATA WAREHOUSE', 'PLSQL', 'NOSQL', 'MONGODB', 'DATABASE',
                   'DATA INTEGRATION', 'DATAQUALITY', 'SQLSERVER', 'SPRINGBOOT', 'SPRINGDATA', 'SPRINGSECURITY',
                   'BUSINESS INTELLIGENCE', 'TABLEAU', 'REPRESENTATION GRAPHIQUE DE DONNEES STATISTIQUES',
                   'MEETUP TAFTERWORKS']
        cat_comp = ['INTERNET DES OBJETS', ' IOT']
        cat_web = ['DEVELOPPEMENT DE CONTENU', 'PHPMYADMIN', 'JAVASCRIPT', 'PHP', 'J2E', 'HTML', 'CSS', 'XML', 'PHP5',
                   'SYMFONY', 'JS', 'CSS3', 'JAVASCRIPT']
        cat_lang = ['C', 'SAS', 'PYTHON', 'JAVA', 'R', 'C++', 'C#', 'MATLAB', 'OCAML', 'UML', 'HASKELL', 'SCALA']
        cat_crea = ['PHOTOSHOP', 'PHOTOGRAPHIE', 'VIDEOGRAPHIE', 'CREATIVITE']
        cat_se = ['LINUX', 'MACOS', 'WINDOWS', 'UBUNTU', 'DEBIAN']
        cat_outil = ['NETBEANS', 'ANDROIDSTUDIO', 'CODE:BLOCKS', 'VISUALSTUDIO', 'STVISUALDEVELOP', 'JUPYTER',
                     'ANACONDA', 'SPYDER', 'TALEND', 'JIRA', 'TRELLO', 'JUPYTER-NOTEBOOK', 'SASSTUDIO', 'EXCEL',
                     'KNIME', 'COLAB', 'MICROSOFTOFFICEEXCEL', 'PANDAS', 'NUMPY', 'SCIKIT-LEARN', 'SCIKIT-FUZZY',
                     'HADOOP', 'SPARK', 'RSTUDIO', 'JUPYTERNOTEBOOK', 'ECLIPSE', 'STUDIOCODE', 'GIT', 'SASVIYA',
                     'METHODEAGILE', 'GITHUB', 'POWERPOINT', 'APACHEKAKFA', 'DOMOTIQUE', 'WORD', 'EXCEL',
                     'MICROSOFT ASP.NET MVC.WEB API']
        cat_softSkill = ['BENEVOLE', 'ANALYSE DES CONCURRENTS', 'COMMUNICATION', 'RESEAUTAGE', 'ESPRIT D EQUIPE',
                         'TRAVAIL AUTONOME', 'CAPACITE A TRAVAILLER SOUS PRESSION', 'GESTION DU TEMPS',
                         'RECHERCHE DE MARCHE', 'FACILITE DINTEGRATION', 'DIPLOMATIE', 'TRAVAILLEUR SOCIAL AGREE',
                         'AUTODIDAXIE', 'ORGANISE', 'APPLIQUE', 'DYNAMIQUE', 'AGILE', 'ASSOCIATION', 'ACTION SOCIALE',
                         'SENS DE RESPONSABILITÉS', 'TRAVAIL EN EQUIPE', 'FLEXIBLE', 'COMMUNICATION',
                         'ADAPTATION FACILE', 'CAPACITE DADAPTATION', 'CURIEUX', 'TRAVAIL EN EQUIPE', 'ADAPTABLE',
                         'COMMUNICANT', 'SERIEUX', 'MOTIVE', 'RIGOUREUX', 'BONNE APPROCHE DES CLIENTS',
                         'SENS  NEGOCIATION', 'COMPETENCES RELATIONNELLES', 'ESPRIT DEQUIPE', 'TRAVAIL EN EQUIPE',
                         ' RESPECT DES DELAIS', 'ETABLIR UN CAHIER DES CHARGES', 'CAPACITE À SORGANISER', 'DETERMINE',
                         'CURIEUSE', 'RIGOUREUSE', 'AVENTURES', 'RELATIONNEL', 'ADAPTABILITE', 'RIGUEUR', 'AUTONOMIE',
                         'TRAVAIL EN GROUPE', 'TRAVAIL SOUS PRESSION', 'ECLIPSE', 'DYNAMIC', 'DYNAMIQUE',
                         'COLLABORATIVE WORK', 'COLLABORATIF', 'PONCTUALITE', 'TRAVAIL EN GROUPE', 'GESTION DE TEMPS',
                         'ESPRIT D’ANALYSE']
        if cpt.upper() in cat_bdd:
            return '\'' + 'BASE DE DONNEES' + '\''
        elif cpt.upper() in cat_lang:
            return '\'' + 'LANGAGE DE PROGRAMMATION' + '\''
        elif cpt.upper() in cat_comp:
            return '\'' + 'ELECTRONIQUE' + '\''
        elif cpt.upper() in cat_crea:
            return '\'' + 'CREATIVITE' + '\''
        elif cpt.upper() in cat_web:
            return '\'' + 'WEB' + '\''
        elif cpt.upper() in cat_se:
            return '\'' + 'SYSTEME EXPLOITATION' + '\''
        elif cpt.upper() in cat_outil:
            return '\'' + 'OUTILS' + '\''
        elif cpt.upper() in cat_softSkill:
            return '\'' + 'SOFTSKILLS' + '\''
        else:
            return 'NULL'


    def convert_date(date):
        """
        Fonction permettant de convertir les dates dans le format souhaité
        @params:
            date -Require : La date
        @return
            date : La date dans le bon format
        """
        # On se met en français
        dateNorm = date[1:][:-1].lower()
        if re.match('(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre) ([0-9]{4})',
                    dateNorm):
            if re.match('decembre [0-9]+', dateNorm):
                an = re.sub('decembre ([0-9]+)', '\g<1>', dateNorm)
                dateNorm = 'décembre ' + an
            elif re.match('fevrier [0-9]+', dateNorm):
                an = re.sub('fevrier ([0-9]+)', '\g<1>', dateNorm)
                dateNorm = 'février ' + an
            elif re.match('aout [0-9]+', dateNorm):
                an = re.sub('aout ([0-9]+)', '\g<1>', dateNorm)
                dateNorm = 'août ' + an
            locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
            # On récupère convertie la date en format numrique en supprimant les apostrophes en début et fin de date
            dateConvert = datetime.strptime(dateNorm, '%B %Y')
            # On crée la date
            date = '\'' + str(dateConvert.day) + '/' + str(dateConvert.month) + '/' + str(dateConvert.year) + '\''
        elif re.match('([0-9]{4})', dateNorm):
            locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
            # On récupère convertie la date en format numrique en supprimant les apostrophes en début et fin de date
            dateConvert = datetime.strptime(dateNorm, '%Y')
            # On crée la date
            date = '\'' + str(dateConvert.day) + '/' + str(dateConvert.month) + '/' + str(dateConvert.year) + '\''

        date = date.strip().upper()
        return date


    # Fonction permettant de séprarer les différents attributs d'une adresse
    def eclater_adresse(adresse):
        """
        Fonction permettant de scinder l'adresse
        @params:
            adresse         - Required  : L'adresse à scinder
        @return:
            num_adr         : Le numéro de la voie ou NULL
            localite_adr    : Le type de la voie ou NULL
            nomRue_adr      : Le nom de la rue ou NULL
            cp_adr          : Le code postal de la ville ou NULL
            ville_adr       : Le nom de la ville ou NULL
            pays_adr        : Le nom du pays
            continent_adr   : Le nom du contient
        """
        punctuation = ['(', ')', '?', ':', ';', ',', '.', '!', '/', '-', "_"]
        num_adr = 'NULL'
        localite_adr = 'NULL'
        nomRue_adr = 'NULL'
        cp_adr = 'NULL'
        ville_adr = 'NULL'
        pays_adr = 'FRANCE'
        continent_adr = 'EUROPE'
        if re.match(
                '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',
                adresse):
            num_adr = re.sub(
                '([0-9]+)(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',
                '\g<1>', adresse)
            cpl_adr = re.sub(
                '[0-9]+((?:BIS|TER)?),? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',
                '\g<1>', adresse)
            num_adr = num_adr + cpl_adr
            localite_adr = re.sub(
                '[0-9]+(?:BIS|TER)?,? ?((?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS)) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',
                '\g<1>', adresse)
            nomRue_adr = re.sub(
                '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) ([A-Z ]+),? ?(?:[0-9]{5}| )? [A-Z\-]+',
                '\g<1>', adresse)
            cp_adr = re.sub(
                '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?((?:[0-9]{5}| ))? [A-Z\-]+',
                '\g<1>', adresse)
            if cp_adr == '':
                cp_adr = 'NULL'
            else:
                cp_adr = '\'' + cp_adr.strip().upper() + '\''
            ville_adr = re.sub(
                '[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? ([A-Z\-]+)',
                '\g<1>', adresse)

            while ville_adr[-1] in punctuation:
                ville_adr = ville_adr[:-1]
            while ville_adr[0] in punctuation:
                ville_adr = ville_adr[1:]

            num_adr = '\'' + num_adr.strip().upper() + '\''
            localite_adr = '\'' + localite_adr.strip().upper() + '\''
            nomRue_adr = '\'' + nomRue_adr.strip().upper() + '\''
            ville_adr = '\'' + ville_adr.strip().upper() + '\''
        pays_adr = '\'' + pays_adr.strip().upper() + '\''
        continent_adr = '\'' + continent_adr.strip().upper() + '\''
        return num_adr, localite_adr, nomRue_adr, cp_adr, ville_adr, pays_adr, continent_adr



    # Fonction Main
    if __name__ == '__main__':
        """
        Fonction Main
        """
        # Traitement des CV acceptés
        print('Traitement des CV acceptés')
        # Fichier de stockage des PDF que l'on veut traiter
        storage_file = './CV_ACCEPTE/'
        # Chargement des PDF

        list_pdf_files = [f for f in listdir(storage_file) if isfile(join(storage_file, f))]

        # Extraction de l'informations des PDF et création des requetes SQL dans les fichiers SQL
        extract_text_pdf(storage_file, list_pdf_files)

        print('Extraction des PDF terminée, vous pouvez lancer les fichiers SQL (.sql)')

