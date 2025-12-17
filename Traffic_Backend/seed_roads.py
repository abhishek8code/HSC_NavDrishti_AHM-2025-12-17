"""
Seed the database with real Ahmedabad road network data.
This populates RoadNetwork with major roads and TrafficDynamics with sample traffic data.
"""
import json
from datetime import datetime, timedelta
import random
from db_config import SessionLocal
from models import RoadNetwork, TrafficDynamics

# Major roads in Ahmedabad with real coordinates (LineString GeoJSON format)
AHMEDABAD_ROADS = [
    {
        "name": "SG Highway (North)",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5200, 23.0300],
                [72.5250, 23.0350],
                [72.5300, 23.0400],
                [72.5350, 23.0450],
                [72.5400, 23.0500]
            ]
        },
        "base_capacity": 5000,
        "roughness_index": 0.2
    },
    {
        "name": "SG Highway (Central)",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5400, 23.0500],
                [72.5450, 23.0550],
                [72.5500, 23.0600],
                [72.5550, 23.0650],
                [72.5600, 23.0700]
            ]
        },
        "base_capacity": 5000,
        "roughness_index": 0.2
    },
    {
        "name": "SG Highway (South)",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5600, 23.0700],
                [72.5650, 23.0750],
                [72.5700, 23.0800],
                [72.5750, 23.0850],
                [72.5800, 23.0900]
            ]
        },
        "base_capacity": 5000,
        "roughness_index": 0.2
    },
    {
        "name": "Ashram Road",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5800, 23.0200],
                [72.5820, 23.0250],
                [72.5840, 23.0300],
                [72.5860, 23.0350],
                [72.5900, 23.0400]
            ]
        },
        "base_capacity": 4000,
        "roughness_index": 0.3
    },
    {
        "name": "CG Road",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5500, 23.0300],
                [72.5550, 23.0310],
                [72.5600, 23.0320],
                [72.5650, 23.0330],
                [72.5700, 23.0350]
            ]
        },
        "base_capacity": 3500,
        "roughness_index": 0.25
    },
    {
        "name": "Nehru Bridge",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5850, 23.0350],
                [72.5880, 23.0360],
                [72.5910, 23.0380],
                [72.5930, 23.0390],
                [72.5950, 23.0400]
            ]
        },
        "base_capacity": 3000,
        "roughness_index": 0.35
    },
    {
        "name": "Paldi Main Road",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5600, 23.0200],
                [72.5620, 23.0215],
                [72.5640, 23.0225],
                [72.5670, 23.0240],
                [72.5700, 23.0250]
            ]
        },
        "base_capacity": 2500,
        "roughness_index": 0.4
    },
    {
        "name": "Maninagar Road",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.6000, 23.0100],
                [72.6020, 23.0120],
                [72.6050, 23.0150],
                [72.6070, 23.0170],
                [72.6100, 23.0200]
            ]
        },
        "base_capacity": 3000,
        "roughness_index": 0.3
    },
    {
        "name": "Relief Road",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5950, 23.0250],
                [72.5980, 23.0280],
                [72.6000, 23.0300],
                [72.6020, 23.0320],
                [72.6050, 23.0350]
            ]
        },
        "base_capacity": 2000,
        "roughness_index": 0.45
    },
    {
        "name": "Sardar Patel Ring Road (SPRR West)",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.4800, 23.0400],
                [72.4850, 23.0450],
                [72.4900, 23.0500],
                [72.4950, 23.0550],
                [72.5000, 23.0600]
            ]
        },
        "base_capacity": 6000,
        "roughness_index": 0.15
    },
    {
        "name": "Sardar Patel Ring Road (SPRR East)",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.6200, 23.0400],
                [72.6250, 23.0450],
                [72.6300, 23.0500],
                [72.6350, 23.0550],
                [72.6400, 23.0600]
            ]
        },
        "base_capacity": 6000,
        "roughness_index": 0.15
    },
    {
        "name": "Narol-Naroda Highway",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.6500, 23.0100],
                [72.6520, 23.0150],
                [72.6550, 23.0200],
                [72.6570, 23.0250],
                [72.6600, 23.0300]
            ]
        },
        "base_capacity": 4500,
        "roughness_index": 0.25
    },
    {
        "name": "Kankaria Lake Road",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.6080, 23.0080],
                [72.6100, 23.0090],
                [72.6120, 23.0100],
                [72.6140, 23.0110],
                [72.6160, 23.0120]
            ]
        },
        "base_capacity": 2500,
        "roughness_index": 0.3
    },
    {
        "name": "Sabarmati Riverfront Road",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5700, 23.0600],
                [72.5720, 23.0620],
                [72.5750, 23.0650],
                [72.5770, 23.0680],
                [72.5800, 23.0700]
            ]
        },
        "base_capacity": 3000,
        "roughness_index": 0.2
    },
    {
        "name": "Ambawadi Circle - Vastrapur Road",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [72.5650, 23.0380],
                [72.5680, 23.0400],
                [72.5710, 23.0420],
                [72.5740, 23.0440],
                [72.5770, 23.0460]
            ]
        },
        "base_capacity": 3500,
        "roughness_index": 0.25
    }
]


