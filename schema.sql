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

# VIEWS

CREATE OR REPLACE VIEW flights_human_readable AS (
  SELECT airlineCode,
         flightNumber,
         arrival_local,
         airlines.name as airline,
         airports.name as airport,
         airports.city,
         airports.country
  FROM flights, airlines, airports
  WHERE flights.airlineCode = airlines.iata
    AND flights.departureId = airports.iata
  ORDER BY arrival_local
  LIMIT 250
);

CREATE OR REPLACE VIEW flights_hourly_by_day AS (
  SELECT
    COUNT(*)                          AS cnt,
    HOUR(arrival_local)               AS f_hour,
    (WEEKDAY(arrival_local) + 1) % 7  AS f_day
  FROM flights
  GROUP BY f_hour, f_day
  ORDER BY f_day ASC, f_hour ASC
);

