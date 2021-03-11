import unidecode
import pandas as pd

from extrInfo import eclater_adresse



def create_requete(storage_file ,pdf_file ,mail ,tel ,adresse ,age ,prenom ,nom ,sexe ,permis ,site_res ,date_naiss
                   ,nationalite ,tabFormation ,listCompetence ,listLangues ,listCentreInteret):
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
    ids = pd.DataFrame \
        ({'id_adr': [new_id_adr], 'id_can' :[new_id_can], 'id_cv' :[new_id_cv], 'id_site' : [int(id_site)]})
    ids.to_csv('./ids_tables.txt', index=False, header = True, mode = 'w')

    # On écrit dans le fichier de sortie .sql
    out_file = open('./G1_InsertDon_CV.sql', 'a')

    # Insertion Adresses
    if adresse != 'NULL':
        num_adr, localite_adr, nomRue_adr, cp_adr, ville_adr, pays_adr, continent_adr = eclater_adresse(adresse)
        out_file.write('EXEC INSERT_ADRESSES( '+ str
            (id_adr) + ',' + num_adr + ',' + localite_adr + ',' + nomRue_adr + ',' + cp_adr + ',' + ville_adr + ',' + pays_adr + ',' + continent_adr + ');\n')
    # Insertion Candidats
    out_file.write('EXEC INSERT_CANDIDATS(\' '+ str(id_can) + '\',' + str
        (id_adr) + ',' + nom + ',' + prenom + ',' + sexe + ',' + age + ',' + date_naiss + ',' + mail + ',' + nationalite +  ',' + tel + ');\n')
    # Insertion Permis
    for p in permis:
        p = p.strip().upper()
        date_obtention = 'NULL'
        out_file.write('EXEC INSERT_OBTENTIONPERMIS(\' '+ p + '\',\'' + str(id_can) + '\',' + date_obtention +');\n')
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
        id_can) + '\',\'' + nom_cv + '\',' + titre_cv + ',' + description_cv + ',' + posteRecherche_cv + ',' + typePoste_cv + ',' + dispo_cv + ',' + admis + ',' + date_transmission + ');\n')

    # Insertion Formations
    for formation in tabFormation:
        niveau = unidecode.unidecode(formation[0].strip().upper())
        specialite = unidecode.unidecode(formation[1].strip().upper())
        ecole = unidecode.unidecode(formation[2].strip().upper())
        out_file.write('EXEC INSERT_SUIT_FORMATIONS(' + ecole + ',' + niveau + ',' + specialite + ',\'' + str(
            id_can) + '\',' + formation[3] + ',' + formation[4] + ');\n')

    # Insertion Compétence
    for competence in listCompetence:
        competence = unidecode.unidecode(competence.strip().upper())
        catCpt = competence
        out_file.write('EXEC INSERT_RELATION_COMP_CAN(' + competence + ',' + catCpt + ',\'' + str(id_can) + '\');\n')

    # Insertion Centre d'interêts
    for centreInteret in listCentreInteret:
        centreInteret = unidecode.unidecode(centreInteret.strip().upper())
        out_file.write('EXEC INSERT_RELATION_CENTINT_CAN(' + centreInteret + ',\'' + str(id_can) + '\');\n')

    out_file.close()
    # print(mail,tel,adresse,age,prenom,nom,sexe,permis,site_res)
