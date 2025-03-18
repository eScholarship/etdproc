
CREATE TABLE ActionLog(
	Id INTEGER NOT NULL AUTO_INCREMENT,
	name nvarchar(100) NULL,
	packageId int NOT NULL,
	actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(packageId) REFERENCES Packages (Id),
	PRIMARY KEY  
(
	Id ASC
));


