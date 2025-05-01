
CREATE TABLE EscholRequests(
	Id INTEGER NOT NULL AUTO_INCREMENT,
	packageId int NOT NULL,
	pubnum  nvarchar (30) NOT NULL,
	escholId  nvarchar (30) NOT NULL,
	depositrequest  json NULL,
	depositresponse  nvarchar (1000) NULL,
	actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(packageId) REFERENCES Packages (Id),
	PRIMARY KEY  
(
	Id ASC
));