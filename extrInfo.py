import re
import unidecode
import parseCV

def corr_prenom(prenom):
    prenom = unidecode.unidecode(prenom)
    prenom = prenom.replace('_',' ')
    prenom = prenom.replace('-',' ')
    listPrenom = prenom.split()
    prenom = ''
    for p in listPrenom:
        pre = p.capitalize()
        prenom = prenom + ' ' + pre
    prenom = prenom.strip()
    prenom = prenom.replace(' ','-')
    return prenom

def extraire_formation(text):
    # clean le texte du cv
    s = ParseCV.cleanText(text)
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

def competenceExtraction(data):
    cleanedData = ParseCV.cleanText(data)

    extracted = re.finditer(
        r"(Communication|réseautage|Esprit d equipe|Travail autonome|Capacité à travailler sous pression|marketing|rédaction|développement de contenu|Gestion du temps|Photoshop|Joomia|Indesign|Graphisme|Illustration|Photographie|Images animéees|Vidéographie|Mise en page|Ruby|Microsoft ASP.NET MVC.Web API|C#|éco-responsables|processus de recyclage|Conceptualisation des espaces 3D|Gestion de marque|Analyse des concurrents|Marketing sur les réseaux sociaux|Optimisation du moteur de recherche|Marketing de contenu|Recherche de marché|Rédacteur publicitaire|notions juridiques et financières|Rigueur|diplomatie|Travailleur social agréé|Association|action sociale|Sens de responsabilités|Travail en équipe|Flexible|Facilité dintégration|Sens de responsabilité|Autodidaxie|Créativité et force de proposition|Ambitieux|Organisé|Appliqué|Désireux dapprendre|Dynamique|Communication|adaptation facile|nouvelles technologies|Bénévole|Organisé|autonome|assidu|curieux|Travail en équipe|Persévérant|Adaptable|Communicant|Curiosité|Sérieux|Motivé|rigoureux|organisé|autonome|Bonne capacité danalyse|traitements de problématiques|Bonnes qualités rédactionnel|bonne approche des clients|Sens  négociation|Capacité dadaptation|Compétences relationnelles|Esprit déquipe|Travail en équipe|Respect des délais|Établir un cahier des charges|Capacité à sorganiser|Déterminé|curieuse|rigoureuse|aventures|Relationnel|Adaptabilité|Apprentissage|Rigueur|Autonomie|Travail en groupe|Travail sous pression|Autonome|Organisé|Rigoureux|Eclipse|NetBeans|AndroidStudio|Code:Blocks|Dev\-C\+\+|VisualStudio|STVisualdevelop|IDE|SASSoftware|SASViya|Jupyter|Linux|Ubuntu|NASM|Anaconda|Spyder|Talend|Tableau|BusinessObjects|SAS|Jira|Trello|jupyter-notebook|pycharm|Oracle|SasStudio|Mangodb|PowerBI|Talend|Tableau|Excel|Jupyter|Anaconda|Jupyter|spyder|KNIME|PhpMyAdmin|Colab|Dynamic|Dynamique|collaborative work|Collaboratif|Analyse critique|Ponctualité|Travail en groupe|Gestion de temps|Esprit d’analyse|Méticulosité|communication|Agile|Waterfal|Python|SQL|PL/SQL|SAS|Java|C|SQL|MATLAB|Python|Sql|Java|OcamlMatlab|UML|Haskell|SQL3|SAS|JavaScript|PHP|J2E|Pascal|HTML|CSS|XML|R|Java/JEE|OCaml|Mysql|Html|VBA|DATA warehouse|DateWarehouse|PHP5|Symfony|Angular9|SpringBoot|JEE|HTML5|CSS3|JS|JavaScript|pandas|numpy|matplotlib|seaborn|PLSQL|Ocaml|Scala|SQL|PLSQL|NoSQL|Prolog|SAS|Oracle|MongoDB|MySQL|Talend|Tableau|BusinessObjects|TensorFlow|Keras|Scikit-learn|Scikit-Fuzzy|MicrosoftOfficeExcel|Prolog|Oracle|MongoDB|MySQL|DataBase|Talend|DataIntegration|DataQuality|SAS|Tableau|BusinessObjects|HADOOP|HDFS|MapReduce|HBASE|SPARK|RSTUDIO|WEKA|IBMSPSSMODELER|REDIS|MongoDB|JupyterNotebook|Eclipse|SAS|VisualStudioCode|Rstudio|AndroidStudio|Git|Oracle|SASViya|SAS9|MangoDB|MATLAB|Oracle|BusinessObjects|MéthodeAgile|SCRUM|Trello|GitHub|oracle|PLSQL|SQLserver|SSIS|Trello|Word|Excel|PowerPoint|make|git|Oracle|SasStudio|PowerBI|Excel|Jupyter|ApacheKakfa|Elasticsearch|Logstash|Kibana|FileBeat|Trello|MarvenApp|Git|UML|Docker|SpringBoot|SpringData|SpringSecurity|HTML|Thymeleaf|CSS|VB|UML|GRASPpattern|Merise|Proto.io|Axure|Internet des objets|IOT|Business intelligence|Représentation graphique de données statistiques|Domotique|meetup tafterworks|Statistiques)",
        cleanedData,
        re.MULTILINE | re.IGNORECASE 
    )
    competences = []
    for value in extracted:
        if "'" + value.group().lower().strip() + "'" not in competences: #pour ne pas insérer des doublons de la même valeur
            competencesDoublee.append("'" + value.group().lower().strip() + "'")
    return competences

