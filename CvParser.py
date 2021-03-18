import fitz

from os import listdir
from os.path import isfile, join
import re
import unidecode
import pandas as pd
from deep_translator import GoogleTranslator
import regx


def cleanText(text):
    output = re.sub(r'(?<=\b[a-zA-ZÉ]) (?=[a-zA-Z]\b)', '', text)  # colle les lettre qui sont seul 'a b ' devient 'ab'
    output = re.sub(r'(?<=\b[0-9]) (?=[0-9]\b)', '', output)  # colle les chiffres qui sont seul '1 2 ' devient '12'
    output = output.replace('  ', ' ')  # remplace tous les double espace par un espace simple
    return output


def read_pdf(storage_directory, pdf_files):
    # Fonction permettant de gérer l'extraction d'information des PDF

    # taille = len(pdf_files)
    # compteur = 1

    for pdf_file in pdf_files:

        # Lecture du CV
        doc = fitz.open(storage_directory + pdf_file)

        # on recupère tout le texte
        content = ""
        for page in doc:
            content = content + str(page.getText())

        # élimine les retour à la ligne
        tx = " ".join(content.split('\n'))

        # On Supprime les caractères non désirable
        tx = unidecode.unidecode(tx)

        # On traduit le texte en francais
        tx = GoogleTranslator(source='auto', target='fr').translate(tx)

        # Extraction des informations des CV
        parse_string(storage_directory, pdf_file, tx)

        # compteur = compteur + 1


def parse_string(storage_directory, pdf_file, text):
    """
    Fonction d'extraire l'information d'un PDF
    """

    # Enlever les accents du text extrait du pdf
    text = unidecode.unidecode(text)
    mail = regx.findMail(text)
    tel = regx.findPhone(text)
    adresse = regx.findAdresse(text)
    age = regx.findAge(text)
    permis = regx.findDriverlicence(text)
    nom  = regx.findName(pdf_file)
    prenom  = regx.findPrenom(pdf_file,mail)

    sexe = regx.findSexe(prenom)

    tabFormation = extraire_formation(text)
    tabExperience = get_experiences(text)
    listCompetence = competenceExtraction(text)
    listLangues = extraire_langue(text)
    listCentreInteret = extraire_centreInteret(text)
    adresse = unidecode.unidecode(adresse)
    nom = unidecode.unidecode(nom)
    mail = unidecode.unidecode(mail)
    # Appelle de la fonction pour creer les requetes d'insertions
    create_requete(storage_directory, pdf_file, mail, tel, adresse, age, prenom, nom, sexe, permis, 'NULL', 'NULL',
                   tabFormation, tabExperience, listCompetence, listLangues, listCentreInteret)



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

        tabFormation.append([niveau, specialite, ecole, dateDebut, dateFin])

    return tabFormation


