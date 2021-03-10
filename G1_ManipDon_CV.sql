-- ===============================================================================
-- ===============================================================================    
-- 	 Projet			   : Projet (Partie1) : Exploration des Curriculum-Vitae (CV)               
--   Nom du SGBD/DBMS  : ORACLE  (MySQL/MongoDB/PostGRES/SQLServer...)        
--   Dates             : 17/12/2020 
--   Lieu              : Université Sorbonne Paris Nord, Institut Galiée
--   Auteurs           : Faïza BERHILI, Ammar ALSADIK, Emiliano BOUSSAC, Julian CHAMBRIER
--   Page Web          : http://www.lipn.univ-paris13.fr/~boufares
-- 	 Fichier		   : G1_ManipDon_CV.sql
--   Enseignant		   : Monsieur Faouzi BOUFARES
-- =============================================================================== 
-- Promotion : M2EID2 
-- =============================================================================== 

-- Numéro du Groupe 	--->>>> : G1
-- Numéro des Binôme  	--->>>> : B18/B19
-- NOM1 PRENOM1        	--->>>> : BERHILI Faiza			(B18)
-- NOM2 PRENOM2         --->>>> : BOUSSAC Emiliano		(B18)
-- NOM3 PRENOM3         --->>>> : ALSADIK Ammar  		(B19)
-- NOM4 PRENOM4         --->>>> : CHAMBRIER Julian 		(B19)



COLUMN NOMCPT FORMAT A15
COLUMN NOMCAN FORMAT A15
COLUMN NOMCTRINT FORMAT A15
COLUMN PRENOMCAN FORMAT A15
COLUMN NOMCATEGORIE FORMAT A25


-- Top 3 des compétences des gens ayant été accepté
SELECT * FROM (SELECT NOMCPT,COUNT(*) AS NB FROM (RELATION_COMP_CAN NATURAL JOIN CANDIDATS) NATURAL JOIN CV 
WHERE ADMIS = 'ACCEPTE' GROUP BY NOMCPT ORDER BY COUNT(*) DESC) WHERE ROWNUM <= 3 ;

/*
NOMCPT                  NB
--------------- ----------
R                       50
C                       50
PYTHON                  39
*/

--Quelles sont les catégories de compétences qui sont le plus accepté 
SELECT NOMCATEGORIE, COUNT(*) NB FROM COMPETENCES WHERE NOMCATEGORIE IS NOT NULL GROUP BY NOMCATEGORIE ORDER BY COUNT(*) DESC;
/*
NOMCATEGORIE                      NB
------------------------- ----------
SOFTSKILLS                        19
OUTILS                            19
LANGAGE DE PROGRAMMATION          11
BASE DE DONNEES                   10
WEB                                7
SYSTEME EXPLOITATION               2
CREATIVITE                         1
ELECTRONIQUE                       1

On voit que les soft skills sont très importantes
*/

-- Quelles sont les étudiants ayant un niveau bac +4  ?
 SELECT NOMCAN,PRENOMCAN FROM (SUIT_FORMATIONS JOIN FORMATIONS USING(IDFORM)) JOIN CANDIDATS USING(IDCAN) WHERE NIVEAU LIKE 'MASTER%' ;

/*
NOMCAN          PRENOMCAN
--------------- ---------------
ALSADIK         Ammar
CHAOUCHE        Yacine
DJENADI         Sabrina
ALSADIK         Ammar
DJENADI         Sabrina
TCHEDRE         Napotiyadja
AOUDJEHANE      Sarah
BENSAID         Imane
                Maurice
BIAN            Yiping
BOUHOUT         Adil
BOUMAZA         Heytem
CHAMBRIER       Julian
CHFADI          Sara
ELHAIL          Mohamed
ESSEBBABI       Nour
KARAKAS         Alexandre
KOUACHI         Abdeldjalil
MALKI           Salma
MBENGUE         Ibrahima
MEDJDOUBI       Lynda
OULDOULHADJ     Dehbia
SABOUNI         Soukayna
SIAMER          Amel
TCHEDRE         Napotiyadja
TERAA           Youcefoussama
YABA            Michel
AOUDJEHANE      Sarah
BIAN            Yiping
BOUMAZA         Heytem
CHAMBRIER       Julian
CHAOUCHE        Yacine
KARAKAS         Alexandre
KOUACHI         Abdeldjalil
MEDJDOUBI       Lynda
OULDOULHADJ     Dehbia
SIAMER          Amel
YABA            Michel
*/

-- Quel est la plage des années de formations 
SELECT MIN(DATEDEBUTFORM),MAX(DATEDEBUTFORM) FROM SUIT_FORMATIONS;
/*
MIN(DATE MAX(DATE
-------- --------
01/01/10 01/04/21
*/

-- Plage d'age des gens acceptés
SELECT MIN(AGE),MAX(AGE) FROM CANDIDATS JOIN CV USING(IDCAN) WHERE ADMIS = 'ACCEPTE';
/*

  MIN(AGE)   MAX(AGE)
---------- ----------
        21         37
*/

-- Quelles sont les personnes qui sont bilingues
SELECT NOMCAN,PRENOMCAN FROM CANDIDATS WHERE IDCAN IN (SELECT IDCAN FROM RELATION_LANG_CAN GROUP BY IDCAN HAVING COUNT(*) >= 2);

