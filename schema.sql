create table flights
(
	flightId int unsigned,
	arrivalId char[4],
	departureId char[4],
	airlineCode char[2],
	flightNumber int,
	departure_local DATETIME,
	arrival_local DATETIME
);