def competenceExtraction(data):
    cleanedData = cleanText(data)

    extracted = re.finditer(
        r"(Communication|réseautage|Esprit d equipe|Travail autonome|Capacité à travailler sous pression|marketing|rédaction|développement de contenu|Gestion du temps|Photoshop|Joomia|Indesign|Graphisme|Illustration|Photographie|Images animéees|Vidéographie|Mise en page|Ruby|Microsoft ASP.NET MVC.Web API|C#|éco-responsables|processus de recyclage|Conceptualisation des espaces 3D|Gestion de marque|Analyse des concurrents|Marketing sur les réseaux sociaux|Optimisation du moteur de recherche|Marketing de contenu|Recherche de marché|Rédacteur publicitaire|notions juridiques et financières|Rigueur|diplomatie|Travailleur social agréé|Association|action sociale|Sens de responsabilités|Travail en équipe|Flexible|Facilité dintégration|Sens de responsabilité|Autodidaxie|Créativité et force de proposition|Ambitieux|Organisé|Appliqué|Désireux dapprendre|Dynamique|Communication|adaptation facile|nouvelles technologies|Bénévole|Organisé|autonome|assidu|curieux|Travail en équipe|Persévérant|Adaptable|Communicant|Curiosité|Sérieux|Motivé|rigoureux|organisé|autonome|Bonne capacité danalyse|traitements de problématiques|Bonnes qualités rédactionnel|bonne approche des clients|Sens  négociation|Capacité dadaptation|Compétences relationnelles|Esprit déquipe|Travail en équipe|Respect des délais|Établir un cahier des charges|Capacité à sorganiser|Déterminé|curieuse|rigoureuse|aventures|Relationnel|Adaptabilité|Apprentissage|Rigueur|Autonomie|Travail en groupe|Travail sous pression|Autonome|Organisé|Rigoureux|Eclipse|NetBeans|AndroidStudio|Code:Blocks|Dev\-C\+\+|VisualStudio|STVisualdevelop|IDE|SASSoftware|SASViya|Jupyter|Linux|Ubuntu|NASM|Anaconda|Spyder|Talend|Tableau|BusinessObjects|SAS|Jira|Trello|jupyter-notebook|pycharm|Oracle|SasStudio|Mangodb|PowerBI|Talend|Tableau|Excel|Jupyter|Anaconda|Jupyter|spyder|KNIME|PhpMyAdmin|Colab|Dynamic|Dynamique|collaborative work|Collaboratif|Analyse critique|Ponctualité|Travail en groupe|Gestion de temps|Esprit d’analyse|Méticulosité|communication|Agile|Waterfal|Python|SQL|PL/SQL|SAS|Java|C|SQL|MATLAB|Python|Sql|Java|OcamlMatlab|UML|Haskell|SQL3|SAS|JavaScript|PHP|J2E|Pascal|HTML|CSS|XML|R|Java/JEE|OCaml|Mysql|Html|VBA|DATA warehouse|DateWarehouse|PHP5|Symfony|Angular9|SpringBoot|JEE|HTML5|CSS3|JS|JavaScript|pandas|numpy|matplotlib|seaborn|PLSQL|Ocaml|Scala|SQL|PLSQL|NoSQL|Prolog|SAS|Oracle|MongoDB|MySQL|Talend|Tableau|BusinessObjects|TensorFlow|Keras|Scikit-learn|Scikit-Fuzzy|MicrosoftOfficeExcel|Prolog|Oracle|MongoDB|MySQL|DataBase|Talend|DataIntegration|DataQuality|SAS|Tableau|BusinessObjects|HADOOP|HDFS|MapReduce|HBASE|SPARK|RSTUDIO|WEKA|IBMSPSSMODELER|REDIS|MongoDB|JupyterNotebook|Eclipse|SAS|VisualStudioCode|Rstudio|AndroidStudio|Git|Oracle|SASViya|SAS9|MangoDB|MATLAB|Oracle|BusinessObjects|MéthodeAgile|SCRUM|Trello|GitHub|oracle|PLSQL|SQLserver|SSIS|Trello|Word|Excel|PowerPoint|make|git|Oracle|SasStudio|PowerBI|Excel|Jupyter|ApacheKakfa|Elasticsearch|Logstash|Kibana|FileBeat|Trello|MarvenApp|Git|UML|Docker|SpringBoot|SpringData|SpringSecurity|HTML|Thymeleaf|CSS|VB|UML|GRASPpattern|Merise|Proto.io|Axure|Internet des objets|IOT|Business intelligence|Représentation graphique de données statistiques|Domotique|meetup tafterworks|Statistiques)",
        cleanedData,
        re.MULTILINE | re.IGNORECASE 
    )
    competences = []
    for value in extracted:
        if "'" + value.group().lower().strip() + "'" not in competences: #pour ne pas insérer des doublons dans la liste
            competences.append("'" + value.group().lower().strip() + "'")
    return competences



def extraire_langue(text):
    s = cleanText(text)
    listLangue = []
    langue = "NULL"
    niveau = "NULL"


    r = '('

    fichier = open("Langues_1.csv", "r")
    for line in fichier:
        s = line.split(';')[0]
        cats = s.split("\n")
        r = r + cats[0] + "|"
    fichier.close()

    reg = r[0:len(r) - 1] +  r')[ ](.*?[ ].*?[ ].*?[ ])'

    matches = re.finditer(reg, text, re.MULTILINE | re.IGNORECASE)

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
    # clean le texte du cvManga
    s = cleanText(text)

    r = "("
    fichier = open("Loisirs.csv", "r")
    for line in fichier:
        s = line.split(';')[0]
        cats = s.split("\n")
        r = r + cats[0] + "|"
    fichier.close()

    reg = r[0:len(r)-1]
    reg = reg + ")"

    matches = re.finditer(reg, s, re.MULTILINE | re.IGNORECASE)
    listeCentreInteret = []
    competence = "null"

    for matchNum, match in enumerate(matches, start=1):
        interet = "'" + match.group().lower().strip() + "'"
        listeCentreInteret.append(interet)

    setCentreInteret = set(listeCentreInteret)  # transforme en set pour enlever doublon
    listCentreInteret = list(setCentreInteret)  # remet en liste

    return (listCentreInteret)


