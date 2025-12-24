"""
Data models for Dira
Corresponds to database tables with type hints
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid

@dataclass
class Organisation:
    """Organisation/Agency model"""
    name: str
    type: str  # government, utility, etc.
    contact_email: str
    id: Optional[str] = None
    contact_api: Optional[str] = None
    facilities: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insert"""
        data = asdict(self)
        # Convert facilities list to JSON string
        if isinstance(data['facilities'], list):
            data['facilities'] = json.dumps(data['facilities'])
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Organisation':
        """Create from database row"""
        if isinstance(data.get('facilities'), str):
            data['facilities'] = json.loads(data['facilities'])
        if isinstance(data.get('id'), uuid.UUID):
            data['id'] = str(data['id'])
        return cls(**data)

@dataclass
class Facility:
    """Facility model"""
    name: str
    location: str
    organisation_id: str
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Facility':
        """Create from database row"""
        if isinstance(data.get('id'), uuid.UUID):
            data['id'] = str(data['id'])
        if isinstance(data.get('organisation_id'), uuid.UUID):
            data['organisation_id'] = str(data['organisation_id'])
        return cls(**data)

@dataclass
class Reporter:
    """Reporter/User model"""
    email: str
    is_anonymous: bool = False
    id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reporter':
        """Create from database row"""
        if isinstance(data.get('id'), uuid.UUID):
            data['id'] = str(data['id'])
        return cls(**data)

@dataclass
class Report:
    """Report model"""
    title: str
    description: str
    id: Optional[str] = None
    category: Optional[str] = None  # infrastructure, safety, utility
    urgency: Optional[str] = None  # low, medium, high
    entities: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    status: str = "submitted"  # submitted, routed, resolved, duplicate
    submitted_at: Optional[datetime] = None
    reporter_id: Optional[str] = None
    image_data: Optional[str] = None
    analysis_result: Optional[str] = None
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insert"""
        data = asdict(self)
        # Convert entities dict to JSON string if present
        if data.get('entities') and isinstance(data['entities'], dict):
            data['entities'] = json.dumps(data['entities'])
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        """Create from database row"""
        # Convert UUIDs to strings
        if isinstance(data.get('id'), uuid.UUID):
            data['id'] = str(data['id'])
        if isinstance(data.get('reporter_id'), uuid.UUID):
            data['reporter_id'] = str(data['reporter_id'])
        
        # Parse JSON fields
        if isinstance(data.get('entities'), str):
            data['entities'] = json.loads(data['entities'])
        
        # Handle embedding conversion from string if needed
        if isinstance(data.get('embedding'), str):
            data['embedding'] = json.loads(data['embedding'])
        
        return cls(**data)

@dataclass
class ReportRoute:
    """Report routing record (which org received which report)"""
    report_id: str
    organisation_id: str
    id: Optional[str] = None
    message: Optional[str] = None
    sent_at: Optional[datetime] = None
    status: str = "sent"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReportRoute':
        """Create from database row"""
        if isinstance(data.get('id'), uuid.UUID):
            data['id'] = str(data['id'])
        if isinstance(data.get('report_id'), uuid.UUID):
            data['report_id'] = str(data['report_id'])
        if isinstance(data.get('organisation_id'), uuid.UUID):
            data['organisation_id'] = str(data['organisation_id'])
        return cls(**data)

@dataclass
class RelatedReport:
    """Related reports (duplicates/similar)"""
    report_id: str
    related_report_id: str
    similarity_score: float
    id: Optional[str] = None
    relationship_type: str = "duplicate"  # duplicate, similar
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelatedReport':
        """Create from database row"""
        if isinstance(data.get('id'), uuid.UUID):
            data['id'] = str(data['id'])
        if isinstance(data.get('report_id'), uuid.UUID):
            data['report_id'] = str(data['report_id'])
        if isinstance(data.get('related_report_id'), uuid.UUID):
            data['related_report_id'] = str(data['related_report_id'])
        return cls(**data)
