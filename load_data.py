import json
import uuid

from app.models import Location
from app.database import init_db, get_db


def load_data():
    init_db()
    generator = get_db()
    db = next(generator)

    try:
        with open('data.json') as json_data:
            data = json.load(json_data)
            for item in data['locations']:

                db_item = {
                    'latitude': float(item['latitude']),
                    'longitude': float(item['longitude']),
                    'time': int(item['time']),
                    'source': 'json_bin',
                    'trip': "South America",
                }

                db_location = Location(**db_item)
                db.add(db_location)
            db.commit()
    finally:
        db.close()


def print_all():
    generator = get_db()
    db = next(generator)

    try:
        locations = db.query(Location).all()
        print(f'Number of locations: {len(locations)}')
        # for location in locations:
            # print(location.id, location.latitude, location.longitude, location.time, location.source, location.trip)
    finally:
        db.close()


if __name__ == "__main__":
    load_data()
    print_all()