CREATE TABLE settings(
	 Id  INTEGER NOT NULL  AUTO_INCREMENT,
	 settingtype   nvarchar(10)  NOT NULL,
	 field1   nvarchar (20)  NULL,
	 field2   nvarchar (20)  NULL,
	 field3   nvarchar (20)  NULL,
	 field4  nvarchar (20)  NULL,
	 field5  nvarchar (20)  NULL,
	 field6  nvarchar (20)  NULL,
	 info nvarchar (100)  NULL,
	 lastUpdated   datetime  NOT NULL DEFAULT CURRENT_TIMESTAMP,
	 isInvalid   bit  NOT NULL DEFAULT 0,
	PRIMARY KEY  
(
	Id ASC
));