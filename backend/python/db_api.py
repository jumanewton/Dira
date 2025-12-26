"""
Database API Service for JAC Backend
Provides HTTP endpoints for database operations that JAC can call
Runs on port 8004
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
import sys
import os

# Add python directory to path
sys.path.append(os.path.dirname(__file__))

from models import Organisation, Reporter, Report, ReportRoute, RelatedReport
import crud

app = FastAPI(title="Dira Database API", version="1.0.0")

# ============ Request/Response Models ============

class CreateReporterRequest(BaseModel):
    name: Optional[str] = None
    email: str
    is_anonymous: bool = False

class CreateReportRequest(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    urgency: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    status: str = "submitted"
    reporter_id: Optional[str] = None
    image_data: Optional[str] = None
    analysis_result: Optional[str] = None
    embedding: Optional[List[float]] = None

class UpdateReportRequest(BaseModel):
    category: Optional[str] = None
    urgency: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    status: Optional[str] = None
    embedding: Optional[List[float]] = None

class CreateRouteRequest(BaseModel):
    report_id: str
    organisation_id: str
    message: Optional[str] = None
    status: str = "sent"

class LinkRelatedReportsRequest(BaseModel):
    report_id: str
    related_report_id: str
    similarity_score: float
    relationship_type: str = "duplicate"

# ============ Reporter Endpoints ============

@app.post("/reporters", response_model=Dict[str, str])
def create_reporter_endpoint(request: CreateReporterRequest):
    """Create a new reporter"""
    try:
        reporter = Reporter(
            name=request.name,
            email=request.email,
            is_anonymous=request.is_anonymous
        )
        reporter_id = crud.create_reporter(reporter)
        return {"reporter_id": reporter_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reporters/{reporter_id}")
def get_reporter_endpoint(reporter_id: UUID):
    """Get reporter by ID"""
    reporter = crud.get_reporter(str(reporter_id))
    if not reporter:
        raise HTTPException(status_code=404, detail="Reporter not found")
    return reporter.__dict__

@app.get("/reporters/email/{email}")
def get_reporter_by_email_endpoint(email: str):
    """Get or create reporter by email"""
    reporter = crud.get_reporter_by_email(email)
    if reporter:
        return {"reporter_id": reporter.id, "exists": True}
    return {"reporter_id": None, "exists": False}

# ============ Report Endpoints ============

@app.post("/reports", response_model=Dict[str, str])
def create_report_endpoint(request: CreateReportRequest):
    """Create a new report"""
    try:
        report = Report(
            title=request.title,
            description=request.description,
            category=request.category,
            urgency=request.urgency,
            entities=request.entities,
            confidence=request.confidence,
            status=request.status,
            reporter_id=request.reporter_id,
            image_data=request.image_data,
            analysis_result=request.analysis_result,
            embedding=request.embedding
        )
        report_id = crud.create_report(report)
        return {"report_id": report_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/{report_id}")
def get_report_endpoint(report_id: UUID):
    """Get report by ID"""
    report = crud.get_report(str(report_id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.__dict__

@app.get("/reports")
def get_all_reports_endpoint(limit: int = 100, offset: int = 0):
    """Get all reports with pagination"""
    reports = crud.get_all_reports(limit, offset)
    return [r.__dict__ for r in reports]

@app.get("/reports/status/{status}")
def get_reports_by_status_endpoint(status: str):
    """Get reports by status"""
    reports = crud.get_reports_by_status(status)
    return [r.__dict__ for r in reports]

@app.get("/reports/category/{category}")
def get_reports_by_category_endpoint(category: str):
    """Get reports by category"""
    reports = crud.get_reports_by_category(category)
    return [r.__dict__ for r in reports]

@app.patch("/reports/{report_id}")
def update_report_endpoint(report_id: str, request: UpdateReportRequest):
    """Update report fields"""
    try:
        updates = {k: v for k, v in request.dict().items() if v is not None}
        if not updates:
            return {"status": "no_changes"}
        
        success = crud.update_report(report_id, **updates)
        if success:
            return {"status": "updated", "report_id": report_id}
        else:
            raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reports/{report_id}")
def delete_report_endpoint(report_id: str):
    """Delete a report"""
    success = crud.delete_report(report_id)
    if success:
        return {"status": "deleted", "report_id": report_id}
    else:
        raise HTTPException(status_code=404, detail="Report not found")

# ============ Organisation Endpoints ============

@app.get("/organisations")
def get_all_organisations_endpoint():
    """Get all organisations"""
    orgs = crud.get_all_organisations()
    return [o.__dict__ for o in orgs]

@app.get("/organisations/type/{org_type}")
def get_organisations_by_type_endpoint(org_type: str):
    """Get organisations by type (government, utility, etc.)"""
    orgs = crud.get_organisations_by_type(org_type)
    return [o.__dict__ for o in orgs]

@app.get("/organisations/{org_id}")
def get_organisation_endpoint(org_id: str):
    """Get organisation by ID"""
    org = crud.get_organisation(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return org.__dict__

# ============ Report Route Endpoints ============

@app.post("/report_routes")
def create_route_endpoint(request: CreateRouteRequest):
    """Create a report route (record of report sent to organisation)"""
    try:
        route = ReportRoute(
            report_id=request.report_id,
            organisation_id=request.organisation_id,
            message=request.message,
            status=request.status
        )
        route_id = crud.create_report_route(route)
        return {"route_id": route_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report_routes/report/{report_id}")
def get_routes_for_report_endpoint(report_id: str):
    """Get all routes for a report"""
    routes = crud.get_routes_for_report(report_id)
    return [r.__dict__ for r in routes]

@app.get("/report_routes/organisation/{org_id}")
def get_routes_for_organisation_endpoint(org_id: str):
    """Get all routes for an organisation"""
    routes = crud.get_routes_for_organisation(org_id)
    return [r.__dict__ for r in routes]

# ============ Related Reports Endpoints ============

@app.post("/related_reports")
def link_related_reports_endpoint(request: LinkRelatedReportsRequest):
    """Link two reports as related/duplicates"""
    try:
        related = RelatedReport(
            report_id=request.report_id,
            related_report_id=request.related_report_id,
            similarity_score=request.similarity_score,
            relationship_type=request.relationship_type
        )
        related_id = crud.create_related_report(related)
        return {"related_id": related_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/related_reports/{report_id}")
def get_related_reports_endpoint(report_id: str):
    """Get all related reports for a given report"""
    related = crud.get_related_reports(report_id)
    return [r.__dict__ for r in related]

@app.get("/related_reports/{report_id}/duplicates")
def get_duplicate_reports_endpoint(report_id: str, threshold: float = 0.9):
    """Get duplicate reports (high similarity)"""
    duplicates = crud.get_duplicate_reports(report_id, threshold)
    return [d.__dict__ for d in duplicates]

# ============ Delete Endpoints (for testing) ============

@app.delete("/reports/{report_id}")
def delete_report_endpoint(report_id: str):
    """Delete a report and its related data"""
    try:
        crud.delete_report(report_id)
        return {"status": "deleted", "report_id": report_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Health Check ============

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "database_api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
