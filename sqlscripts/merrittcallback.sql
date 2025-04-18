
CREATE TABLE MerrittCallbacks(
	Id INTEGER NOT NULL AUTO_INCREMENT,
	jid nvarchar(30) NULL,
	callbackdata  json NULL,
	created datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
	isProcessed   bit  NOT NULL DEFAULT 0,
	PRIMARY KEY  
(
	Id ASC
));


