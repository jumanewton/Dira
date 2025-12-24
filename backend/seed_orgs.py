#!/usr/bin/env python3
"""
Seed initial organisations into the database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from models import Organisation
import crud

def seed_organisations():
    """Seed initial organisations"""
    
    print("🌱 Seeding organisations...")
    
    organisations = [
        Organisation(
            name="City Water Department",
            type="utility",
            contact_email="water@city.gov",
            contact_api="",
            facilities=["Water Treatment Plant A", "Distribution Center"]
        ),
        Organisation(
            name="Municipal Public Works",
            type="government",
            contact_email="publicworks@city.gov",
            contact_api="",
            facilities=["Roads Department", "Infrastructure Maintenance"]
        ),
        Organisation(
            name="City Power Company",
            type="utility",
            contact_email="support@citypower.com",
            contact_api="",
            facilities=["Power Station 1", "Grid Control Center"]
        ),
        Organisation(
            name="Department of Public Safety",
            type="government",
            contact_email="safety@city.gov",
            contact_api="",
            facilities=["Emergency Response Center"]
        ),
        Organisation(
            name="Waste Management Services",
            type="utility",
            contact_email="info@wastemanagement.com",
            contact_api="",
            facilities=["Collection Center", "Recycling Plant"]
        )
    ]
    
    created_count = 0
    for org in organisations:
        try:
            # Check if organisation already exists
            existing_orgs = crud.get_all_organisations()
            exists = any(e.name == org.name for e in existing_orgs)
            
            if not exists:
                org_id = crud.create_organisation(org)
                print(f"   ✅ Created: {org.name} (ID: {org_id})")
                created_count += 1
            else:
                print(f"   ⏭️  Skipped: {org.name} (already exists)")
        except Exception as e:
            print(f"   ❌ Failed to create {org.name}: {e}")
    
    print(f"\n✅ Seeding complete! Created {created_count} organisations")
    
    # List all organisations
    all_orgs = crud.get_all_organisations()
    print(f"\n📋 Total organisations in database: {len(all_orgs)}")
    for org in all_orgs:
        print(f"   - {org.name} ({org.type})")

if __name__ == "__main__":
    seed_organisations()
