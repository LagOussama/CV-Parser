 ---------------------------------------------------------------
 --        Script Création de la base de données CV
 ---------------------------------------------------------------
 drop table LanguesCandidat;
 drop table Langues;
 drop table LoisirsCandidat;
 drop table Loisirs;
 drop table Formations;
 drop table Diplomes;
 drop table EtablissementPedagogique;
 drop table ExperiencesProfessionnelles;
 drop table GenreCompetences;
 drop table CompetencesCandidat;
 drop table EtablissementProfessionnelle;
 drop table Projets;
 drop table EtablissementPedaCandidat;
 drop table EtablissementProCandidat;
 drop table candidat;
 drop table Competences;

/*
drop table Candidat cascade constraints;
*/
------------------------------------------------------------
-- Table: Candidat
------------------------------------------------------------
CREATE TABLE Candidat(
	IdCandidat             NUMBER NOT NULL ,
	NomCandidat            VARCHAR2 (50)  ,
	PrenomCandidat         VARCHAR2 (50)  ,
	DateNaissanceCandidat  DATE   ,
	TelephoneCandidat      VARCHAR2 (50)  ,
	EmailCandidat          VARCHAR2 (100)  ,
	RueCandidat            VARCHAR2 (100)   ,
	AvenueCandidat         VARCHAR2 (100)  ,
	VilleCandidat          VARCHAR2 (50)  ,
	PaysCandidat           VARCHAR2 (50)  ,
	CodePostalCandidat     VARCHAR2 (50)  ,
	Permis                 VARCHAR2 (10)  ,
	CiviliteCandidat       VARCHAR2 (50)  ,
	CvCandidat             VARCHAR2 (200)  ,
	PhotoCandidat          VARCHAR2 (200)  ,
	CONSTRAINT Candidat_PK PRIMARY KEY (IdCandidat)
);

------------------------------------------------------------
-- Table: Loisirs
------------------------------------------------------------
CREATE TABLE Loisirs(
	IdLoisir           NUMBER NOT NULL ,
	NomLoisir          VARCHAR2 (50)  ,
	CONSTRAINT Loisirs_PK PRIMARY KEY (IdLoisir)
);

------------------------------------------------------------
-- Table: Langues
------------------------------------------------------------
CREATE TABLE Langues(
	IdLangue      NUMBER NOT NULL ,
	Langue        VARCHAR2 (50)  ,
	CONSTRAINT Langues_PK PRIMARY KEY (IdLangue)
);

------------------------------------------------------------
-- Table: GenreCompetences
------------------------------------------------------------
CREATE TABLE GenreCompetences(
	IdGenreCompetence  NUMBER NOT NULL ,
	GenreCompetence    VARCHAR2 (50)  ,
	CONSTRAINT GenreCompetences_PK PRIMARY KEY (IdGenreCompetence)
);

------------------------------------------------------------
-- Table: Competences
------------------------------------------------------------
CREATE TABLE Competences(
	IdCompetence  NUMBER NOT NULL ,
	Competence    VARCHAR2 (50)  ,
	IdGenreCompetence     NUMBER(10,0)   ,
	CONSTRAINT Competences_PK PRIMARY KEY (IdCompetence)
	,CONSTRAINT GenreCompetences_FK FOREIGN KEY (IdGenreCompetence) REFERENCES GenreCompetences(IdGenreCompetence)
	,CONSTRAINT Competences_AK UNIQUE (IdGenreCompetence)
);

------------------------------------------------------------
-- Table: Projets
------------------------------------------------------------
CREATE TABLE Projets(
	IdProjet           NUMBER NOT NULL ,
	IntituleProjet     VARCHAR2 (200)  ,
	DescriptionProjet  VARCHAR2 (200)  ,
	DateDebutProjet    DATE   ,
	DateFinProjet      DATE   ,
	IdCandidat         NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT Projets_PK PRIMARY KEY (IdProjet)
	,CONSTRAINT Projets_Candidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);

------------------------------------------------------------
-- Table: EtablissementPedagogique
------------------------------------------------------------
CREATE TABLE EtablissementPedagogique(
	IdEtPed  NUMBER NOT NULL ,
	DetailsEtablissement        VARCHAR2 (100)  ,
	NomEtablissementP           VARCHAR2 (200)  ,
	VilleEtablissementP         VARCHAR2 (50) ,
	PaysEtablissementP          VARCHAR2 (50)  ,
	CONSTRAINT EtablissementPedagogique_PK PRIMARY KEY (IdEtPed)
);

------------------------------------------------------------
-- Table: Diplomes
------------------------------------------------------------
CREATE TABLE Diplomes(
	IdDiplome           NUMBER NOT NULL ,
	DesignationDiplome  VARCHAR2 (100)  ,
	CONSTRAINT Diplomes_PK PRIMARY KEY (IdDiplome)
);

