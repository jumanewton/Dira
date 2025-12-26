#!/usr/bin/env python3
"""
Seed initial Kenyan organisations into the database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from models import Organisation
import crud

def seed_organisations():
    """Seed initial Kenyan organisations"""
    
    print("Seeding Kenyan organisations...")
    
    organisations = [
        Organisation(
            name="Nairobi City Water & Sewerage Company (NCWSC)",
            type="utility",
            # contact_email="info@nairobiwater.co.ke",
            contact_email="ccs00056021@student.maseno.ac.ke", # Test email
            contact_api="",
            facilities=["Kabete Water Treatment Works", "Dandora Estate Sewerage Treatment Plant"]
        ),
        Organisation(
            name="Kenya Urban Roads Authority (KURA)",
            type="government",
            # contact_email="info@kura.go.ke",
            contact_email="ccs00056021@student.maseno.ac.ke", # Test email
            contact_api="",
            facilities=["Nairobi Region Office", "Road Maintenance Depot"]
        ),
        Organisation(
            name="Kenya Power (KPLC)",
            type="utility",
            # contact_email="customercare@kplc.co.ke",
            contact_email="ccs00056021@student.maseno.ac.ke", # Test email
            contact_api="",
            facilities=["Embakasi Substation", "Stima Plaza Control Centre"]
        ),
        Organisation(
            name="National Police Service (NPS)",
            type="government",
            # contact_email="info@nationalpolice.go.ke",
            contact_email="ccs00056021@student.maseno.ac.ke", # Test email
            contact_api="",
            facilities=["Central Police Station", "Traffic Headquarters"]
        ),
        Organisation(
            name="NEMA (National Environment Management Authority)",
            type="government",
            # contact_email="info@nema.go.ke",
            contact_email="ccs00056021@student.maseno.ac.ke", # Test email
            contact_api="",
            facilities=["Headquarters", "Waste Compliance Unit"]
        ),
        Organisation(
            name="Nairobi County Government",
            type="government",
            # contact_email="info@nairobi.go.ke",
            contact_email="ccs00056021@student.maseno.ac.ke", # Test email
            contact_api="",
            facilities=["City Hall", "Public Health Department"]
        )
    ]
    
    created_count = 0
    updated_count = 0
    for org in organisations:
        # Check if exists
        existing = crud.get_organisations_by_type(org.type)
        exists = False
        existing_id = None
        for e in existing:
            if e.name == org.name:
                exists = True
                existing_id = e.id
                break
        
        if not exists:
            crud.create_organisation(org)
            print(f"Created: {org.name}")
            created_count += 1
        else:
            # Update email for testing
            crud.update_organisation(existing_id, contact_email=org.contact_email)
            print(f"Updated email for: {org.name}")
            updated_count += 1
            
    print(f"\n Seeding complete! Created {created_count}, Updated {updated_count} organisations")

if __name__ == "__main__":
    seed_organisations()
