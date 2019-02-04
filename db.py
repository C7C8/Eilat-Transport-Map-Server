import pymysql

from conf import conf


def get_db():
    """Get a DB cursor, because persistent DB connections = bad"""
    connection = pymysql.connect(**(conf()["db"]))
    return connection.cursor()


def save_flights(flights):
    """Insert a list of flights to the DB; won't insert duplicates (detected by flight ID)"""
    with get_db() as cursor:
        for flight in flights:
            try:
                cursor.execute("INSERT INTO flights (flightId, arrivalId, departureId, airlineCode, flightNumber, departure_local, arrival_local)"
                               " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                               (flight["flightId"],
                                flight["arrivalId"],
                                flight["departureId"],
                                flight["airlineCode"],
                                flight["flightNumber"],
                                flight["departure_local"],
                                flight["arrival_local"]))
            except pymysql.IntegrityError:
                # Ignore duplicate flight entries
                continue

        cursor.connection.commit()


def save_airlines(airlines):
    """Insert a list of airlines to the DB; won't insert duplicates (detected by IATA)"""
    with get_db() as cursor:
        for airline in airlines:
            try:
                cursor.execute("INSERT INTO airlines (name, fs, iata) VALUES (%s, %s, %s)",
                               (airline["name"], airline["fs"], airline["iata"]))
            except pymysql.IntegrityError:
                # Ignore duplicate airline entries
                continue

        cursor.connection.commit()


def save_airports(airports):
    """Insert a list of airports to the DB; won't insert duplicates (detected by IATA)"""
    with get_db() as cursor:
        for airport in airports:
            try:
                cursor.execute("INSERT INTO airports (name, city, country, fs, iata) VALUES (%s, %s, %s, %s, %s)",
                               (airport["name"], airport["city"], airport["country"], airport["fs"], airport["iata"]))
            except pymysql.IntegrityError:
                # Ignore duplicate airport entries
                continue

        cursor.connection.commit()


def get_flights():
    """Get most recent 100 flights from the database"""
    with get_db() as cursor:
        cursor.execute("SELECT airlineCode,"
                       "flightNumber, "
                       "arrival_local, "
                       "airlines.name as airline, "
                       "airports.name as airport, "
                       "airports.city, "
                       "airports.country "
                       "FROM flights, airlines, airports "
                       "WHERE flights.airlineCode = airlines.iata "
                       "AND flights.departureId = airports.iata")
        res = cursor.fetchall()
        if res is None:
            return None

        return list(map(lambda flight: {
            "airlineCode": str(flight[0]),
            "flightNumber": int(flight[1]),
            "arrival": flight[2].timestamp(),
            "airline": str(flight[3]),
            "srcAirport": str(flight[4]),
            "srcCity": str(flight[5]),
            "srcCountry": str(flight[6])
        }, res))

