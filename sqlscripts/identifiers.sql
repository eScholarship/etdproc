

CREATE TABLE  Identifiers(
	 Id  INTEGER NOT NULL  AUTO_INCREMENT,
	 packageId   int  NOT NULL,
	 idtype   nvarchar (30) NOT NULL,
	 idvalue  nvarchar (100)  NULL,
	 lastUpdated   datetime  NOT NULL DEFAULT CURRENT_TIMESTAMP,
	 isInvalid   bit  NOT NULL DEFAULT 0,
	 FOREIGN KEY( packageId ) REFERENCES  Packages  ( Id ),
PRIMARY KEY   
(
	 Id  ASC
));