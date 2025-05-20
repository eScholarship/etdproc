
CREATE TABLE EscholRequests(
	Id INTEGER NOT NULL AUTO_INCREMENT,
	packageId int unique NOT NULL,
	escholId  nvarchar (30) unique NOT NULL,
	depositrequest  json NULL,
	depositresponse  nvarchar (1000) NULL,
	actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(packageId) REFERENCES Packages (Id),
	PRIMARY KEY  
(
	Id ASC
));