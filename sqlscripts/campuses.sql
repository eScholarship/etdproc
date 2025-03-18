CREATE TABLE  Campuses(
	 Id  INTEGER NOT NULL  AUTO_INCREMENT,
	 code   nvarchar (10) unique NOT NULL,
	 namesuffix   nvarchar(40) NOT NULL,
	 pqcode nvarchar(10) unique NOT NULL,
	 instloc   nvarchar(40) NOT NULL,
	 escholunit   nvarchar(40) NOT NULL,
	 merrittcol   nvarchar(40) NOT NULL,
	 nameinmarc   nvarchar(100) NOT NULL,
	 isInvalid   bit  NOT NULL  DEFAULT 0,
PRIMARY KEY   
(
	 Id  ASC
));