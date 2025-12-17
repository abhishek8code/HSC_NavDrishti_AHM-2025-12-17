from Traffic_Backend.db_config import SessionLocal
from Traffic_Backend.models import RoadNetwork
import json

db = SessionLocal()
road = db.query(RoadNetwork).first()
geom = json.loads(road.geometry)
print(f'Road: {road.name}')
print(f'Coordinates: {geom["coordinates"]}')
print(f'Number of points: {len(geom["coordinates"])}')
db.close()
