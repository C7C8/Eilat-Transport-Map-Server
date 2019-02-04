CREATE TABLE flights
(
	flightId 				INTEGER UNSIGNED	PRIMARY KEY,
	arrivalId 			CHAR(4),
	departureId			CHAR(4),
	airlineCode 		CHAR(4),
	flightNumber 		INTEGER,
	departure_local DATETIME,
	arrival_local 	DATETIME,

	FOREIGN KEY airline_fk(airlineCode) REFERENCES airlines(iata),
	FOREIGN KEY airport_dep_fk(departureId) REFERENCES airports(iata),
	FOREIGN KEY airport_arv_fk(arrivalId) REFERENCES airports(iata)
);

CREATE TABLE airlines (
  name						VARCHAR(128)	UNIQUE,
  fs							CHAR(4) 			UNIQUE,
  iata						CHAR(4)				PRIMARY KEY
);

CREATE TABLE airports (
  name						VARCHAR(128)	UNIQUE,
  city						VARCHAR(128),
  country         VARCHAR(128),
  fs							CHAR(4)				UNIQUE,
  iata						CHAR(4)				PRIMARY KEY
);