def extraire_langue(text):
    s = ParseCV.cleanText(text)
    listLangue=[]
    langue = "NULL"
    niveau = "NULL"
    regex = r"(français|francais|anglais|Allemand|Kabyle|Arabe|Chinois|mandarin|hindi|bengali|panjabi|Espagnol|Deutsch|Turc|Berbère|Wolof|Tamoul|italien|portuguais|russe|japonais|danois|polonais|javanais|telougou|malais|coreen|marathi|turc|vietnamien|tamoul|italien|persan|thai|gujarati|polonais|pachtou|kannada|malayalam|soundanais|oriya|birman|ukrainien|bhojpouri|filipino |yorouba|maithili|ouzbek|sindhi|amharique|peul|roumain|oromo|igbo |azéri|awadhi|visayan|neerlandais|kurde|malgache|saraiki|chittagonien|khmer|turkmène|assamais|madourais|somali|marwari|magahi|haryanvi|hongrois|chhattisgarhi|grec|chewa|deccan|akan|kazakh|sylheti|zoulou|tcheque)[ ](.*?[ ].*?[ ].*?[ ])"

    matches = re.finditer(regex, text, re.MULTILINE | re.IGNORECASE)

    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            if(groupNum==1):
                langue = "'"+match.group(groupNum).strip() +"'"
            elif(groupNum==2):
                regexNiveau = r"(A1|B1|B2|C1|C2|langue maternelle|bilingue|débutant|avancé|HSK 3)"
                matchesNiveau = re.finditer(regexNiveau, match.group(groupNum),re.IGNORECASE)
                for matchNumNiveau, matchNiveau in enumerate(matchesNiveau, start=1):
                    niveau = "'"+ matchNiveau.group().strip() +"'"
        listLangue.append([langue,niveau])
    return(listLangue)

def extraire_centreInteret(text):
    # clean le texte du cv
    s = ParseCV.cleanText(text)

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
    punctuation=['(', ')', '?', ':', ';', ',', '.', '!', '/', '-', "_"]
    num_adr = 'NULL'
    localite_adr = 'NULL'
    nomRue_adr = 'NULL'
    cp_adr = 'NULL'
    ville_adr = 'NULL'
    pays_adr = 'FRANCE'
    continent_adr = 'EUROPE'
    if re.match('[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+',adresse):
        num_adr = re.sub('([0-9]+)(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+', '\g<1>',adresse)
        cpl_adr = re.sub('[0-9]+((?:BIS|TER)?),? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+', '\g<1>',adresse)
        num_adr = num_adr + cpl_adr
        localite_adr = re.sub('[0-9]+(?:BIS|TER)?,? ?((?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS)) [A-Z ]+,? ?(?:[0-9]{5}| )? [A-Z\-]+', '\g<1>',adresse)
        nomRue_adr = re.sub('[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) ([A-Z ]+),? ?(?:[0-9]{5}| )? [A-Z\-]+', '\g<1>',adresse)
        cp_adr = re.sub('[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?((?:[0-9]{5}| ))? [A-Z\-]+', '\g<1>',adresse)
        if cp_adr == '':
            cp_adr = 'NULL'
        else:
            cp_adr = '\'' + cp_adr.strip().upper() + '\''
        ville_adr = re.sub('[0-9]+(?:BIS|TER)?,? ?(?:AVENUE|RUE|BOULEVARD|QUAI|IMPASSE|PONT|PLACE|SQUARE|ALLEE|ALLEES|VOIE|MONTEE|ESPLANADE|ROUTE|VOIRIE|CITE|CHEMIN|PARVIS) [A-Z ]+,? ?(?:[0-9]{5}| )? ([A-Z\-]+)', '\g<1>',adresse)


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
    return num_adr,localite_adr,nomRue_adr,cp_adr,ville_adr,pays_adr,continent_adr
