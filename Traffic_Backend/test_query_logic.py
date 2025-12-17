import sys
sys.path.insert(0, '.')

from db_config import SessionLocal
from models import TrafficDynamics, RoadNetwork
from sqlalchemy import func
import json

db = SessionLocal()

# Test 1: Count records
print(f"=== Direct Query Test ===")
print(f"RoadNetwork count: {db.query(RoadNetwork).count()}")
print(f"TrafficDynamics count: {db.query(TrafficDynamics).count()}")

# Test 2: Try the subquery logic
print(f"\n=== Subquery Test ===")
subquery = db.query(
    TrafficDynamics.road_segment_id,
    func.max(TrafficDynamics.timestamp).label('max_timestamp')
).group_by(TrafficDynamics.road_segment_id).subquery()

entries = db.query(TrafficDynamics).join(
    subquery,
    (TrafficDynamics.road_segment_id == subquery.c.road_segment_id) &
    (TrafficDynamics.timestamp == subquery.c.max_timestamp)
).all()

print(f"Latest traffic entries retrieved: {len(entries)}")
if entries:
    print(f"First entry: road_segment_id={entries[0].road_segment_id}, vehicle_count={entries[0].vehicle_count}")
    
    # Try to get the road
    road = db.query(RoadNetwork).filter(RoadNetwork.id == entries[0].road_segment_id).first()
    if road:
        print(f"Road name: {road.name}")
        print(f"Geometry length: {len(road.geometry) if road.geometry else 'None'}")
        if road.geometry:
            try:
                geom = json.loads(road.geometry)
                print(f"Geometry type: {geom.get('type')}")
                print(f"Coordinates count: {len(geom.get('coordinates', []))}")
            except Exception as e:
                print(f"Error parsing geometry: {e}")
    else:
        print("Road not found!")

db.close()
