
CREATE TABLE EscholRequests(
	Id INTEGER NOT NULL AUTO_INCREMENT,
	packageId int NOT NULL,
	pubnum  nvarchar (20) NOT NULL,
	escholId  nvarchar (20) NOT NULL,
	depositrequest  json NULL,
	depositresponse  json NULL,
	actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(packageId) REFERENCES Packages (Id),
	PRIMARY KEY  
(
	Id ASC
));