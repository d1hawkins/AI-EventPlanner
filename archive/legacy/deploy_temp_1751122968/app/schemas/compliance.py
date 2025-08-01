from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ComplianceRequirement(BaseModel):
    """Model for legal and regulatory requirements."""
    
    name: str = Field(..., description="Name of the requirement")
    description: str = Field(..., description="Detailed description of the requirement")
    category: str = Field(..., description="Category of the requirement (e.g., data_protection, accessibility, health_safety)")
    jurisdiction: str = Field(..., description="Jurisdiction where the requirement applies (e.g., EU, US, global)")
    applicable_event_types: List[str] = Field(..., description="Types of events to which this requirement applies")
    documentation_needed: List[str] = Field(..., description="Documentation needed to demonstrate compliance")
    verification_steps: List[str] = Field(..., description="Steps to verify compliance with this requirement")
    status: str = Field("not_started", description="Current status of compliance with this requirement")


class SecurityProtocol(BaseModel):
    """Model for security protocols."""
    
    name: str = Field(..., description="Name of the security protocol")
    description: str = Field(..., description="Detailed description of the protocol")
    category: str = Field(..., description="Category of the protocol (e.g., physical, data, access_control)")
    risk_level: str = Field(..., description="Risk level addressed by this protocol (low, medium, high, critical)")
    implementation_steps: List[str] = Field(..., description="Steps to implement this protocol")
    verification_method: str = Field(..., description="Method to verify implementation of this protocol")
    status: str = Field("not_implemented", description="Current status of implementation")


class DataProtectionMeasure(BaseModel):
    """Model for data protection measures."""
    
    name: str = Field(..., description="Name of the data protection measure")
    description: str = Field(..., description="Detailed description of the measure")
    data_types_covered: List[str] = Field(..., description="Types of data covered by this measure")
    applicable_regulations: List[str] = Field(..., description="Regulations to which this measure applies")
    implementation_steps: List[str] = Field(..., description="Steps to implement this measure")
    status: str = Field("not_implemented", description="Current status of implementation")


class ComplianceAudit(BaseModel):
    """Model for compliance audits."""
    
    name: str = Field(..., description="Name of the audit")
    description: str = Field(..., description="Description of the audit scope and purpose")
    requirements_checked: List[str] = Field(..., description="Requirements checked in this audit")
    findings: List[Dict[str, Any]] = Field(..., description="Findings from the audit")
    recommendations: List[str] = Field(..., description="Recommendations based on audit findings")
    completion_date: datetime = Field(..., description="Date when the audit was completed")
    status: str = Field("scheduled", description="Current status of the audit")


class SecurityIncident(BaseModel):
    """Model for security incidents."""
    
    incident_type: str = Field(..., description="Type of security incident")
    description: str = Field(..., description="Detailed description of the incident")
    severity: str = Field(..., description="Severity of the incident (low, medium, high, critical)")
    date_reported: datetime = Field(..., description="Date when the incident was reported")
    affected_areas: List[str] = Field(..., description="Areas affected by the incident")
    response_steps: List[str] = Field(..., description="Steps taken in response to the incident")
    resolution_status: str = Field(..., description="Current status of incident resolution")
    lessons_learned: Optional[List[str]] = Field(None, description="Lessons learned from the incident")


class IncidentResponsePlan(BaseModel):
    """Model for incident response plans."""
    
    name: str = Field(..., description="Name of the incident response plan")
    description: str = Field(..., description="Description of the plan's scope and purpose")
    incident_types_covered: List[str] = Field(..., description="Types of incidents covered by this plan")
    response_team: List[Dict[str, str]] = Field(..., description="Members of the response team and their roles")
    response_procedures: List[Dict[str, Any]] = Field(..., description="Procedures to follow in response to incidents")
    communication_protocol: Dict[str, Any] = Field(..., description="Protocol for communicating during incidents")
    status: str = Field("draft", description="Current status of the plan")


class ComplianceReport(BaseModel):
    """Model for compliance reports."""
    
    title: str = Field(..., description="Title of the report")
    description: str = Field(..., description="Description of the report's scope and purpose")
    event_details: Dict[str, Any] = Field(..., description="Details of the event covered by this report")
    requirements_summary: Dict[str, int] = Field(..., description="Summary of requirement compliance status")
    security_summary: Dict[str, int] = Field(..., description="Summary of security protocol implementation status")
    data_protection_summary: Dict[str, int] = Field(..., description="Summary of data protection measure implementation status")
    findings: List[Dict[str, Any]] = Field(..., description="Key findings from compliance and security assessment")
    recommendations: List[str] = Field(..., description="Recommendations for improving compliance and security")
    risk_assessment: Dict[str, Any] = Field(..., description="Assessment of remaining risks")
    generated_at: datetime = Field(..., description="Date when the report was generated")


class RegulatoryUpdate(BaseModel):
    """Model for regulatory updates."""
    
    regulation_name: str = Field(..., description="Name of the regulation")
    update_description: str = Field(..., description="Description of the update")
    effective_date: datetime = Field(..., description="Date when the update becomes effective")
    jurisdiction: str = Field(..., description="Jurisdiction where the update applies")
    impact_assessment: Dict[str, Any] = Field(..., description="Assessment of the impact of this update")
    required_actions: List[str] = Field(..., description="Actions required to comply with the update")
    status: str = Field("identified", description="Current status of addressing this update")
