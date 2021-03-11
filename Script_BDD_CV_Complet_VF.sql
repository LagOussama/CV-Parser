 ---------------------------------------------------------------
 --        Script Création de la base de données CV
 ---------------------------------------------------------------


------------------------------------------------------------
-- Table: Candidat
------------------------------------------------------------
CREATE TABLE Candidat(
	IdCandidat             NUMBER NOT NULL ,
	NomCandidat            VARCHAR2 (50)  ,
	PrenomCandidat         VARCHAR2 (50)  ,
	-- Date
	DateNaissanceCandidat  VARCHAR(50)   ,
	TelephoneCandidat      VARCHAR2 (50)  ,
	EmailCandidat          VARCHAR2 (100)  ,
	RueCandidat            NUMBER(10,0)   ,
	AvenueCandidat         VARCHAR2 (100)  ,
	VilleCandidat          VARCHAR2 (50)  ,
	PaysCandidat           VARCHAR2 (50)  ,
	CodePostalCandidat     VARCHAR2 (50)  ,
	LienLinkedin           VARCHAR2 (100)  ,
	Permis                 VARCHAR2 (10)  ,
	SituationFamiliale     VARCHAR2 (50)  ,
	CiviliteCandidat       VARCHAR2 (50)  ,
	HandicapCandidat       NUMBER (1) ,
	TitreProfil            VARCHAR2 (100)  ,
	DescriptionProfil      VARCHAR2 (200)  ,
	CvCandidat             VARCHAR2 (200)  ,
	PhotoCandidat          VARCHAR2 (200)  ,
	CONSTRAINT Candidat_PK PRIMARY KEY (IdCandidat),
	CONSTRAINT CHK_BOOLEAN_HandicapCandidat CHECK (HandicapCandidat IN (0,1))
);

------------------------------------------------------------
-- Table: References
------------------------------------------------------------
CREATE TABLE References1(
	IdReference        NUMBER NOT NULL ,
	NomReferent        VARCHAR2 (100)  ,
	PrenomReferent     VARCHAR2 (100)  ,
	EmailReferent      VARCHAR2 (200)  ,
	TelephoneReferent  VARCHAR2 (50)  ,
	IdCandidat         NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT References_PK PRIMARY KEY (IdReference)
	,CONSTRAINT References_Candidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);

------------------------------------------------------------
-- Table: Loisirs
------------------------------------------------------------
CREATE TABLE Loisirs(
	IdLoisir           NUMBER NOT NULL ,
	NomLoisir          VARCHAR2 (50)  ,
	DescriptionLoisir  VARCHAR2 (200)  ,
	CONSTRAINT Loisirs_PK PRIMARY KEY (IdLoisir)
);

------------------------------------------------------------
-- Table: Langues
------------------------------------------------------------
CREATE TABLE Langues(
	IdLangue      NUMBER NOT NULL ,
	Langue        VARCHAR2 (50) NOT NULL  ,
	NiveauLangue  VARCHAR2 (50)  ,
	CONSTRAINT Langues_PK PRIMARY KEY (IdLangue)
);

------------------------------------------------------------
-- Table: Competences
------------------------------------------------------------
CREATE TABLE Competences(
	IdCompetence  NUMBER NOT NULL ,
	Competence    VARCHAR2 (50) NOT NULL  ,
	CONSTRAINT Competences_PK PRIMARY KEY (IdCompetence)
);

------------------------------------------------------------
-- Table: GenreCompetences
------------------------------------------------------------
CREATE TABLE GenreCompetences(
	IdGenreCompetence  NUMBER NOT NULL ,
	GenreCompetence    VARCHAR2 (50) NOT NULL  ,
	IdCompetence       NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT GenreCompetences_PK PRIMARY KEY (IdGenreCompetence)
	,CONSTRAINT GenreCompetences_FK FOREIGN KEY (IdCompetence) REFERENCES Competences(IdCompetence)
	,CONSTRAINT GenreCompetences_AK UNIQUE (IdCompetence)
);

