#!/usr/bin/env python3
"""
Test CRUD operations for the database layer
"""

import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from models import Organisation, Reporter, Report, ReportRoute, RelatedReport
import crud

def test_crud_operations():
    """Test all CRUD operations"""
    
    print("🧪 Testing CRUD Operations\n")
    
    # Test 1: Create Organisation
    print("1️⃣  Testing Organisation CRUD...")
    org = Organisation(
        name="City Water Department",
        type="utility",
        contact_email="water@city.gov",
        facilities=["Plant A", "Plant B"]
    )
    org_id = crud.create_organisation(org)
    print(f"   ✅ Created organisation: {org_id}")
    
    # Read organisation
    retrieved_org = crud.get_organisation(org_id)
    assert retrieved_org.name == "City Water Department"
    print(f"   ✅ Retrieved organisation: {retrieved_org.name}")
    
    # Update organisation
    crud.update_organisation(org_id, contact_email="newwater@city.gov")
    updated_org = crud.get_organisation(org_id)
    assert updated_org.contact_email == "newwater@city.gov"
    print(f"   ✅ Updated organisation email")
    
    # Get all organisations
    all_orgs = crud.get_all_organisations()
    print(f"   ✅ Retrieved {len(all_orgs)} organisations")
    
    # Test 2: Create Reporter
    print("\n2️⃣  Testing Reporter CRUD...")
    reporter = Reporter(
        name="John Doe",
        email="john@example.com",
        is_anonymous=False
    )
    reporter_id = crud.create_reporter(reporter)
    print(f"   ✅ Created reporter: {reporter_id}")
    
    retrieved_reporter = crud.get_reporter(reporter_id)
    assert retrieved_reporter.email == "john@example.com"
    print(f"   ✅ Retrieved reporter: {retrieved_reporter.name}")
    
    # Test 3: Create Report with Embedding
    print("\n3️⃣  Testing Report CRUD...")
    
    # Create a test embedding (384 dimensions)
    test_embedding = [0.1] * 384
    
    report = Report(
        title="Water Main Break on Elm Street",
        description="Large water main break causing flooding",
        category="infrastructure",
        urgency="high",
        entities={"locations": ["Elm Street"], "organisations": ["City Water"]},
        confidence=0.95,
        status="submitted",
        reporter_id=reporter_id,
        embedding=test_embedding
    )
    report_id = crud.create_report(report)
    print(f"   ✅ Created report with embedding: {report_id}")
    
    retrieved_report = crud.get_report(report_id)
    assert retrieved_report.title == "Water Main Break on Elm Street"
    assert retrieved_report.embedding is not None
    print(f"   ✅ Retrieved report: {retrieved_report.title}")
    print(f"   ✅ Embedding dimension: {len(retrieved_report.embedding)}")
    
    # Update report status
    crud.update_report(report_id, status="routed")
    updated_report = crud.get_report(report_id)
    assert updated_report.status == "routed"
    print(f"   ✅ Updated report status to: {updated_report.status}")
    
    # Test 4: Vector Similarity Search
    print("\n4️⃣  Testing Vector Similarity Search...")
    
    # Create a second similar report
    similar_report = Report(
        title="Water pipe burst near Elm",
        description="Water pipe has burst causing street flooding",
        category="infrastructure",
        urgency="high",
        entities={"locations": ["Elm Street"]},
        status="submitted",
        reporter_id=reporter_id,
        embedding=[0.11] * 384  # Slightly different embedding (similar)
    )
    similar_report_id = crud.create_report(similar_report)
    print(f"   ✅ Created similar report: {similar_report_id}")
    
    # Find duplicates
    duplicates = crud.find_duplicate_reports(
        title=report.title,
        description=report.description,
        embedding=test_embedding,
        threshold=0.95,
        exclude_id=report_id
    )
    print(f"   ✅ Found {len(duplicates)} potential duplicates")
    if duplicates:
        for dup in duplicates:
            print(f"      - {dup['title']} (similarity: {dup['similarity_score']:.3f})")
    
    # Test 5: Report Routes
    print("\n5️⃣  Testing Report Routes...")
    route = ReportRoute(
        report_id=report_id,
        organisation_id=org_id,
        message="Report has been forwarded to your department",
        status="sent"
    )
    route_id = crud.create_report_route(route)
    print(f"   ✅ Created report route: {route_id}")
    
    routes = crud.get_routes_for_report(report_id)
    assert len(routes) > 0
    print(f"   ✅ Retrieved {len(routes)} routes for report")
    
    # Test 6: Related Reports
    print("\n6️⃣  Testing Related Reports...")
    if duplicates:
        related = RelatedReport(
            report_id=report_id,
            related_report_id=similar_report_id,
            similarity_score=duplicates[0]['similarity_score'],
            relationship_type="duplicate"
        )
        related_id = crud.create_related_report(related)
        print(f"   ✅ Created related report link: {related_id}")
        
        related_reports = crud.get_related_reports(report_id)
        print(f"   ✅ Retrieved {len(related_reports)} related reports")
    
    # Test 7: Query by Status/Category
    print("\n7️⃣  Testing Queries...")
    routed_reports = crud.get_reports_by_status("routed")
    print(f"   ✅ Found {len(routed_reports)} routed reports")
    
    infra_reports = crud.get_reports_by_category("infrastructure")
    print(f"   ✅ Found {len(infra_reports)} infrastructure reports")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    crud.delete_report(report_id)
    crud.delete_report(similar_report_id)
    crud.delete_organisation(org_id)
    print("   ✅ Test data cleaned up")
    
    print("\n🎉 All CRUD tests passed!")

if __name__ == "__main__":
    try:
        test_crud_operations()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
