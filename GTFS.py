from pygtfs import Schedule, append_feed
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from transit_util import Stop

lat_bounds = {
    'high': 29.596243,
    'low': 29.515590,
}

lon_bounds = {
    'high': 34.998930,
    'low': 34.900423
}

engine = create_engine('sqlite:///gtfs.sqlite', echo=False)
automap = automap_base()
automap.prepare(engine, reflect=True)


def gtfs_import():
    schedule = Schedule("gtfs.sqlite")
    append_feed(schedule, "israel-gtfs.zip")


def get_stops():
    stop_table = automap.classes.stops
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
    return eilat_stops


def agency_by_id(id):
    agency_table = automap.classes.agency
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(agency_table).filter(agency_table.agency_id == id)



if __name__ == '__main__':
    get_stops()