------------------------------------------------------------
-- Table: Projets
------------------------------------------------------------
CREATE TABLE Projets(
	IdProjet           NUMBER NOT NULL ,
	IntituleProjet     VARCHAR2 (200) NOT NULL  ,
	DescriptionProjet  VARCHAR2 (200)  ,
	-- Date 
	DateDebutProjet    VARCHAR(50)   ,
	DateFinProjet      VARCHAR(50)   ,
	IdCandidat         NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT Projets_PK PRIMARY KEY (IdProjet)
	,CONSTRAINT Projets_Candidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);

------------------------------------------------------------
-- Table: TypeExperienceProfessionnelle
------------------------------------------------------------
CREATE TABLE TypeExperienceProfessionnelle(
	IdTypeExperiencePro  NUMBER NOT NULL ,
	TypeExperienceProfessionnelle    VARCHAR2 (200) NOT NULL  ,
	CONSTRAINT TypeExperience_PK PRIMARY KEY (IdTypeExperiencePro)
);

------------------------------------------------------------
-- Table: Etablissement
------------------------------------------------------------
CREATE TABLE Etablissement(
	IdEtablissement     NUMBER NOT NULL ,
	NomEtablissement    VARCHAR2 (200) NOT NULL  ,
	VilleEtablissement  VARCHAR2 (100)  ,
	PaysEtablissement   VARCHAR2 (100)  ,
	CONSTRAINT Etablissement_PK PRIMARY KEY (IdEtablissement)
);

------------------------------------------------------------
-- Table: EtablissementProfessionnelle
------------------------------------------------------------
CREATE TABLE EtablissementProfessionnelle(
	IdEtablissement                 NUMBER(10,0)  NOT NULL  ,
	IdEtablissementPro              NUMBER(10,0)  NOT NULL  ,
	DepartementEtablissement        VARCHAR2 (100) NOT NULL  ,
	NomEtablissement                VARCHAR2 (200) NOT NULL  ,
	VilleEtablissement              VARCHAR2 (100)  ,
	PaysEtablissement               VARCHAR2 (100)  ,
	CONSTRAINT EtablissementPro_PK PRIMARY KEY (IdEtablissement,IdEtablissementPro)
	,CONSTRAINT EtablissementPro_FK FOREIGN KEY (IdEtablissement) REFERENCES Etablissement(IdEtablissement)
);

------------------------------------------------------------
-- Table: ExperiencesProfessionnelles
------------------------------------------------------------
CREATE TABLE ExperiencesProfessionnelles(
	IdExperiencePro                 NUMBER NOT NULL ,
	IntitulePoste                   VARCHAR2 (200) NOT NULL  ,
	-- Date 
	DateDebutExperience             VARCHAR(50)   ,
	DateFinExperience               VARCHAR(50)   ,
	IdEtablissement                 NUMBER(10,0)  NOT NULL  ,
	IdEtablissementPro  NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT ExperiencesPro_PK PRIMARY KEY (IdExperiencePro)
	,CONSTRAINT ExperiencesPro_FK FOREIGN KEY (IdEtablissement,IdEtablissementPro) REFERENCES EtablissementProfessionnelle(IdEtablissement,IdEtablissementPro)
);

------------------------------------------------------------
-- Table: EtablissementPedagogique
------------------------------------------------------------
CREATE TABLE EtablissementPedagogique(
	IdEtablissement             NUMBER(10,0)  NOT NULL  ,
	IdEtablissementPedagogique  NUMBER(10,0)  NOT NULL  ,
	DetailsEtablissement        VARCHAR2 (100) NOT NULL  ,
	NomEtablissement            VARCHAR2 (200) NOT NULL  ,
	VilleEtablissement          VARCHAR2 (100)  ,
	PaysEtablissement           VARCHAR2 (100)  ,
	CONSTRAINT EtablissementPedagogique_PK PRIMARY KEY (IdEtablissement,IdEtablissementPedagogique)
	,CONSTRAINT EtablissementPedagogique_FK FOREIGN KEY (IdEtablissement) REFERENCES Etablissement(IdEtablissement)
);