/*
NOMCAN          PRENOMCAN
--------------- ---------------
AOUDJEHANE      Sarah
                Maurice
CHAMBRIER       Julian
GUASSIM         Mohamed
JIANG           Alexis
ELHAIL          Mohamed
KARAKAS         Alexandre
QIAN            Xiaotong
SATHIANATHAN    Sayanthan
BOUHOUT         Adil
BOUSSAC         Emiliano
MALKI           Salma
SABOUNI         Soukayna
BENSAID         Imane
BIAN            Yiping
CHFADI          Sara
DJENADI         Sabrina
TERAA           Youcefoussama
YABA            Michel
LE              Minhhao
MEDJDOUBI       Lynda
ALSADIK         Ammar
BABORI          Yasmine
OULDOULHADJ     Dehbia
                Sene
SIAMER          Amel
*/ 

-- Age moyen des personnes ayant suivie une formation de master
SELECT AVG(AGE) FROM (CANDIDATS JOIN SUIT_FORMATIONS USING(IDCAN)) JOIN FORMATIONS USING(IDFORM) WHERE NIVEAU LIKE 'MASTER%';

/*
  AVG(AGE)
----------
     24,85
*/

-- Top 3 des centres d'intérêts des personnes refusées
SELECT * FROM (SELECT NOMCTRINT,COUNT(*) AS NB FROM (RELATION_CENTINT_CAN NATURAL JOIN CANDIDATS) NATURAL JOIN CV WHERE ADMIS = 'REFUSE' GROUP BY NOMCTRINT ORDER BY COUNT(*) DESC) WHERE ROWNUM <= 3 ;
 
/*
NOMCTRINT               NB
--------------- ----------
TECHNOLOGIE              3
MUSIQUE                  2
PHOTOGRAPHIE             2
*/ 
 
-- Quels candidats a une photo sur son CV

SELECT NOMCAN,PRENOMCAN FROM CANDIDATS JOIN CV USING(IDCAN) WHERE PHOTO IS NOT NULL;

/*
NOMCAN          PRENOMCAN
--------------- ---------------
ADEL            Salaheddine
ALSADIK         Ammar
AOUDJEHANE      Sarah
BABORI          Yasmine
BIAN            Yiping
BOUHOUT         Adil
BOUSSAC         Emiliano
CHAMBRIER       Julian
CHATTAT         Naima
CHFADI          Sara
DJENADI         Sabrina
ELHAIL          Mohamed
ESSEBBABI       Nour
GUASSIM         Mohamed
HJIB            Maroua
KARAKAS         Alexandre
KOUACHI         Abdeldjalil
LE              Minhhao
MALKI           Salma
MEDJDOUBI       Lynda
QIAN            Xiaotong
SABOUNI         Soukayna
TCHEDRE         Napotiyadja
YABA            Michel
DIALLO          Mamadou-Korka
SENE            Mame-Astou
BENJAMIN        Seveno
DUPONT          Julie
MARION          Naudin
RICHARD         Seguin
SAUMUR          Thomas
*/

-- Quels étudiants à postuler l'année où il a fait sa dernière formation

SELECT NOMCAN, PRENOMCAN FROM (CANDIDATS JOIN CV USING(IDCAN)) JOIN SUIT_FORMATIONS USING(IDCAN) WHERE EXTRACT(YEAR FROM DATETRANSMISSION) = EXTRACT(YEAR FROM DATEFINFORM);

/*
NOMCAN          PRENOMCAN
--------------- ---------------
BENSAID         Imane
BERHILI         Faiza
BIAN            Yiping
BOUHOUT         Adil
CHAMBRIER       Julian
CHFADI          Sara
DJENADI         Sabrina
ELHAIL          Mohamed
MALKI           Salma
MEDJDOUBI       Lynda
OULDOULHADJ     Dehbia
SABOUNI         Soukayna
SIAMER          Amel

*/

-- Quels sont les étudiants qui on des compétences en PL/SQL et des compétences dans la catégorie WEB
SELECT NOMCAN, PRENOMCAN FROM CANDIDATS WHERE IDCAN IN (
SELECT IDCAN FROM RELATION_COMP_CAN JOIN COMPETENCES USING(NOMCPT) WHERE NOMCPT = 'PL/SQL'
INTERSECT 
SELECT IDCAN FROM RELATION_COMP_CAN JOIN COMPETENCES USING(NOMCPT) WHERE NOMCATEGORIE = 'WEB');
/*
NOMCAN          PRENOMCAN
--------------- ---------------
ADEL            Salaheddine
ALSADIK         Ammar
AOUDJEHANE      Sarah
BENSAID         Imane
BOUMAZA         Heytem
BOUSSAC         Emiliano
CHAMBRIER       Julian
DJENADI         Sabrina
GUASSIM         Mohamed
HAIDOURI        Issam
HJIB            Maroua
JIANG           Alexis
LE              Minhhao
MALKI           Salma
OULDOULHADJ     Dehbia
QIAN            Xiaotong
TCHEDRE         Napotiyadja
TERAA           Youcefoussama
YABA            Michel
/*




