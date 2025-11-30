#!/usr/bin/env python3
"""
Quick script to create an admin user for testing
"""

import sys
from sqlalchemy.orm import Session
from Traffic_Backend.db_config import SessionLocal
from Traffic_Backend.auth import create_user
import Traffic_Backend.models as models

def create_admin_user():
    """Create a test admin user"""
    db: Session = SessionLocal()
    try:
        # Check if testadmin already exists
        existing = db.query(models.User).filter(models.User.username == "testadmin").first()
        if existing:
            print("✅ Admin user 'testadmin' already exists")
            # Update to ensure admin role
            if 'admin' not in (existing.roles or ''):
                existing.roles = 'admin,user'
                db.commit()
                print("   Updated to admin role")
            return True
        
        # Create new admin user
        user = create_user(
            db=db,
            username="testadmin",
            password="testpass123",
            email="admin@test.com",
            roles="admin,user"
        )
        print(f"✅ Created admin user: {user.username}")
        print(f"   Password: testpass123")
        print(f"   Roles: {user.roles}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_admin_user()
    sys.exit(0 if success else 1)
