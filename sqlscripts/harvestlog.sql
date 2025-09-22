

CREATE TABLE harvestLog (
    identifier VARCHAR(50) NOT NULL,
    datestamp TIMESTAMP  NOT NULL,
    -- other columns go here
    rawvalue TEXT NOT NULL,
    packageId int NULL,
    attrs JSON NULL,
    isProcessed bit NOT NULL DEFAULT 0,
    actionTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (identifier, datestamp)
);