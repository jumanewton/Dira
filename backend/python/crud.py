"""
CRUD operations for Dira database
Provides create, read, update, delete functions for all models
"""

from typing import List, Optional, Dict, Any, Tuple
from psycopg2.extras import execute_values
import json

from db import get_db_cursor
from models import Organisation, Report, Reporter, Facility, ReportRoute, RelatedReport

# ============ Organisation CRUD ============

def create_organisation(org: Organisation) -> str:
    """Create a new organisation and return its ID"""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO organisations (name, type, contact_email, contact_api, facilities)
            VALUES (%(name)s, %(type)s, %(contact_email)s, %(contact_api)s, %(facilities)s::jsonb)
            RETURNING id
        """, {
            'name': org.name,
            'type': org.type,
            'contact_email': org.contact_email,
            'contact_api': org.contact_api,
            'facilities': json.dumps(org.facilities) if org.facilities else '[]'
        })
        return str(cur.fetchone()['id'])

def get_organisation(org_id: str) -> Optional[Organisation]:
    """Get organisation by ID"""
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM organisations WHERE id = %s", (org_id,))
        row = cur.fetchone()
        return Organisation.from_dict(dict(row)) if row else None

def get_all_organisations() -> List[Organisation]:
    """Get all organisations"""
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM organisations ORDER BY name")
        return [Organisation.from_dict(dict(row)) for row in cur.fetchall()]

def get_organisations_by_type(org_type: str) -> List[Organisation]:
    """Get organisations by type (government, utility, etc.)"""
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM organisations WHERE type = %s ORDER BY name", (org_type,))
        return [Organisation.from_dict(dict(row)) for row in cur.fetchall()]

def update_organisation(org_id: str, **kwargs) -> bool:
    """Update organisation fields"""
    if not kwargs:
        return False
    
    # Handle facilities JSON conversion
    if 'facilities' in kwargs and isinstance(kwargs['facilities'], list):
        kwargs['facilities'] = json.dumps(kwargs['facilities'])
    
    set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
    values = list(kwargs.values()) + [org_id]
    
    with get_db_cursor() as cur:
        cur.execute(f"UPDATE organisations SET {set_clause} WHERE id = %s", values)
        return cur.rowcount > 0

def delete_organisation(org_id: str) -> bool:
    """Delete organisation"""
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM organisations WHERE id = %s", (org_id,))
        return cur.rowcount > 0

# ============ Reporter CRUD ============

def create_reporter(reporter: Reporter) -> str:
    """Create a new reporter and return its ID"""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO reporters (name, email, is_anonymous)
            VALUES (%(name)s, %(email)s, %(is_anonymous)s)
            RETURNING id
        """, {
            'name': reporter.name,
            'email': reporter.email,
            'is_anonymous': reporter.is_anonymous
        })
        return str(cur.fetchone()['id'])

def get_reporter(reporter_id: str) -> Optional[Reporter]:
    """Get reporter by ID"""
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM reporters WHERE id = %s", (reporter_id,))
        row = cur.fetchone()
        return Reporter.from_dict(dict(row)) if row else None

def get_reporter_by_email(email: str) -> Optional[Reporter]:
    """Get reporter by email"""
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM reporters WHERE email = %s", (email,))
        row = cur.fetchone()
        return Reporter.from_dict(dict(row)) if row else None

# ============ Report CRUD ============

def create_report(report: Report) -> str:
    """Create a new report and return its ID"""
    with get_db_cursor() as cur:
        # Convert entities to JSON if present
        entities_json = json.dumps(report.entities) if report.entities else None
        
        cur.execute("""
            INSERT INTO reports (
                title, description, category, urgency, entities, confidence,
                status, reporter_id, image_data, analysis_result, embedding
            )
            VALUES (
                %(title)s, %(description)s, %(category)s, %(urgency)s, %(entities)s::jsonb,
                %(confidence)s, %(status)s, %(reporter_id)s, %(image_data)s,
                %(analysis_result)s, %(embedding)s::vector
            )
            RETURNING id
        """, {
            'title': report.title,
            'description': report.description,
            'category': report.category,
            'urgency': report.urgency,
            'entities': entities_json,
            'confidence': report.confidence,
            'status': report.status,
            'reporter_id': report.reporter_id,
            'image_data': report.image_data,
            'analysis_result': report.analysis_result,
            'embedding': report.embedding
        })
        return str(cur.fetchone()['id'])

def get_report(report_id: str) -> Optional[Report]:
    """Get report by ID"""
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
        row = cur.fetchone()
        return Report.from_dict(dict(row)) if row else None

def get_all_reports(limit: int = 100, offset: int = 0) -> List[Report]:
    """Get all reports with pagination"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM reports 
            ORDER BY submitted_at DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        return [Report.from_dict(dict(row)) for row in cur.fetchall()]

def get_reports_by_status(status: str) -> List[Report]:
    """Get reports by status"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM reports 
            WHERE status = %s 
            ORDER BY submitted_at DESC
        """, (status,))
        return [Report.from_dict(dict(row)) for row in cur.fetchall()]

def get_reports_by_category(category: str) -> List[Report]:
    """Get reports by category"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM reports 
            WHERE category = %s 
            ORDER BY submitted_at DESC
        """, (category,))
        return [Report.from_dict(dict(row)) for row in cur.fetchall()]

def update_report(report_id: str, **kwargs) -> bool:
    """Update report fields"""
    if not kwargs:
        return False
    
    # Handle JSON fields
    if 'entities' in kwargs and isinstance(kwargs['entities'], dict):
        kwargs['entities'] = json.dumps(kwargs['entities'])
    
    set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
    values = list(kwargs.values()) + [report_id]
    
    with get_db_cursor() as cur:
        cur.execute(f"UPDATE reports SET {set_clause} WHERE id = %s", values)
        return cur.rowcount > 0

def delete_report(report_id: str) -> bool:
    """Delete report"""
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM reports WHERE id = %s", (report_id,))
        return cur.rowcount > 0

# ============ Vector Search Operations ============

def store_report_embedding(report_id: str, embedding: List[float]) -> bool:
    """Store or update embedding for a report"""
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE reports 
            SET embedding = %s::vector 
            WHERE id = %s
        """, (embedding, report_id))
        return cur.rowcount > 0

