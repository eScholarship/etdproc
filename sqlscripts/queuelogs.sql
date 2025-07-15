
CREATE TABLE QueueLogs(
	Id INTEGER NOT NULL AUTO_INCREMENT,
	packageId int NOT NULL,
	queuename  nvarchar (20) NOT NULL,
	actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(packageId) REFERENCES Packages (Id),
	PRIMARY KEY  
(
	Id ASC
));