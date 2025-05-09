
CREATE TABLE Queues(
	Id INTEGER NOT NULL AUTO_INCREMENT,
	packageId int NOT NULL,
	queuename  nvarchar (20) NOT NULL  DEFAULT 'fetch',
	actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(packageId) REFERENCES Packages (Id),
	PRIMARY KEY  
(
	Id ASC
));