------------------------------------------------------------
-- Table: Diplomes
------------------------------------------------------------
CREATE TABLE Diplomes(
	IdDiplome           NUMBER NOT NULL ,
	DesignationDiplome  VARCHAR2 (100) NOT NULL  ,
	CONSTRAINT Diplomes_PK PRIMARY KEY (IdDiplome)
);

------------------------------------------------------------
-- Table: Formations
------------------------------------------------------------
CREATE TABLE Formations(
	IdFormations                NUMBER NOT NULL ,
	SpecialiteFormation         VARCHAR2 (100) NOT NULL  ,
	OptionFormation             VARCHAR2 (100)  ,
	-- Date
	DateDebutFormation          VARCHAR(50)   ,
	DateFinFormation            VARCHAR(50)  ,
	MentionObtenu               VARCHAR2 (100)  ,
	IdDiplome                   NUMBER(10,0)   ,
	IdEtablissement		 		NUMBER(10,0)   ,
	IdEtablissementPedagogique   NUMBER(10,0)   ,  
	CONSTRAINT Formations_PK PRIMARY KEY (IdFormations)
	,CONSTRAINT Formations_Diplomes_FK FOREIGN KEY (IdDiplome) REFERENCES Diplomes(IdDiplome)
	,CONSTRAINT Formations_Etablissement_FK FOREIGN KEY (IdEtablissement) REFERENCES Etablissement(IdEtablissement)
);
--,CONSTRAINT Formations_EtablissementPe_FK FOREIGN KEY (IdEtablissementPedagogique) REFERENCES EtablissementPedagogique(IdEtablissementPedagogique)

------------------------------------------------------------
-- Table: CompetencesProjetExperience
------------------------------------------------------------
CREATE TABLE CompetencesProjetExperience(
	IdCompetence                 NUMBER(10,0)  NOT NULL  ,
	IdProjet                     NUMBER(10,0)  NOT NULL  ,
	IdExperiencePro              NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT CompetencesProjetExperience_PK PRIMARY KEY (IdCompetence,IdProjet,IdExperiencePro)
	,CONSTRAINT CompetencesProjetExperien_FK FOREIGN KEY (IdCompetence) REFERENCES Competences(IdCompetence)
	,CONSTRAINT CompetencesProjetExperienc_FK FOREIGN KEY (IdProjet) REFERENCES Projets(IdProjet)
	,CONSTRAINT CompetencesProjetExperience_FK FOREIGN KEY (IdExperiencePro) REFERENCES ExperiencesProfessionnelles(IdExperiencePro)
);


------------------------------------------------------------
-- Table: ExperienceTypeExperience
------------------------------------------------------------
CREATE TABLE ExperienceTypeExperience(
	IdTypeExperiencePro  NUMBER(10,0)  NOT NULL  ,
	IdExperiencePro      NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT ExperienceTypeExperience_PK PRIMARY KEY (IdTypeExperiencePro,IdExperiencePro)
	,CONSTRAINT ExperienceTypeExperienc_FK FOREIGN KEY (IdTypeExperiencePro) REFERENCES TypeExperienceProfessionnelle(IdTypeExperiencePro)
	,CONSTRAINT ExperienceTypeExperience_FK FOREIGN KEY (IdExperiencePro) REFERENCES ExperiencesProfessionnelles(IdExperiencePro)
);


------------------------------------------------------------
-- Table: LoisirsCandidat
------------------------------------------------------------
CREATE TABLE LoisirsCandidat(
	IdLoisir       NUMBER(10,0)  NOT NULL  ,
	IdCandidat     NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT LoisirsCandidat_PK PRIMARY KEY (IdLoisir,IdCandidat)
	,CONSTRAINT LoisirsCandidat_Loisirs_FK FOREIGN KEY (IdLoisir) REFERENCES Loisirs(IdLoisir)
	,CONSTRAINT LoisirsCandidat_Candidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);