------------------------------------------------------------
-- Table: Formations
------------------------------------------------------------
CREATE TABLE Formations(
	IdFormations                NUMBER NOT NULL ,
	SpecialiteFormation         VARCHAR2 (100) ,
	OptionFormation             VARCHAR2 (100) ,
	MentionObtenu               VARCHAR2 (100)  ,
	NiveauEtude                 VARCHAR2 (50) ,
	IdDiplome                   NUMBER(10,0)   ,
	IdEtPed  NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT Formations_PK PRIMARY KEY (IdFormations)
	,CONSTRAINT Formations_Diplomes_FK FOREIGN KEY (IdDiplome) REFERENCES Diplomes(IdDiplome)
	,CONSTRAINT Formations_EttPed0_FK FOREIGN KEY (IdEtPed) REFERENCES EtablissementPedagogique(IdEtPed)
);

------------------------------------------------------------
-- Table: EtablissementProfessionnelle
------------------------------------------------------------
CREATE TABLE EtablissementProfessionnelle(
	IdEtPro  NUMBER NOT NULL ,
	NomEtablissementPro             VARCHAR2 (200)  ,
	VilleEtablissementPro           VARCHAR2 (50)  ,
	PaysEtablissementPro            VARCHAR2 (50) ,
	CONSTRAINT EtPro_PK PRIMARY KEY (IdEtPro)
);

------------------------------------------------------------
-- Table: ExperiencesProfessionnelles
------------------------------------------------------------
CREATE TABLE ExperiencesProfessionnelles(
	IdExperienceProfessionnelle     NUMBER NOT NULL ,
	IntitulePoste                   VARCHAR2 (200)  ,
	IdEtPro  NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT ExperiencesProfessionnelles_PK PRIMARY KEY (IdExperienceProfessionnelle)
	,CONSTRAINT ExpPro_EtPro_FK FOREIGN KEY (IdEtPro) REFERENCES EtablissementProfessionnelle(IdEtPro)
);

------------------------------------------------------------
-- Table: LoisirsCandidat
------------------------------------------------------------
CREATE TABLE LoisirsCandidat(
	IdCandidat         NUMBER(10,0)  NOT NULL  ,
	IdLoisir           NUMBER(10,0)  NOT NULL  ,
	DescriptionLoisir  VARCHAR2 (50) ,
	CONSTRAINT Passioner_PK PRIMARY KEY (IdCandidat,IdLoisir)
	,CONSTRAINT Passioner_Candidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
	,CONSTRAINT Passioner_Loisirs0_FK FOREIGN KEY (IdLoisir) REFERENCES Loisirs(IdLoisir)
);

------------------------------------------------------------
-- Table: LanguesCandidat
------------------------------------------------------------
CREATE TABLE LanguesCandidat(
	IdCandidat    NUMBER(10,0)  NOT NULL  ,
	IdLangue      NUMBER(10,0)  NOT NULL  ,
	NiveauLangue  VARCHAR2 (50)  ,
	CONSTRAINT Parler_PK PRIMARY KEY (IdCandidat,IdLangue)
	,CONSTRAINT Parler_Candidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
	,CONSTRAINT Parler_Langues0_FK FOREIGN KEY (IdLangue) REFERENCES Langues(IdLangue)
);

------------------------------------------------------------
-- Table: CompetencesCandidat
------------------------------------------------------------
CREATE TABLE CompetencesCandidat(
	IdCompetence      NUMBER(10,0)  NOT NULL  ,
	IdCandidat        NUMBER(10,0)  NOT NULL  ,
	NiveauCompetence  VARCHAR2 (50)  ,
	CONSTRAINT Maitriser_PK PRIMARY KEY (IdCompetence,IdCandidat)
	,CONSTRAINT Maitriser_Competences_FK FOREIGN KEY (IdCompetence) REFERENCES Competences(IdCompetence)
	,CONSTRAINT Maitriser_Candidat0_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);

------------------------------------------------------------
-- Table: EtablissementPedaCandidat
------------------------------------------------------------
CREATE TABLE EtablissementCandidat(
	IdEtablissementPedagogique  NUMBER(10,0)  NOT NULL  ,
	IdCandidat     NUMBER(10,0)  NOT NULL  ,
	DateDebutAffectationPe Date,
	DateFinAffectationPe Date,
	CONSTRAINT EtablissementCandidat_PK PRIMARY KEY (IdEtablissementPedagogique,IdCandidat)
	,CONSTRAINT EtablissementCandidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);

------------------------------------------------------------
-- Table: EtablissementProCandidat
------------------------------------------------------------
CREATE TABLE EtablissementProCandidat(
	IdEtablissementProfessionnelle  NUMBER(10,0)  NOT NULL  ,
	IdCandidat     NUMBER(10,0)  NOT NULL  ,
	DateDebutAffectationPro Date,
	DateFinAffectationPro Date,
	CONSTRAINT EtablissementCandidat_PK_0 PRIMARY KEY (IdEtablissementProfessionnelle,IdCandidat)
	,CONSTRAINT EtablissementCandidat_FK_0 FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);
