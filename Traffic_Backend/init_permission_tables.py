#!/usr/bin/env python3
"""
Initialize permission request tables in the database.
Run from root directory:
  python Traffic_Backend/init_permission_tables.py
"""
import sys
import os

# Add Traffic_Backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.dirname(backend_dir))

# Import after path is set
from db_config import engine
from models import Base, RoutePermissionRequest, AuditLog

def create_permission_tables():
    """Create permission request and audit log tables"""
    print("📊 Creating permission request tables...")
    
    try:
        # Create only permission-related tables
        RoutePermissionRequest.__table__.create(engine, checkfirst=True)
        print("✓ RoutePermissionRequest table created")
        
        AuditLog.__table__.create(engine, checkfirst=True)
        print("✓ AuditLog table created")
        
        print("\n✅ All permission tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = create_permission_tables()
    sys.exit(0 if success else 1)