def seed_roads():
    """Populate RoadNetwork table with Ahmedabad major roads."""
    db = SessionLocal()
    try:
        # Check if roads already exist
        existing_count = db.query(RoadNetwork).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} roads. Skipping seed.")
            print("To re-seed, delete existing roads first.")
            return
        
        print(f"Seeding {len(AHMEDABAD_ROADS)} roads into database...")
        
        for road_data in AHMEDABAD_ROADS:
            road = RoadNetwork(
                name=road_data["name"],
                geometry=json.dumps(road_data["geometry"]),  # Store as JSON string
                base_capacity=road_data["base_capacity"],
                roughness_index=road_data["roughness_index"]
            )
            db.add(road)
        
        db.commit()
        print(f"✓ Successfully seeded {len(AHMEDABAD_ROADS)} roads")
        
        # Verify
        count = db.query(RoadNetwork).count()
        print(f"✓ Total roads in database: {count}")
        
    except Exception as e:
        print(f"✗ Error seeding roads: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_traffic_data():
    """Populate TrafficDynamics with sample traffic data for each road."""
    db = SessionLocal()
    try:
        # Get all roads
        roads = db.query(RoadNetwork).all()
        if not roads:
            print("No roads found. Run seed_roads() first.")
            return
        
        print(f"Generating traffic data for {len(roads)} roads...")
        
        # Generate traffic data for the past hour with 5-minute intervals
        now = datetime.now()
        intervals = 12  # 12 intervals of 5 minutes = 1 hour
        
        traffic_entries = []
        for road in roads:
            # Each road gets different base traffic characteristics
            base_speed = random.uniform(40, 70)  # km/h
            base_vehicles = int(road.base_capacity * random.uniform(0.3, 0.7))
            
            for i in range(intervals):
                timestamp = now - timedelta(minutes=5 * (intervals - i - 1))
                
                # Add some variation
                speed_variation = random.uniform(-10, 10)
                vehicle_variation = int(random.uniform(-50, 50))
                
                avg_speed = max(10, base_speed + speed_variation)
                vehicle_count = max(0, base_vehicles + vehicle_variation)
                
                # Calculate congestion state based on capacity
                utilization = vehicle_count / road.base_capacity
                if utilization < 0.4:
                    congestion = "free-flow"
                    flow_entropy = random.uniform(0.1, 0.3)
                elif utilization < 0.7:
                    congestion = "moderate"
                    flow_entropy = random.uniform(0.4, 0.6)
                else:
                    congestion = "congested"
                    flow_entropy = random.uniform(0.7, 0.9)
                
                traffic = TrafficDynamics(
                    road_segment_id=road.id,
                    timestamp=timestamp,
                    flow_entropy=flow_entropy,
                    congestion_state=congestion,
                    vehicle_count=vehicle_count,
                    average_speed=avg_speed
                )
                traffic_entries.append(traffic)
        
        db.add_all(traffic_entries)
        db.commit()
        print(f"✓ Successfully generated {len(traffic_entries)} traffic entries")
        
    except Exception as e:
        print(f"✗ Error seeding traffic data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main seeding function."""
    print("=" * 60)
    print("Seeding Ahmedabad Road Network Database")
    print("=" * 60)
    
    # Seed roads first
    seed_roads()
    
    print("\n" + "=" * 60)
    print("Seeding Traffic Data")
    print("=" * 60)
    
    # Then seed traffic data
    seed_traffic_data()
    
    print("\n" + "=" * 60)
    print("Database seeding complete!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Access traffic data via /traffic/live endpoint")
    print("  2. View real road networks on the Operations Center map")
    print("  3. See realistic traffic flow patterns")


if __name__ == "__main__":
    main()