def find_duplicate_reports(
    title: str,
    description: str,
    embedding: List[float],
    threshold: float = 0.8,
    limit: int = 10,
    exclude_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Find duplicate/similar reports using vector similarity
    
    Args:
        title: Report title
        description: Report description
        embedding: Vector embedding of the report
        threshold: Similarity threshold (0-1, higher = more similar)
        limit: Maximum number of results
        exclude_id: Exclude this report ID from results
    
    Returns:
        List of similar reports with similarity scores
    """
    with get_db_cursor() as cur:
        # Calculate cosine similarity (1 - distance)
        # The <=> operator calculates cosine distance
        query = """
            SELECT 
                id,
                title,
                description,
                category,
                status,
                submitted_at,
                1 - (embedding <=> %s::vector) as similarity_score
            FROM reports
            WHERE embedding IS NOT NULL
        """
        
        params = [embedding]
        
        if exclude_id:
            query += " AND id != %s"
            params.append(exclude_id)
        
        # Filter by threshold
        query += " AND (1 - (embedding <=> %s::vector)) >= %s"
        params.extend([embedding, threshold])
        
        query += " ORDER BY embedding <=> %s::vector LIMIT %s"
        params.extend([embedding, limit])
        
        cur.execute(query, params)
        
        results = []
        for row in cur.fetchall():
            result = dict(row)
            # Convert UUID to string
            result['id'] = str(result['id'])
            results.append(result)
        
        return results

def search_reports_by_similarity(
    embedding: List[float],
    limit: int = 10,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search for similar reports by embedding"""
    with get_db_cursor() as cur:
        query = """
            SELECT 
                id, title, description, category, status, submitted_at,
                1 - (embedding <=> %s::vector) as similarity_score
            FROM reports
            WHERE embedding IS NOT NULL
        """
        
        params = [embedding]
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY embedding <=> %s::vector LIMIT %s"
        params.extend([embedding, limit])
        
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

# ============ Report Route CRUD ============

def create_report_route(route: ReportRoute) -> str:
    """Create a report route (record of report sent to organisation)"""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO report_routes (report_id, organisation_id, message, status)
            VALUES (%(report_id)s, %(organisation_id)s, %(message)s, %(status)s)
            RETURNING id
        """, {
            'report_id': route.report_id,
            'organisation_id': route.organisation_id,
            'message': route.message,
            'status': route.status
        })
        return str(cur.fetchone()['id'])

def get_routes_for_report(report_id: str) -> List[ReportRoute]:
    """Get all routes for a report"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM report_routes 
            WHERE report_id = %s 
            ORDER BY sent_at DESC
        """, (report_id,))
        return [ReportRoute.from_dict(dict(row)) for row in cur.fetchall()]

def get_routes_for_organisation(org_id: str) -> List[ReportRoute]:
    """Get all routes for an organisation"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM report_routes 
            WHERE organisation_id = %s 
            ORDER BY sent_at DESC
        """, (org_id,))
        return [ReportRoute.from_dict(dict(row)) for row in cur.fetchall()]

# ============ Related Reports CRUD ============

def create_related_report(related: RelatedReport) -> str:
    """Link two reports as related/duplicates"""
    with get_db_cursor() as cur:
        cur.execute("""
            INSERT INTO related_reports (
                report_id, related_report_id, similarity_score, relationship_type
            )
            VALUES (%(report_id)s, %(related_report_id)s, %(similarity_score)s, %(relationship_type)s)
            ON CONFLICT (report_id, related_report_id) DO UPDATE
            SET similarity_score = EXCLUDED.similarity_score,
                relationship_type = EXCLUDED.relationship_type
            RETURNING id
        """, {
            'report_id': related.report_id,
            'related_report_id': related.related_report_id,
            'similarity_score': related.similarity_score,
            'relationship_type': related.relationship_type
        })
        return str(cur.fetchone()['id'])

def get_related_reports(report_id: str) -> List[RelatedReport]:
    """Get all related reports for a given report"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM related_reports 
            WHERE report_id = %s 
            ORDER BY similarity_score DESC
        """, (report_id,))
        return [RelatedReport.from_dict(dict(row)) for row in cur.fetchall()]

def get_duplicate_reports(report_id: str, threshold: float = 0.9) -> List[RelatedReport]:
    """Get duplicate reports (high similarity)"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT * FROM related_reports 
            WHERE report_id = %s 
            AND similarity_score >= %s
            AND relationship_type = 'duplicate'
            ORDER BY similarity_score DESC
        """, (report_id, threshold))
        return [RelatedReport.from_dict(dict(row)) for row in cur.fetchall()]
