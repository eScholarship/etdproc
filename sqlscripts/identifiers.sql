

CREATE TABLE  Identifiers(
	 Id  INTEGER NOT NULL  AUTO_INCREMENT,
	 packageId   int  NOT NULL,
	 isbn   nvarchar (100) NOT NULL,
	 escholId  nvarchar (100)  NULL,
	 merrittId  nvarchar (100)  NULL,
	 additionalIds json NULL,
	 lastUpdated   datetime  NOT NULL DEFAULT CURRENT_TIMESTAMP,
	 isInvalid   bit  NOT NULL DEFAULT 0,
	 FOREIGN KEY( packageId ) REFERENCES  Packages  ( Id ),
PRIMARY KEY   
(
	 Id  ASC
));