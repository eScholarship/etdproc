

CREATE TABLE oaiOverride (
	Id INTEGER NOT NULL AUTO_INCREMENT,
    packageId int Unique NOT NULL,
	marcattrs JSON NOT NULL,
    escholattrs JSON NOT NULL,
    actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(packageId) REFERENCES Packages (Id),
    PRIMARY KEY  
	(
		Id ASC
	));
