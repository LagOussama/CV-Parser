
Pour exécuter ce Projet.

Suivez les étapes ci-dessous : 

Etape 1) Python 

- Ouvrez un terminal :
	- Lancez : Invite de commandes (ou CMD) sur WINDOWS (ou Terminal sur Mac et Linux)
	- Placez vous dans le dossier de ce projet (cd ..'lien avant le dossier'../Projet_CV)
	
- Installer les bibliothèques Python : 
	- pip install numpy
	- pip install unidecode
	- pip install pandas
	- pip install "PyMuPDF==1.16.11"
	- pip install soundex
	- pip install strsimpy
 	- pip install opencv-python
	- pip install pdf2image
	- pip install deep-translator


- Exécuter le code python du fichier Extract_PDF_V2.py avec la commande : python Extract_PDF_V2.py (ou python3 selon votre version)
	- En cas d'erreur, vérifier qu'il ne vous manque pas une bibliothèque, qui n'est pas mentionnée au-dessus

- Un barre de chargement indique l'avancée du processus
	- Attendre la fin d'exécution de script python (Quelques secondes avec une quarantaire de PDF)

L'exécution de ce scipt python a permit d'extraire l'information des PDF et de créer les requêtes d'insertions par rapport à ces PDF.


Etape 2) SQL

- Exécuter le fichier G1_CreatDon_CV.sql (@G1_CreatDon_CV.sql sur SQL*PLUS ou copier/coller sur d'autre environnement)
- Exécuter le fichier G1_InsertDon_CV.sql (@G1_InsertDon_CV.sql sur SQL*PLUS ou copier/coller sur d'autre environnement)
- Exécuter le fichier G1_ManipDon_CV.sql (@G1_ManipDon_CV.sql sur SQL*PLUS ou copier/coller sur d'autre environnement)

Notes importantes : 

- Ne pas toucher au fichier ids_tables.txt
Il s'agit d'un fichier permettant d'éviter la redondance des identifiants.
Il garde en mémoire, les identifiants disponibles afin d'éviter la redondance.
Les identifiants sont initialisés à 1,1,1,1. 

- Le fichier Prenoms.csv est une base de données contenant de nombreuses données de Prénoms, le script va s'en servir afin de faciliter l'extraction de ces informations.
En effet, il utilise notamment Prenoms avec le soundex et la distance de Levenshtein.

- Les dossiers CV_ACCEPTE, CV_REFUSE, et Photo_CV stockent, respectivement, les cv des personnes acceptées, les cv des personnes refusées et les photos extraies automatiquement 
par le script avec un detection des visage.