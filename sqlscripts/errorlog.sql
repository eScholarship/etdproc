CREATE TABLE  ErrorLog (
	 Id  INTEGER NOT NULL AUTO_INCREMENT,
	 message   nvarchar (100) NULL,
	 detail   nvarchar (1000) NULL,
	 packageId  int  NULL, 
	 errorTime   datetime  NOT NULL DEFAULT CURRENT_TIMESTAMP,
	 FOREIGN KEY( packageId ) REFERENCES  Packages  ( Id ),
PRIMARY KEY  
(
	 Id  ASC
));