import sqlalchemy
from pygtfs import Schedule
from sqlalchemy import orm as SQL, MetaData
from sqlalchemy.types import FLOAT

lat = {
    'high': 29.596243,
    'low': 29.515590,
}

lon = {
    'high': 34.998930,
    'low': 34.900423
}


def pygtfs_import():
    sched = Schedule("gtfs.sqlite")
    # append_feed(sched, "israel-gtfs.zip")
    coords_lat = sqlalchemy.Column('stop_lat', FLOAT)
    coords_lon = sqlalchemy.Column('stop_lat', FLOAT)
    stops = sqlalchemy.Table('stops', MetaData(bind=None), coords_lat, coords_lon)

    q = SQL.Query(stops).filter(coords_lon >= lon['low'], coords_lat <= lon['high'])
    sched

# mytable = Table("mytable", metadata,
#                         Column('mytable_id', Integer, primary_key=True),
#                         Column('value', String(50))

# def transitfeed():
#     import transitfeed.transitfeed.schedule
#     schedule = transitfeed.Schedule()
#     schedule.GetStopsInBoundingBox()


if __name__ == '__main__':
    pygtfs_import()
