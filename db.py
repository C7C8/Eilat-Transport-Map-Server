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


def get_flights():
    """Get most recent 100 flights from the database"""
    with get_db() as cursor:
        cursor.execute("SELECT flightId, arrivalId, departureId, airlineCode, flightNumber, departure_local, arrival_Local FROM flights ORDER BY arrival_local LIMIT 100")
        res = cursor.fetchall()
        if res is None:
            return None

        flights = []
        airports = {
            "ETH": "Eilat Airport",
            "ETM": "Ramon Airport",
            "VDA": "Ovda Airport"
        }
        return list(map(lambda flight: {
            "flightId": flight[0],
            "arrivalId": flight[1],
            "arrival": airports[flight[1]],
            "departureId": flight[2],
            "airlineCode": flight[3],
            "flightNumber": flight[4],
            "departure_local": flight[5].timestamp(),
            "arrival_local": flight[6].timestamp()
        }, res))