------------------------------------------------------------
-- Table: LanguesCandidat
------------------------------------------------------------
CREATE TABLE LanguesCandidat(
	IdLangue       NUMBER(10,0)  NOT NULL  ,
	IdCandidat     NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT LanguesCandidat_PK PRIMARY KEY (IdLangue,IdCandidat)
	,CONSTRAINT LanguesCandidat_Langues_FK FOREIGN KEY (IdLangue) REFERENCES Langues(IdLangue)
	,CONSTRAINT LanguesCandidat_Candidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);


------------------------------------------------------------
-- Table: CompetencesCandidat
------------------------------------------------------------
CREATE TABLE CompetencesCandidat(
	IdCompetence   NUMBER(10,0)  NOT NULL  ,
	IdCandidat     NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT CompetCandidat_PK PRIMARY KEY (IdCompetence,IdCandidat)
	,CONSTRAINT CompetCandidat_Langues_FK FOREIGN KEY (IdCompetence) REFERENCES Competences(IdCompetence)
	,CONSTRAINT CompetCandidat_Candidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);

------------------------------------------------------------
-- Table: EtablissementCandidat
------------------------------------------------------------
CREATE TABLE EtablissementCandidat(
	IdEtablissement  NUMBER(10,0)  NOT NULL  ,
	IdCandidat       NUMBER(10,0)  NOT NULL  ,
	CONSTRAINT EtablissementCandidat_PK PRIMARY KEY (IdEtablissement,IdCandidat)
	,CONSTRAINT EtablissementCandida_FK FOREIGN KEY (IdEtablissement) REFERENCES Etablissement(IdEtablissement)
	,CONSTRAINT EtablissementCandidat_FK FOREIGN KEY (IdCandidat) REFERENCES Candidat(IdCandidat)
);


--------------------------------------------------------- Méta DATA -------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------

