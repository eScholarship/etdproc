
CREATE TABLE  Packages(
	 Id  INTEGER NOT NULL  AUTO_INCREMENT,
	 pubnum   nvarchar (20) unique NOT NULL,
	 zipname   nvarchar (200) NULL,
	 currentstatus  nvarchar (20) NULL,
	 campusId  int  NULL, 
	 fileattrs  json NULL,
	 gwattrs  json NULL,
	 xmlattrs  json NULL,
	 computedattrs  json NULL,
	 escholinfo  json NULL,
	 merrittinfo  json NULL,
	 silsinfo  json NULL,
	 lastUpdated   datetime  NOT NULL DEFAULT CURRENT_TIMESTAMP,
	 isInvalid   bit  NOT NULL DEFAULT 0,
	 FOREIGN KEY( campusId ) REFERENCES  Campuses  ( Id ),
PRIMARY KEY   
(
	 Id  ASC
));
