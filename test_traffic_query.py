from Traffic_Backend.db_config import SessionLocal
from Traffic_Backend.models import TrafficDynamics, RoadNetwork
from sqlalchemy import func

db = SessionLocal()

# Check how many TrafficDynamics entries exist
count = db.query(TrafficDynamics).count()
print(f"Total TrafficDynamics entries: {count}")

# Try the subquery approach
subquery = db.query(
    TrafficDynamics.road_segment_id,
    func.max(TrafficDynamics.timestamp).label('max_timestamp')
).group_by(TrafficDynamics.road_segment_id).subquery()

entries = db.query(TrafficDynamics).join(
    subquery,
    (TrafficDynamics.road_segment_id == subquery.c.road_segment_id) &
    (TrafficDynamics.timestamp == subquery.c.max_timestamp)
).all()

print(f"Retrieved entries from latest timestamps: {len(entries)}")

if entries:
    entry = entries[0]
    print(f"\nFirst entry:")
    print(f"  road_segment_id: {entry.road_segment_id}")
    print(f"  timestamp: {entry.timestamp}")
    print(f"  vehicle_count: {entry.vehicle_count}")
    
    # Try to get the road
    segment = db.query(RoadNetwork).filter(RoadNetwork.id == entry.road_segment_id).first()
    if segment:
        print(f"  road name: {segment.name}")
        print(f"  geometry length: {len(segment.geometry) if segment.geometry else 0}")

db.close()