------------------------------------------------------------
-- Table: MetaData_Candidat
------------------------------------------------------------
CREATE TABLE MetaData_Candidat(
	Contrainte_IdCandidat             VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_NomCandidat            VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_PrenomCandidat         VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DateNaissanceCandidat  VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_TelephoneCandidat      VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_EmailCandidat          VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_RueCandidat            VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_BoulvardCandidat       VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_AvenueCandidat         VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_VilleCandidat          VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_PaysCandidat           VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_CodePostalCandidat     VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_LienLinkedin           VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_Permis                 VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_SituationFamiliale     VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_CiviliteCandidat       VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_HandicapCandidat       VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_TitreProfil            VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DescriptionProfil      VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_CvCandidat             VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_PhotoCandidat          VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: MetaData_References
------------------------------------------------------------
CREATE TABLE MetaData_References(
	Contrainte_IdReference        VARCHAR2(1500) DEFAULT NULL,
	Contrainte_NomReferent        VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_PrenomReferent     VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_EmailReferent      VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_TelephoneReferent  VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_IdCandidat         VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: MetaData_Loisirs
------------------------------------------------------------
CREATE TABLE MetaData_Loisirs(
	Contrainte_IdLoisir           VARCHAR2(1500) DEFAULT NULL ,
	Contrainte_NomLoisir          VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DescriptionLoisir  VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: MetaData_Langues
------------------------------------------------------------
CREATE TABLE MetaData_Langues(
	Contrainte_IdLangue      VARCHAR2(1500) DEFAULT NULL ,
	Contrainte_Langue        VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_NiveauLangue  VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: MetaData_Competences
------------------------------------------------------------
CREATE TABLE MetaData_Competences(
	Contrainte_IdCompetence  VARCHAR2(1500) DEFAULT NULL ,
	Contrainte_Competence    VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: MetaData_GenreCompetences
------------------------------------------------------------
CREATE TABLE MetaData_GenreCompetences(
	Contrainte_IdGenreCompetence  VARCHAR2(1500) DEFAULT NULL ,
	Contrainte_GenreCompetence    VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_IdCompetence       VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: MetaData_Projets
------------------------------------------------------------
CREATE TABLE MetaData_Projets(
	Contrainte_IdProjet           VARCHAR2(1500) DEFAULT NULL ,
	Contrainte_IntituleProjet     VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DescriptionProjet  VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DateDebutProjet    VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DateFinProjet      VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_IdCandidat         VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: MetaData_TypeExperienceProfessionnelle
------------------------------------------------------------
CREATE TABLE MetaData_TypeExperienceProfessionnelle(
	Contrainte_IdTypeExperiencePro              VARCHAR2(1500) DEFAULT NULL,
	Contrainte_TypeExperienceProfessionnelle    VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: MetaData_Etablissement
------------------------------------------------------------
CREATE TABLE MetaData_Etablissement(
	Contrainte_IdEtablissement     VARCHAR2(1500) DEFAULT NULL ,
	Contrainte_NomEtablissement    VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_VilleEtablissement  VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_PaysEtablissement   VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: M_EtablissementProfessionnelle
------------------------------------------------------------
CREATE TABLE M_EtablissementProfessionnelle(
	Contrainte_IdEtablissement                 VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_IdEtablissementPro  			   VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DepartementEtablissement        VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_NomEtablissement                VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_VilleEtablissement              VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_PaysEtablissement               VARCHAR2(1500) DEFAULT NULL
);

------------------------------------------------------------
-- Table: M_ExperiencesProfessionnelles
------------------------------------------------------------
CREATE TABLE M_ExperiencesProfessionnelles(
	Contrainte_IdExperiencePro    			   VARCHAR2(1500) DEFAULT NULL   ,
	Contrainte_IntitulePoste                   VARCHAR2(1500) DEFAULT NULL   ,
	Contrainte_DateDebutExperience             VARCHAR2(1500) DEFAULT NULL   ,
	Contrainte_DateFinExperience               VARCHAR2(1500) DEFAULT NULL   ,
	Contrainte_IdEtablissement                 VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_IdEtablissementPro  	           VARCHAR2(1500) DEFAULT NULL 
);

------------------------------------------------------------
-- Table: M_EtablissementPedagogique
------------------------------------------------------------
CREATE TABLE M_EtablissementPedagogique(
	Contrainte_IdEtablissement             VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_IdEtablissementPedagogique  VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DetailsEtablissement        VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_NomEtablissement            VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_VilleEtablissement          VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_PaysEtablissement           VARCHAR2(1500) DEFAULT NULL 
);

------------------------------------------------------------
-- Table: MetaData_Diplomes
------------------------------------------------------------
CREATE TABLE MetaData_Diplomes(
	Contrainte_IdDiplome           VARCHAR2(1500) DEFAULT NULL ,
	Contrainte_DesignationDiplome  VARCHAR2(1500) DEFAULT NULL ,
);

------------------------------------------------------------
-- Table: MetaData_Formations
------------------------------------------------------------
CREATE TABLE MetaData_Formations(
	Contrainte_IdFormations                VARCHAR2(1500) DEFAULT NULL ,
	Contrainte_SpecialiteFormation         VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_OptionFormation             VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_DateDebutFormation          VARCHAR2(1500) DEFAULT NULL   ,
	Contrainte_DateFinFormation            VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_MentionObtenu               VARCHAR2(1500) DEFAULT NULL  ,
	Contrainte_IdDiplome                   VARCHAR2(1500) DEFAULT NULL   ,
	Contrainte_IdEtablissement		 	   VARCHAR2(1500) DEFAULT NULL   ,
	Contrainte_IdEtablissementPedagogique  VARCHAR2(1500) DEFAULT NULL
);
--,CONSTRAINT Formations_EtablissementPe_FK FOREIGN KEY (IdEtablissementPedagogique) REFERENCES EtablissementPedagogique(IdEtablissementPedagogique)