def get_experiences(text):
    s = cleanText(text)
    # regEXp = r"(EXPERIENCES PROFESSIONNELLES)(.*?)(LANGUES)"
    # results = re.finditer(regEXp, s, re.MULTILINE | re.IGNORECASE)
    s = re.search(r"EXPERIENCES PROFESSIONNELLES(.*)LANGUES", s, re.MULTILINE | re.IGNORECASE).group(1)

    regex = r"((janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)[ ])(20[0-2][0-9]|19[0-9][0-9])(.{0,30}?)(STAGE)(.{0,100}?)((janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)[ ])?(20[0-2][0-9]|19[0-9][0-9])"

    matches1 = re.finditer(regex, s, re.MULTILINE | re.IGNORECASE)
    compteur1 = 0

    regexDate = r"((janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)[ ])?(20[0-2][0-9]|19[0-9][0-9])"

    listexp1 = []
    for matchNum, match in enumerate(matches1, start=1):
        # print("match ",match.group(6).strip()) #4  #6
        element = []
        dateDebut1 = "NULL"
        dateFin1 = "NULL"
        title1 = "NULL"
        firm1 = "NULL"
        compteur1 = compteur1 + 1
        title1 = "'" + match.group(4).strip() + "'"
        firm1 = "'" + re.search(r"chez(.*)", match.group(6).strip(), re.MULTILINE | re.IGNORECASE).group(1).replace("'", ' ') + "'"
        matchesDate = re.finditer(regexDate, match.group().strip(), re.MULTILINE | re.IGNORECASE)
        compteurDate = 0
        # print(" title ", title1)
        # print(" firm ", firm1)
        for matchNumDate, matchDate in enumerate(matchesDate, start=1):
            if matchNumDate == 1:
                dateDebut1 = "'" + matchDate.group().strip() + "'"
            elif matchNumDate == 2:
                dateFin1 = "'" + matchDate.group().strip() + "'"
        element.append(dateDebut1)
        element.append(dateFin1)
        element.append(title1)
        element.append(firm1)
        listexp1.append(element)
        # print("start ",dateDebut1)
        # print("end ",dateFin1)
    listexp2 = []
    regx2 = r"(stage)(.*?)(((janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)[ ])?(20[0-2][0-9]|19[0-9][0-9]))"
    matches2 = re.finditer(regx2, s, re.MULTILINE | re.IGNORECASE)
    compteur2 = 0
    for matchNum, match in enumerate(matches2, start=1):
        element = []
        dateDebut2 = "NULL"
        dateFin2 = "NULL"
        title2 = "NULL"
        firm2 = "NULL"
        result = re.search(r"(.*)(chez)(.*)", match.group(2).strip(), re.MULTILINE | re.IGNORECASE)
        firm2 = "'" + result.group(3).replace("'", ' ') + "'"
        title2 = "'" + result.group(1) + "'"
        compteur2 = compteur2 + 1
        matchesDate = re.finditer(regexDate, match.group().strip(), re.MULTILINE | re.IGNORECASE)
        compteurDate = 0
        for matchNumDate, matchDate in enumerate(matchesDate, start=1):
            if matchNumDate == 1:
                dateDebut2 = "'" + matchDate.group().strip() + "'"
            elif matchNumDate == 2:
                dateFin2 = "'" + matchDate.group().strip() + "'"
        element.append(dateDebut2)
        element.append(dateFin2)
        element.append(title2)
        element.append(firm2)
        listexp2.append(element)

    reg = 0
    if compteur1 >= compteur2:
        explist = listexp1
    else:
        explist = listexp2

    return (explist)


