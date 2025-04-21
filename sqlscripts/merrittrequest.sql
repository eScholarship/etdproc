
CREATE TABLE MerrittRequests(
	Id INTEGER NOT NULL AUTO_INCREMENT,
	packageId int NOT NULL,
	request  json NULL,
	response  json NULL,
	currentstatus  nvarchar (20) NULL,
	actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(packageId) REFERENCES Packages (Id),
	PRIMARY KEY  
(
	Id ASC
));