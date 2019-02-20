from pygtfs import Schedule, append_feed
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from conf import conf
from transit_util import Stop

lat_bounds = {
    'high': 29.596243,
    'low': 29.515590,
}

lon_bounds = {
    'high': 34.998930,
    'low': 34.900423
}
print("Creating Engine...", end="")
engine = None
try:
    DB = conf()['db']
    engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(DB['user'], DB['password'], DB['host'], DB['database']))
    automap = automap_base()
    automap.prepare(engine, reflect=True)
except Exception as e:
    print("Failed:", e)
    exit(-1)
print("Done")


def gtfs_import():
    schedule = Schedule("gtfs.sqlite")
    append_feed(schedule, "israel-gtfs.zip")


def get_stops():
    print("Loading stops from GTFS...", end="")
    stop_table = automap.classes.gtfs_stops
    Session = sessionmaker(bind=engine)
    session = Session()

    query = session.query(stop_table).filter(stop_table.stop_lon >= lon_bounds['low'],
                                             stop_table.stop_lon <= lon_bounds['high'],
                                             stop_table.stop_lat >= lat_bounds['low'],
                                             stop_table.stop_lat <= lat_bounds['high'])

    eilat_stops = {}
    for stop in query:
        S = Stop()
        S.name = stop.stop_name
        S.code = stop.stop_code
        S.longitude = stop.stop_lon
        S.latitude = stop.stop_lat
        S.description = stop.stop_desc
        eilat_stops[S.code] = S
    print("Done")
    return eilat_stops


def agency_by_id(agency_id):
    # print("Getting Agency Info for Agency ID", agency_id)
    agency_table = automap.classes.gtfs_agency
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(agency_table).filter(agency_table.agency_id == agency_id)
    for agency in query:
        return agency.agency_name, agency.agency_url


if __name__ == '__main__':
    get_stops()