def create_requete(storage_file, pdf_file, mail, tel, adresse, age, prenom, nom, sexe, permis, date_naiss,
                   nationalite, tabFormation,tabExperience ,listCompetence, listLangues, listCentreInteret):
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
    id_dipl = ids['id_dipl'][0]
    id_formation = ids['id_formation'][0]
    id_compet = ids['id_compet'][0]
    id_lang = ids['id_lang'][0]
    id_loisir = ids['id_loisir'][0]
    id_ecole = ids['id_ecole'][0]
    id_etabl = ids['id_etablissement'][0]
    idExp = ids['idExp'][0]


    new_id_can = int(id_can) + 1
    new_id_cv = int(id_cv) + 1
    new_id_dipl = int(id_dipl) + 1
    new_id_formation = int(id_formation) + 1


    if adresse == 'NULL':
        new_id_adr = int(id_adr)
        id_adr = 'NULL'
    else:
        new_id_adr = int(id_adr) + 1
        id_adr = '\'' + str(id_adr) + '\''



    # Insertion des id (pour éviter la redondance)
    ids = pd.DataFrame(
        {'id_adr': [new_id_adr], 'id_can': [new_id_can], 'id_cv': [new_id_cv] , 'id_formation' : [new_id_formation],
         'id_compet' :[int(id_compet) + 1], 'id_lang' : [int(id_lang) + 1],'id_loisir' : [int(id_loisir) + 1] , 'id_ecole' : [int(id_ecole) + 1], 'id_etablissement' : [int(id_etabl) + 1],  'idExp' : [int(idExp) + 1]})
    ids.to_csv('./ids_tables.txt', index=False, header=True, mode='w')

    # On écrit dans le fichier de sortie .sql
    out_file = open('./G1_InsertDon_CV.sql', 'a')

    # Insertion Adresses
    if adresse != 'NULL':
        num_adr, localite_adr, nomRue_adr, cp_adr, ville_adr, pays_adr, continent_adr = eclater_adresse(adresse)
    # # Insertion Permis

    nomm = nom.split("'")
    nomPers = nomm[1];

    prenomm = prenom.split("'")
    prenomPers = prenomm[1];



    photo = "'" +  "2020-12-10-PH_" + nomPers + "_" + prenomPers + ".jpg"+"'"
    CV = "'" +  "2020-12-03-CV_" + nomPers + "_" + prenomPers + ".jpg"+"'"


    if permis:
        permi = "'"+ permis[0] + "'"
    else:
        permi = "'NULL'"

    out_file.write('EXEC INSERT_Candidats(' + str(id_can) + ',' + nom + ',' + prenom + ',' + date_naiss + ',' + tel
                   + ',' + mail + ',' + num_adr + ',' + nomRue_adr + ',' + ville_adr + ',' + pays_adr + ',' + cp_adr
                   + ',' + permi + ',' + sexe + ','  + CV + ',' + photo +');\n')






    # Insertion sites/Réseaux sociaux

        # Insertion des id (pour éviter la redondance)
    ids = pd.DataFrame(
            {'id_adr': [new_id_adr], 'id_can': [new_id_can], 'id_cv': [new_id_cv]})
    ids.to_csv('./ids_tables.txt', index=False, header=True, mode='w')

    newlist3 = []
    # Insertion des langues
    for langue, niveau in listLangues:
        langue = langue.strip().upper()
        niveau = niveau.strip().upper()

        if langue not in newlist3:
            newlist3.append(langue)
            id_lang = id_lang + 1
            out_file.write('EXEC INSERT_Langues(' + str(id_lang) + ',' + langue +');\n')
            out_file.write('EXEC INSERT_LanguesCandidat(' + str(id_can) + ',' + str(id_lang) + ',' + niveau+ ');\n')

    new_listEtabProf = []
    for experience in tabExperience:
        dateDeb = unidecode.unidecode(experience[0].strip().upper())
        dateFin = unidecode.unidecode(experience[1].strip().upper())
        Titre = unidecode.unidecode(experience[2].strip().upper())
        etablissement = unidecode.unidecode(experience[3].strip().upper())
        idExp = idExp + 1

        if etablissement != 'NULL':
            if etablissement not in new_listEtabProf:
                id_etabl = id_etabl + 1
                new_listEtabProf.append(etablissement)
                out_file.write('EXEC INSERT_EtablissementProfessionnelle(' + str(id_etabl) + ',' + etablissement + ');\n')
                out_file.write('EXEC INSERT_ExperiencesProfessionnelles(' + str(idExp) + ',' + Titre + ','+ str(id_etabl) + ');\n')
                out_file.write('EXEC INSERT_EtablissementProCandidat(' + str(id_etabl)  + ','+ str(id_can) +',' + dateDeb + ',' + dateFin + ');\n')

            else:
                out_file.write(
                    'EXEC INSERT_EtablissementProfessionnelle(' + str(id_etabl) + ',' + etablissement + ');\n')
                out_file.write('EXEC INSERT_ExperiencesProfessionnelles(' + str(idExp) + ',' + Titre + ',' + str(
                    id_etabl) + ');\n')
                out_file.write('EXEC INSERT_EtablissementProCandidat(' + str(id_etabl) + ',' + str(
                    id_can) + ',' + dateDeb + ',' + dateFin + ');\n')

    new_list = []
    new_listEcole = []

    for formation in tabFormation:
        niveau = unidecode.unidecode(formation[0].strip().upper())
        specialite = unidecode.unidecode(formation[1].strip().upper())
        ecole = unidecode.unidecode(formation[2].strip().upper())
        if specialite != 'NULL' :
            if specialite not in new_list:
                id_dipl = id_dipl + 1
                new_list.append(specialite)
                out_file.write('EXEC INSERT_Diplomes(' + str(id_dipl) + ',' + specialite + ');\n')

            if ecole not in new_listEcole:
                new_listEcole.append(ecole)
                id_ecole = id_ecole  + 1 ;

            out_file.write(
                'EXEC INSERT_Formations(' + str(id_formation) + ',' + specialite  + ',' + niveau + ',' + str(id_dipl) + ',' + str(id_ecole)
                     + ');\n')

            out_file.write(
                'EXEC INSERT_EtablissementPedaCandidat(' + str(id_ecole) + ',' + str(id_can) + ',' + formation[3] + ',' +formation[4] + ');\n')

            if ecole == 'NULL':
                out_file.write(
                    'EXEC INSERT_EtablissementPedagogique(' + str(id_ecole) + ',' + "'DetailsEtablissement'" + ','+ "'OTHER'" + ',' +"'OTHER'"+ ',' + "'OTHER'" + ');\n')
            else:
                out_file.write(
                    'EXEC INSERT_EtablissementPedagogique(' + str(
                        id_ecole) + ',' + "'DetailsEtablissement'" + ',' + ecole + ',' + "'OTHER'" + ',' + "'OTHER'" + ');\n')

    # Insertion Compétence
    new_list2 = []


    for competence in listCompetence:
        competence = unidecode.unidecode(competence.strip().upper())
        if competence not in new_list2:
            new_list2.append(competence)
            id_compet  = id_compet + 1

            catCpt = regx.findCompetenceCat(competence)
           # catCpt = find_cat_cpt(competence)
            out_file.write('EXEC INSERT_Competences('+ str(id_compet) + ','+ competence + ',' + catCpt + ');\n')
            out_file.write('EXEC INSERT_CompetencesCandidat('+ str(id_compet) + ','+ str(id_can) + ');\n')


    # Insertion Centre d'interêts
    for centreInteret in listCentreInteret:
        centreInteret = unidecode.unidecode(centreInteret.strip().upper())
        if centreInteret not in new_list2:
            new_list2.append(centreInteret)
            id_loisir = id_loisir + 1
            out_file.write('EXEC INSERT_Loisirs(' + str(id_loisir)+ ',' + centreInteret +');\n')
            out_file.write('EXEC INSERT_LoisirsCandidat('+ str(id_loisir) + ','+ str(id_can) + ');\n')


    out_file.close()

# Insertion des id (pour éviter la redondance)
    ids = pd.DataFrame(
        {'id_adr': [new_id_adr], 'id_can': [new_id_can], 'id_cv': [new_id_cv] , 'id_formation' : [new_id_formation],
         'id_compet' :[int(id_compet) + 1], 'id_lang' : [int(id_lang) + 1],'id_loisir' : [int(id_loisir) + 1], 'id_dipl' : [int(id_dipl) + 1], 'id_ecole' : [int(id_ecole) + 1] , 'id_etablissement' : [int(id_etabl) + 1],  'idExp' : [int(idExp) + 1]})
    ids.to_csv('./ids_tables.txt', index=False, header=True, mode='w')



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
    print('BEGIN')

    storage_file = './CV_ACCEPTE/'

    list_pdf_files = [f for f in listdir(storage_file) if isfile(join(storage_file, f))]
    read_pdf(storage_file, list_pdf_files)

    print('WORK DONE ! ')