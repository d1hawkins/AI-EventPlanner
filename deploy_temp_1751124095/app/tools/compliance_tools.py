from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import uuid
import json

from pydantic import BaseModel, Field
from pydantic import BaseModel, Field

    ComplianceRequirement,
    SecurityProtocol,
    DataProtectionMeasure,
    ComplianceAudit,
    SecurityIncident,
    IncidentResponsePlan,
    ComplianceReport,
    RegulatoryUpdate
    RegulatoryUpdate
)


class RequirementTrackingInput(BaseModel):
    """Input schema for the requirement tracking tool."""
    
    name: str = Field(..., description="Name of the requirement")
    description: str = Field(..., description="Description of the requirement")
    category: str = Field(..., description="Category of the requirement")
    jurisdiction: str = Field(..., description="Jurisdiction where the requirement applies")
    applicable_event_types: List[str] = Field(..., description="Types of events to which this requirement applies")
    documentation_needed: Optional[List[str]] = Field(None, description="Documentation needed to demonstrate compliance")
    verification_steps: Optional[List[str]] = Field(None, description="Steps to verify compliance with this requirement")


class RequirementTrackingTool(BaseTool):
    """Tool for tracking legal and regulatory requirements."""
    
    name: str = "requirement_tracking_tool"
    description: str = "Track legal and regulatory requirements for an event"
    args_schema: Type[RequirementTrackingInput] = RequirementTrackingInput
    
    def _run(self, name: str, description: str, category: str, jurisdiction: str,
             applicable_event_types: List[str], documentation_needed: Optional[List[str]] = None,
             verification_steps: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the requirement tracking tool.
        
        Args:
            name: Name of the requirement
            description: Description of the requirement
            category: Category of the requirement
            jurisdiction: Jurisdiction where the requirement applies
            applicable_event_types: Types of events to which this requirement applies
            documentation_needed: Documentation needed to demonstrate compliance
            verification_steps: Steps to verify compliance with this requirement
            
        Returns:
            Dictionary with requirement details
        """
        # In a real implementation, this would store the requirement in a database
        # For now, we'll return a mock requirement
        
        # Set default values if not provided
        if documentation_needed is None:
            documentation_needed = [
                "Compliance policy document",
                "Signed acknowledgment forms",
                "Verification checklist"
            ]
        
        if verification_steps is None:
            verification_steps = [
                "Review documentation",
                "Conduct compliance check",
                "Obtain necessary approvals"
            ]
        
        # Create a ComplianceRequirement object
        requirement = ComplianceRequirement(
            name=name,
            description=description,
            category=category,
            jurisdiction=jurisdiction,
            applicable_event_types=applicable_event_types,
            documentation_needed=documentation_needed,
            verification_steps=verification_steps,
            status="not_started"
        )
        
        # Generate a requirement ID
        requirement_id = f"req-{uuid.uuid4().hex[:8]}"
        
        return {
            "requirement_id": requirement_id,
            "requirement": requirement.dict(),
            "tracking_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class DocumentationReviewInput(BaseModel):
    """Input schema for the documentation review tool."""
    
    document_type: str = Field(..., description="Type of document to review")
    document_content: str = Field(..., description="Content of the document to review")
    requirements: List[str] = Field(..., description="Requirements to check against")
    event_type: str = Field(..., description="Type of event for which the document is being reviewed")


class DocumentationReviewTool(BaseTool):
    """Tool for reviewing compliance documentation."""
    
    name: str = "documentation_review_tool"
    description: str = "Review documentation for compliance with requirements"
    args_schema: Type[DocumentationReviewInput] = DocumentationReviewInput
    
    def _run(self, document_type: str, document_content: str, requirements: List[str],
             event_type: str) -> Dict[str, Any]:
        """
        Run the documentation review tool.
        
        Args:
            document_type: Type of document to review
            document_content: Content of the document to review
            requirements: Requirements to check against
            event_type: Type of event for which the document is being reviewed
            
        Returns:
            Dictionary with review results
        """
        # In a real implementation, this would analyze the document against requirements
        # For now, we'll return mock review results
        
        # Generate mock findings
        findings = []
        
        # For demonstration purposes, we'll create some mock findings
        if "privacy" in document_type.lower() or "data" in document_type.lower():
            findings.append({
                "requirement": "Data Protection",
                "status": "compliant",
                "details": "Document includes appropriate data protection clauses"
            })
            findings.append({
                "requirement": "Consent Mechanisms",
                "status": "non_compliant",
                "details": "Document lacks clear consent mechanisms for data collection"
            })
        elif "security" in document_type.lower():
            findings.append({
                "requirement": "Access Controls",
                "status": "compliant",
                "details": "Document specifies appropriate access control measures"
            })
            findings.append({
                "requirement": "Incident Response",
                "status": "partially_compliant",
                "details": "Document includes incident response procedures but lacks specific timelines"
            })
        elif "contract" in document_type.lower() or "agreement" in document_type.lower():
            findings.append({
                "requirement": "Liability Clauses",
                "status": "compliant",
                "details": "Document includes appropriate liability clauses"
            })
            findings.append({
                "requirement": "Termination Provisions",
                "status": "compliant",
                "details": "Document includes clear termination provisions"
            })
        else:
            findings.append({
                "requirement": "General Compliance",
                "status": "needs_review",
                "details": "Document requires further review by compliance specialist"
            })
        
        # Generate recommendations based on findings
        recommendations = []
        for finding in findings:
            if finding["status"] == "non_compliant":
                recommendations.append(f"Address {finding['requirement']} issues: {finding['details']}")
            elif finding["status"] == "partially_compliant":
                recommendations.append(f"Improve {finding['requirement']}: {finding['details']}")
            elif finding["status"] == "needs_review":
                recommendations.append(f"Seek specialist review for {finding['requirement']}")
        
        # Calculate compliance score
        compliant_count = sum(1 for finding in findings if finding["status"] == "compliant")
        total_count = len(findings)
        compliance_score = (compliant_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "document_type": document_type,
            "event_type": event_type,
            "findings": findings,
            "recommendations": recommendations,
            "compliance_score": compliance_score,
            "review_details": {
                "reviewed_at": datetime.now().isoformat(),
                "reviewed_by": "Compliance & Security Agent",
                "requirements_checked": requirements
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class AuditSupportInput(BaseModel):
    """Input schema for the audit support tool."""
    
    audit_name: str = Field(..., description="Name of the audit")
    audit_description: str = Field(..., description="Description of the audit scope and purpose")
    requirements_to_check: List[str] = Field(..., description="Requirements to check in this audit")
    event_details: Dict[str, Any] = Field(..., description="Details of the event being audited")


class AuditSupportTool(BaseTool):
    """Tool for supporting compliance audits."""
    
    name: str = "audit_support_tool"
    description: str = "Support compliance audits for events"
    args_schema: Type[AuditSupportInput] = AuditSupportInput
    
    def _run(self, audit_name: str, audit_description: str, requirements_to_check: List[str],
             event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the audit support tool.
        
        Args:
            audit_name: Name of the audit
            audit_description: Description of the audit scope and purpose
            requirements_to_check: Requirements to check in this audit
            event_details: Details of the event being audited
            
        Returns:
            Dictionary with audit results
        """
        # In a real implementation, this would conduct an actual audit
        # For now, we'll return mock audit results
        
        # Generate mock findings
        findings = []
        
        # For demonstration purposes, we'll create some mock findings
        for i, requirement in enumerate(requirements_to_check):
            # Alternate between different statuses for demonstration
            if i % 3 == 0:
                status = "compliant"
                details = f"Requirement '{requirement}' is fully implemented and documented"
            elif i % 3 == 1:
                status = "partially_compliant"
                details = f"Requirement '{requirement}' is partially implemented but lacks complete documentation"
            else:
                status = "non_compliant"
                details = f"Requirement '{requirement}' is not implemented or documented"
            
            findings.append({
                "requirement": requirement,
                "status": status,
                "details": details,
                "evidence": f"Evidence for {requirement} compliance check"
            })
        
        # Generate recommendations based on findings
        recommendations = []
        for finding in findings:
            if finding["status"] == "non_compliant":
                recommendations.append(f"Implement and document {finding['requirement']}")
            elif finding["status"] == "partially_compliant":
                recommendations.append(f"Complete documentation for {finding['requirement']}")
        
        # Create a ComplianceAudit object
        audit = ComplianceAudit(
            name=audit_name,
            description=audit_description,
            requirements_checked=requirements_to_check,
            findings=findings,
            recommendations=recommendations,
            completion_date=datetime.now(),
            status="completed"
        )
        
        # Generate an audit ID
        audit_id = f"audit-{uuid.uuid4().hex[:8]}"
        
        return {
            "audit_id": audit_id,
            "audit": audit.dict(),
            "summary": {
                "total_requirements": len(requirements_to_check),
                "compliant": sum(1 for finding in findings if finding["status"] == "compliant"),
                "partially_compliant": sum(1 for finding in findings if finding["status"] == "partially_compliant"),
                "non_compliant": sum(1 for finding in findings if finding["status"] == "non_compliant"),
                "recommendations_count": len(recommendations)
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class RegulatoryUpdateInput(BaseModel):
    """Input schema for the regulatory update tool."""
    
    regulation_name: str = Field(..., description="Name of the regulation")
    update_description: str = Field(..., description="Description of the update")
    effective_date: str = Field(..., description="Date when the update becomes effective (YYYY-MM-DD)")
    jurisdiction: str = Field(..., description="Jurisdiction where the update applies")
    event_types_affected: List[str] = Field(..., description="Types of events affected by this update")


class RegulatoryUpdateTool(BaseTool):
    """Tool for monitoring regulatory updates."""
    
    name: str = "regulatory_update_tool"
    description: str = "Monitor and track regulatory updates relevant to events"
    args_schema: Type[RegulatoryUpdateInput] = RegulatoryUpdateInput
    
    def _run(self, regulation_name: str, update_description: str, effective_date: str,
             jurisdiction: str, event_types_affected: List[str]) -> Dict[str, Any]:
        """
        Run the regulatory update tool.
        
        Args:
            regulation_name: Name of the regulation
            update_description: Description of the update
            effective_date: Date when the update becomes effective
            jurisdiction: Jurisdiction where the update applies
            event_types_affected: Types of events affected by this update
            
        Returns:
            Dictionary with regulatory update details
        """
        # In a real implementation, this would store the update in a database
        # For now, we'll return a mock update
        
        # Parse the effective date
        effective_date_obj = datetime.strptime(effective_date, "%Y-%m-%d")
        
        # Generate impact assessment based on the update description
        impact_assessment = {
            "severity": "medium",
            "areas_affected": ["data_collection", "consent_management", "documentation"],
            "implementation_complexity": "moderate",
            "estimated_effort": "2-3 weeks",
            "cost_implications": "moderate"
        }
        
        # Generate required actions based on the update description
        required_actions = [
            f"Update privacy policies to comply with {regulation_name}",
            f"Revise consent forms to include new requirements",
            f"Train staff on {regulation_name} compliance",
            f"Update documentation to reflect new requirements",
            f"Conduct compliance audit after implementation"
        ]
        
        # Create a RegulatoryUpdate object
        regulatory_update = RegulatoryUpdate(
            regulation_name=regulation_name,
            update_description=update_description,
            effective_date=effective_date_obj,
            jurisdiction=jurisdiction,
            impact_assessment=impact_assessment,
            required_actions=required_actions,
            status="identified"
        )
        
        # Generate an update ID
        update_id = f"update-{uuid.uuid4().hex[:8]}"
        
        return {
            "update_id": update_id,
            "regulatory_update": regulatory_update.dict(),
            "time_to_compliance": (effective_date_obj - datetime.now()).days,
            "affected_event_types": event_types_affected,
            "tracking_details": {
                "identified_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "identified_by": "Compliance & Security Agent"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class AccessControlInput(BaseModel):
    """Input schema for the access control tool."""
    
    event_type: str = Field(..., description="Type of event")
    venue_type: str = Field(..., description="Type of venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    security_level: str = Field(..., description="Required security level (low, medium, high, critical)")
    special_requirements: Optional[List[str]] = Field(None, description="Special access control requirements")


class AccessControlTool(BaseTool):
    """Tool for planning and implementing access control."""
    
    name: str = "access_control_tool"
    description: str = "Plan and implement access control for events"
    args_schema: Type[AccessControlInput] = AccessControlInput
    
    def _run(self, event_type: str, venue_type: str, attendee_count: int,
             security_level: str, special_requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the access control tool.
        
        Args:
            event_type: Type of event
            venue_type: Type of venue
            attendee_count: Expected number of attendees
            security_level: Required security level
            special_requirements: Special access control requirements
            
        Returns:
            Dictionary with access control plan
        """
        # In a real implementation, this would generate an actual access control plan
        # For now, we'll return a mock plan
        
        # Set default special requirements if not provided
        if special_requirements is None:
            special_requirements = []
        
        # Generate access control protocols based on inputs
        protocols = []
        
        # Basic access control for all events
        protocols.append(
            SecurityProtocol(
                name="Attendee Identification",
                description="System for identifying and verifying attendees",
                category="access_control",
                risk_level="medium",
                implementation_steps=[
                    "Set up registration verification system",
                    "Prepare attendee badges or wristbands",
                    "Train staff on verification procedures"
                ],
                verification_method="Test verification process with sample attendees",
                status="not_implemented"
            ).dict()
        )
        
        # Add protocols based on security level
        if security_level.lower() in ["medium", "high", "critical"]:
            protocols.append(
                SecurityProtocol(
                    name="Perimeter Security",
                    description="Measures to secure the event perimeter",
                    category="physical",
                    risk_level="medium",
                    implementation_steps=[
                        "Define secure perimeter boundaries",
                        "Establish entry and exit points",
                        "Deploy security personnel at key points"
                    ],
                    verification_method="Conduct perimeter security walkthrough",
                    status="not_implemented"
                ).dict()
            )
        
        if security_level.lower() in ["high", "critical"]:
            protocols.append(
                SecurityProtocol(
                    name="Security Screening",
                    description="Screening process for attendees and items",
                    category="physical",
                    risk_level="high",
                    implementation_steps=[
                        "Set up screening equipment",
                        "Establish screening procedures",
                        "Train security personnel on screening protocols"
                    ],
                    verification_method="Test screening process with security team",
                    status="not_implemented"
                ).dict()
            )
        
        if security_level.lower() == "critical":
            protocols.append(
                SecurityProtocol(
                    name="Advanced Security Measures",
                    description="Advanced security measures for high-risk events",
                    category="physical",
                    risk_level="critical",
                    implementation_steps=[
                        "Coordinate with local law enforcement",
                        "Implement multi-layer security checks",
                        "Establish command center for security operations"
                    ],
                    verification_method="Conduct full security drill with all personnel",
                    status="not_implemented"
                ).dict()
            )
        
        # Add protocols for large events
        if attendee_count > 500:
            protocols.append(
                SecurityProtocol(
                    name="Crowd Management",
                    description="Measures for managing large crowds",
                    category="physical",
                    risk_level="medium",
                    implementation_steps=[
                        "Develop crowd flow plan",
                        "Establish capacity limits for different areas",
                        "Train staff on crowd management techniques"
                    ],
                    verification_method="Simulate crowd flow with staff",
                    status="not_implemented"
                ).dict()
            )
        
        # Add protocols for special requirements
        for requirement in special_requirements:
            if "vip" in requirement.lower():
                protocols.append(
                    SecurityProtocol(
                        name="VIP Security",
                        description="Special security measures for VIPs",
                        category="access_control",
                        risk_level="high",
                        implementation_steps=[
                            "Establish VIP-only areas",
                            "Assign dedicated security personnel to VIPs",
                            "Create separate entry and exit routes for VIPs"
                        ],
                        verification_method="Conduct VIP security walkthrough",
                        status="not_implemented"
                    ).dict()
                )
            elif "data" in requirement.lower() or "privacy" in requirement.lower():
                protocols.append(
                    SecurityProtocol(
                        name="Data Security",
                        description="Measures to protect sensitive data",
                        category="data",
                        risk_level="high",
                        implementation_steps=[
                            "Implement data encryption",
                            "Establish data access controls",
                            "Train staff on data handling procedures"
                        ],
                        verification_method="Conduct data security audit",
                        status="not_implemented"
                    ).dict()
                )
        
        # Generate staffing requirements based on attendee count and security level
        security_staff_count = max(2, attendee_count // 100)
        if security_level.lower() == "high":
            security_staff_count = max(4, attendee_count // 75)
        elif security_level.lower() == "critical":
            security_staff_count = max(6, attendee_count // 50)
        
        # Generate equipment requirements
        equipment_requirements = [
            {"name": "Attendee Badges", "quantity": attendee_count},
            {"name": "Badge Scanners", "quantity": max(2, attendee_count // 200)},
            {"name": "Two-way Radios", "quantity": security_staff_count + 2}
        ]
        
        if security_level.lower() in ["medium", "high", "critical"]:
            equipment_requirements.append({"name": "Security Barriers", "quantity": max(10, attendee_count // 100)})
        
        if security_level.lower() in ["high", "critical"]:
            equipment_requirements.append({"name": "Metal Detectors", "quantity": max(2, attendee_count // 300)})
            equipment_requirements.append({"name": "Security Cameras", "quantity": max(4, attendee_count // 200)})
        
        return {
            "access_control_plan": {
                "event_type": event_type,
                "venue_type": venue_type,
                "attendee_count": attendee_count,
                "security_level": security_level,
                "special_requirements": special_requirements,
                "protocols": protocols,
                "staffing_requirements": {
                    "security_staff": security_staff_count,
                    "access_control_staff": max(2, attendee_count // 200),
                    "supervisors": max(1, security_staff_count // 5)
                },
                "equipment_requirements": equipment_requirements
            },
            "plan_id": f"access-{uuid.uuid4().hex[:8]}",
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class DataProtectionInput(BaseModel):
    """Input schema for the data protection tool."""
    
    event_type: str = Field(..., description="Type of event")
    data_types_collected: List[str] = Field(..., description="Types of data collected for the event")
    jurisdictions: List[str] = Field(..., description="Jurisdictions where the event and data collection occur")
    processing_purposes: List[str] = Field(..., description="Purposes for processing the collected data")
    third_party_sharing: bool = Field(..., description="Whether data will be shared with third parties")
    retention_period: Optional[str] = Field(None, description="Period for which data will be retained")


class DataProtectionTool(BaseTool):
    """Tool for implementing data protection measures."""
    
    name: str = "data_protection_tool"
    description: str = "Implement data protection measures for events"
    args_schema: Type[DataProtectionInput] = DataProtectionInput
    
    def _run(self, event_type: str, data_types_collected: List[str], jurisdictions: List[str],
             processing_purposes: List[str], third_party_sharing: bool,
             retention_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the data protection tool.
        
        Args:
            event_type: Type of event
            data_types_collected: Types of data collected for the event
            jurisdictions: Jurisdictions where the event and data collection occur
            processing_purposes: Purposes for processing the collected data
            third_party_sharing: Whether data will be shared with third parties
            retention_period: Period for which data will be retained
            
        Returns:
            Dictionary with data protection plan
        """
        # In a real implementation, this would generate an actual data protection plan
        # For now, we'll return a mock plan
        
        # Set default retention period if not provided
        if retention_period is None:
            retention_period = "1 year after event"
        
        # Determine applicable regulations based on jurisdictions
        applicable_regulations = []
        for jurisdiction in jurisdictions:
            if jurisdiction.lower() in ["eu", "european union", "europe"]:
                applicable_regulations.append("GDPR")
            if jurisdiction.lower() in ["california", "ca", "us-ca"]:
                applicable_regulations.append("CCPA")
            if jurisdiction.lower() in ["us", "united states", "usa"]:
                applicable_regulations.append("US State Privacy Laws")
                if "health" in data_types_collected or "medical" in data_types_collected:
                    applicable_regulations.append("HIPAA")
            if jurisdiction.lower() in ["canada"]:
                applicable_regulations.append("PIPEDA")
            if jurisdiction.lower() in ["australia"]:
                applicable_regulations.append("Privacy Act 1988")
            if jurisdiction.lower() in ["uk", "united kingdom"]:
                applicable_regulations.append("UK GDPR")
                applicable_regulations.append("Data Protection Act 2018")
        
        # Remove duplicates
        applicable_regulations = list(set(applicable_regulations))
        
        # Generate data protection measures based on inputs
        measures = []
        
        # Basic data protection for all events
        measures.append(
            DataProtectionMeasure(
                name="Privacy Notice",
                description="Clear and comprehensive privacy notice for attendees",
                data_types_covered=data_types_collected,
                applicable_regulations=applicable_regulations,
                implementation_steps=[
                    "Draft privacy notice covering all required elements",
                    "Review privacy notice with legal team",
                    "Make privacy notice accessible to all attendees"
                ],
                status="not_implemented"
            ).dict()
        )
        
        measures.append(
            DataProtectionMeasure(
                name="Data Collection Consent",
                description="Mechanism for obtaining consent for data collection",
                data_types_covered=data_types_collected,
                applicable_regulations=applicable_regulations,
                implementation_steps=[
                    "Design consent mechanism",
                    "Ensure consent is freely given, specific, informed, and unambiguous",
                    "Implement consent recording system"
                ],
                status="not_implemented"
            ).dict()
        )
        
        # Add measures for specific data types
        if any(dt for dt in data_types_collected if "personal" in dt.lower()):
            measures.append(
                DataProtectionMeasure(
                    name="Personal Data Security",
                    description="Measures to secure personal data",
                    data_types_covered=[dt for dt in data_types_collected if "personal" in dt.lower()],
                    applicable_regulations=applicable_regulations,
                    implementation_steps=[
                        "Implement data encryption",
                        "Establish access controls",
                        "Set up secure data storage"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        if any(dt for dt in data_types_collected if "financial" in dt.lower() or "payment" in dt.lower()):
            measures.append(
                DataProtectionMeasure(
                    name="Financial Data Protection",
                    description="Measures to protect financial data",
                    data_types_covered=[dt for dt in data_types_collected if "financial" in dt.lower() or "payment" in dt.lower()],
                    applicable_regulations=applicable_regulations + ["PCI DSS"],
                    implementation_steps=[
                        "Implement PCI DSS compliant payment processing",
                        "Minimize storage of financial data",
                        "Secure transmission of financial information"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        if any(dt for dt in data_types_collected if "health" in dt.lower() or "medical" in dt.lower()):
            measures.append(
                DataProtectionMeasure(
                    name="Health Data Protection",
                    description="Measures to protect health-related data",
                    data_types_covered=[dt for dt in data_types_collected if "health" in dt.lower() or "medical" in dt.lower()],
                    applicable_regulations=[reg for reg in applicable_regulations if reg in ["HIPAA", "GDPR"]],
                    implementation_steps=[
                        "Implement enhanced security for health data",
                        "Obtain explicit consent for health data processing",
                        "Limit access to health data to authorized personnel only"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        # Add measures for third-party sharing
        if third_party_sharing:
            measures.append(
                DataProtectionMeasure(
                    name="Third-Party Data Sharing Controls",
                    description="Controls for sharing data with third parties",
                    data_types_covered=data_types_collected,
                    applicable_regulations=applicable_regulations,
                    implementation_steps=[
                        "Identify all third parties receiving data",
                        "Establish data processing agreements with third parties",
                        "Implement data transfer mechanisms for cross-border transfers",
                        "Ensure third parties maintain adequate security measures"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        # Add data retention measure
        measures.append(
            DataProtectionMeasure(
                name="Data Retention Controls",
                description=f"Controls for data retention and deletion after {retention_period}",
                data_types_covered=data_types_collected,
                applicable_regulations=applicable_regulations,
                implementation_steps=[
                    "Implement data retention policy",
                    f"Set up automated deletion after {retention_period}",
                    "Establish process for handling retention exceptions"
                ],
                status="not_implemented"
            ).dict()
        )
        
        # Add data subject rights measure if GDPR or CCPA applies
        if "GDPR" in applicable_regulations or "CCPA" in applicable_regulations:
            measures.append(
                DataProtectionMeasure(
                    name="Data Subject Rights Procedures",
                    description="Procedures for handling data subject rights requests",
                    data_types_covered=data_types_collected,
                    applicable_regulations=[reg for reg in applicable_regulations if reg in ["GDPR", "CCPA", "UK GDPR"]],
                    implementation_steps=[
                        "Establish process for receiving rights requests",
                        "Implement procedures for responding to access, deletion, and other requests",
                        "Train staff on handling rights requests",
                        "Set up record-keeping for rights requests"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        # Generate documentation requirements
        documentation_requirements = [
            "Privacy Notice",
            "Consent Forms",
            "Data Processing Inventory",
            "Data Protection Impact Assessment"
        ]
        
        if third_party_sharing:
            documentation_requirements.append("Third-Party Data Processing Agreements")
        
        if "GDPR" in applicable_regulations:
            documentation_requirements.append("Records of Processing Activities")
            documentation_requirements.append("Data Subject Rights Procedures")
        
        return {
            "data_protection_plan": {
                "event_type": event_type,
                "data_types_collected": data_types_collected,
                "jurisdictions": jurisdictions,
                "processing_purposes": processing_purposes,
                "third_party_sharing": third_party_sharing,
                "retention_period": retention_period,
                "applicable_regulations": applicable_regulations,
                "measures": measures,
                "documentation_requirements": documentation_requirements
            },
            "plan_id": f"dp-{uuid.uuid4().hex[:8]}",
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class ThreatMonitoringInput(BaseModel):
    """Input schema for the threat monitoring tool."""
    
    event_type: str = Field(..., description="Type of event")
    venue_type: str = Field(..., description="Type of venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    event_duration: str = Field(..., description="Duration of the event (e.g., '3 days', '8 hours')")
    high_profile: bool = Field(..., description="Whether the event includes high-profile individuals")
    threat_categories: List[str] = Field(..., description="Categories of threats to monitor")


class ThreatMonitoringTool(BaseTool):
    """Tool for monitoring security threats."""
    
    name: str = "threat_monitoring_tool"
    description: str = "Monitor and assess security threats for events"
    args_schema: Type[ThreatMonitoringInput] = ThreatMonitoringInput
    
    def _run(self, event_type: str, venue_type: str, attendee_count: int,
             event_duration: str, high_profile: bool, threat_categories: List[str]) -> Dict[str, Any]:
        """
        Run the threat monitoring tool.
        
        Args:
            event_type: Type of event
            venue_type: Type of venue
            attendee_count: Expected number of attendees
            event_duration: Duration of the event
            high_profile: Whether the event includes high-profile individuals
            threat_categories: Categories of threats to monitor
            
        Returns:
            Dictionary with threat monitoring plan
        """
        # In a real implementation, this would generate an actual threat monitoring plan
        # For now, we'll return a mock plan
        
        # Generate threat assessment based on inputs
        threats = []
        
        # Physical security threats
        if "physical" in threat_categories:
            # Base risk level
            risk_level = "low"
            
            # Adjust risk level based on inputs
            if attendee_count > 1000:
                risk_level = "medium"
            if attendee_count > 5000:
                risk_level = "high"
            if high_profile:
                risk_level = "high" if risk_level != "critical" else risk_level
            if venue_type.lower() in ["outdoor", "public", "open"]:
                risk_level = "medium" if risk_level == "low" else risk_level
            
            threats.append({
                "category": "physical",
                "name": "Unauthorized Access",
                "description": "Risk of unauthorized individuals accessing restricted areas",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Access control systems at all entry points",
                    "Security personnel stationed at key locations",
                    "Regular perimeter checks"
                ],
                "response_procedures": [
                    "Immediate notification of security team",
                    "Escort unauthorized individuals out of restricted areas",
                    "Document incidents and review access control measures"
                ]
            })
            
            threats.append({
                "category": "physical",
                "name": "Crowd Management Incidents",
                "description": "Risk of overcrowding, stampedes, or other crowd-related incidents",
                "risk_level": "high" if attendee_count > 1000 else "medium",
                "monitoring_measures": [
                    "Real-time crowd density monitoring",
                    "CCTV surveillance of high-traffic areas",
                    "Regular headcounts in different zones"
                ],
                "response_procedures": [
                    "Implement crowd control measures",
                    "Open additional exits if necessary",
                    "Deploy security personnel to manage flow"
                ]
            })
        
        # Cyber security threats
        if "cyber" in threat_categories:
            # Base risk level
            risk_level = "medium"
            
            # Adjust risk level based on inputs
            if high_profile:
                risk_level = "high"
            if event_type.lower() in ["tech", "technology", "digital"]:
                risk_level = "high"
            
            threats.append({
                "category": "cyber",
                "name": "Data Breach",
                "description": "Risk of unauthorized access to attendee or event data",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Real-time monitoring of network traffic",
                    "Intrusion detection systems",
                    "Regular security scans"
                ],
                "response_procedures": [
                    "Isolate affected systems",
                    "Implement incident response plan",
                    "Notify affected individuals if necessary"
                ]
            })
            
            threats.append({
                "category": "cyber",
                "name": "Wi-Fi Security",
                "description": "Risk of attacks on event Wi-Fi networks",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Secure Wi-Fi configuration",
                    "Network traffic monitoring",
                    "Regular security scans"
                ],
                "response_procedures": [
                    "Shut down compromised networks",
                    "Switch to backup systems",
                    "Notify attendees of security issues"
                ]
            })
        
        # Health and safety threats
        if "health" in threat_categories:
            # Base risk level
            risk_level = "medium"
            
            # Adjust risk level based on inputs
            if attendee_count > 1000:
                risk_level = "medium" if risk_level == "low" else risk_level
            if event_duration.lower().find("day") != -1:
                risk_level = "medium" if risk_level == "low" else risk_level
            
            threats.append({
                "category": "health",
                "name": "Medical Emergencies",
                "description": "Risk of attendee medical emergencies",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Medical staff on site",
                    "First aid stations",
                    "Emergency response protocols"
                ],
                "response_procedures": [
                    "Immediate medical assistance",
                    "Clear area for medical personnel",
                    "Contact emergency services if necessary"
                ]
            })
            
            threats.append({
                "category": "health",
                "name": "Food Safety",
                "description": "Risk of foodborne illness from event catering",
                "risk_level": "medium",
                "monitoring_measures": [
                    "Food safety inspections",
                    "Temperature monitoring",
                    "Vendor certification verification"
                ],
                "response_procedures": [
                    "Remove affected food items",
                    "Provide medical assistance to affected individuals",
                    "Document incidents and notify health authorities if necessary"
                ]
            })
        
        # Weather-related threats for outdoor events
        if "weather" in threat_categories and venue_type.lower() in ["outdoor", "open"]:
            threats.append({
                "category": "weather",
                "name": "Severe Weather",
                "description": "Risk of severe weather affecting the event",
                "risk_level": "medium",
                "monitoring_measures": [
                    "Weather forecast monitoring",
                    "On-site weather stations",
                    "Lightning detection systems"
                ],
                "response_procedures": [
                    "Implement weather emergency plan",
                    "Move attendees to shelter if necessary",
                    "Postpone or cancel outdoor activities if required"
                ]
            })
        
        # Generate monitoring schedule
        monitoring_schedule = []
        
        # Pre-event monitoring
        monitoring_schedule.append({
            "phase": "pre-event",
            "timeframe": "1 week before event",
            "activities": [
                "Conduct initial threat assessment",
                "Test all monitoring systems",
                "Brief security personnel on monitoring protocols"
            ]
        })
        
        # During event monitoring
        monitoring_schedule.append({
            "phase": "during-event",
            "timeframe": "Throughout event duration",
            "activities": [
                "Continuous monitoring of all identified threats",
                "Regular security sweeps",
                "Shift changes for monitoring personnel"
            ]
        })
        
        # Post-event monitoring
        monitoring_schedule.append({
            "phase": "post-event",
            "timeframe": "24 hours after event",
            "activities": [
                "Final security sweep",
                "Data security verification",
                "Incident report compilation"
            ]
        })
        
        # Generate staffing requirements
        staffing_requirements = {
            "security_personnel": max(2, attendee_count // 100),
            "cyber_security_analysts": 2 if "cyber" in threat_categories else 0,
            "medical_staff": max(2, attendee_count // 500) if "health" in threat_categories else 0,
            "monitoring_center_staff": 2 + len(threat_categories)
        }
        
        return {
            "threat_monitoring_plan": {
                "event_type": event_type,
                "venue_type": venue_type,
                "attendee_count": attendee_count,
                "event_duration": event_duration,
                "high_profile": high_profile,
                "threat_categories": threat_categories,
                "identified_threats": threats,
                "monitoring_schedule": monitoring_schedule,
                "staffing_requirements": staffing_requirements,
                "equipment_requirements": [
                    {"name": "CCTV Cameras", "quantity": max(4, attendee_count // 250)},
                    {"name": "Two-way Radios", "quantity": staffing_requirements["security_personnel"] + 2},
                    {"name": "Network Monitoring Systems", "quantity": 1 if "cyber" in threat_categories else 0},
                    {"name": "Weather Monitoring Equipment", "quantity": 1 if "weather" in threat_categories else 0}
                ]
            },
            "plan_id": f"threat-{uuid.uuid4().hex[:8]}",
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class IncidentResponseInput(BaseModel):
    """Input schema for the incident response tool."""
    
    event_type: str = Field(..., description="Type of event")
    venue_type: str = Field(..., description="Type of venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    incident_types: List[str] = Field(..., description="Types of incidents to plan for")
    high_profile: bool = Field(..., description="Whether the event includes high-profile individuals")
    response_team_size: Optional[int] = Field(None, description="Size of the response team")


class IncidentResponseTool(BaseTool):
    """Tool for planning and executing incident response."""
    
    name: str = "incident_response_tool"
    description: str = "Plan and implement incident response procedures for events"
    args_schema: Type[IncidentResponseInput] = IncidentResponseInput
    
    def _run(self, event_type: str, venue_type: str, attendee_count: int,
             incident_types: List[str], high_profile: bool,
             response_team_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the incident response tool.
        
        Args:
            event_type: Type of event
            venue_type: Type of venue
            attendee_count: Expected number of attendees
            incident_types: Types of incidents to plan for
            high_profile: Whether the event includes high-profile individuals
            response_team_size: Size of the response team
            
        Returns:
            Dictionary with incident response plan
        """
        # In a real implementation, this would generate an actual incident response plan
        # For now, we'll return a mock plan
        
        # Set default response team size if not provided
        if response_team_size is None:
            response_team_size = max(3, attendee_count // 500)
        
        # Generate response procedures for each incident type
        procedures = []
        
        # Security breach procedures
        if "security_breach" in incident_types:
            procedures.append({
                "incident_type": "security_breach",
                "name": "Security Breach Response",
                "description": "Procedures for responding to unauthorized access or security breaches",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor breach with limited impact",
                        "examples": ["Unauthorized access to non-sensitive area", "Tailgating at entry point"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant breach with potential for harm",
                        "examples": ["Unauthorized access to restricted area", "Credential theft"]
                    },
                    {
                        "level": "high",
                        "description": "Major breach with immediate risk",
                        "examples": ["Armed intruder", "Coordinated breach of multiple security layers"]
                    }
                ],
                "response_steps": [
                    "Identify and assess the breach",
                    "Secure affected areas",
                    "Notify security team and event management",
                    "Document the incident",
                    "Implement containment measures",
                    "Investigate root cause",
                    "Restore normal operations"
                ],
                "team_roles": [
                    {"role": "Incident Commander", "responsibilities": ["Overall coordination", "Decision making"]},
                    {"role": "Security Lead", "responsibilities": ["Direct security personnel", "Implement containment"]},
                    {"role": "Communications Officer", "responsibilities": ["Internal notifications", "External communications if needed"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 1", "Emergency phone tree", "Secure messaging app"],
                    "external_channels": ["Local law enforcement hotline", "Event management contact"]
                },
                "equipment_needed": [
                    "Two-way radios",
                    "Access control override tools",
                    "Incident documentation forms",
                    "Emergency contact list"
                ]
            })
        
        # Medical emergency procedures
        if "medical_emergency" in incident_types:
            procedures.append({
                "incident_type": "medical_emergency",
                "name": "Medical Emergency Response",
                "description": "Procedures for responding to medical emergencies",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor medical issue requiring basic first aid",
                        "examples": ["Minor cuts or bruises", "Headache", "Mild dehydration"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant medical issue requiring medical attention",
                        "examples": ["Allergic reaction", "Sprain or fracture", "Heat exhaustion"]
                    },
                    {
                        "level": "high",
                        "description": "Life-threatening medical emergency",
                        "examples": ["Heart attack", "Severe allergic reaction", "Unconsciousness"]
                    }
                ],
                "response_steps": [
                    "Assess the situation and ensure scene safety",
                    "Provide immediate first aid",
                    "Notify medical team",
                    "Clear area for medical personnel",
                    "Coordinate with emergency services if needed",
                    "Document the incident",
                    "Follow up with affected individual"
                ],
                "team_roles": [
                    {"role": "Medical Lead", "responsibilities": ["Coordinate medical response", "Assess severity"]},
                    {"role": "First Aid Provider", "responsibilities": ["Deliver immediate care", "Monitor vital signs"]},
                    {"role": "Logistics Support", "responsibilities": ["Clear access routes", "Guide emergency services"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 2", "Medical emergency hotline"],
                    "external_channels": ["Emergency services (911/999/112)", "Local hospital contact"]
                },
                "equipment_needed": [
                    "First aid kits",
                    "AED (Automated External Defibrillator)",
                    "Emergency medical supplies",
                    "Medical incident documentation forms"
                ]
            })
        
        # Fire or evacuation procedures
        if "fire" in incident_types or "evacuation" in incident_types:
            procedures.append({
                "incident_type": "evacuation",
                "name": "Fire and Evacuation Response",
                "description": "Procedures for responding to fires or other incidents requiring evacuation",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Localized incident with limited evacuation needed",
                        "examples": ["Small fire contained to one area", "Localized hazardous material spill"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant incident requiring partial evacuation",
                        "examples": ["Fire affecting multiple areas", "Structural damage to part of venue"]
                    },
                    {
                        "level": "high",
                        "description": "Major incident requiring full evacuation",
                        "examples": ["Large fire", "Major structural damage", "Widespread hazardous material release"]
                    }
                ],
                "response_steps": [
                    "Activate alarm system",
                    "Notify emergency response team",
                    "Begin evacuation procedures",
                    "Guide attendees to emergency exits",
                    "Conduct sweep of affected areas",
                    "Account for all attendees and staff",
                    "Coordinate with emergency services",
                    "Provide updates and instructions to evacuees"
                ],
                "team_roles": [
                    {"role": "Evacuation Coordinator", "responsibilities": ["Overall evacuation management", "Coordination with emergency services"]},
                    {"role": "Zone Marshals", "responsibilities": ["Guide evacuation in assigned zones", "Conduct sweeps"]},
                    {"role": "Assembly Point Coordinator", "responsibilities": ["Manage assembly points", "Account for evacuees"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 3", "Emergency announcement system"],
                    "external_channels": ["Emergency services", "Local authority emergency management"]
                },
                "equipment_needed": [
                    "Evacuation maps and signage",
                    "Emergency lighting",
                    "Megaphones",
                    "High-visibility vests for response team"
                ]
            })
        
        # Data breach procedures
        if "data_breach" in incident_types:
            procedures.append({
                "incident_type": "data_breach",
                "name": "Data Breach Response",
                "description": "Procedures for responding to data breaches or cyber security incidents",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor breach with limited data exposure",
                        "examples": ["Exposure of non-sensitive data", "Brief system outage"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant breach with potential for harm",
                        "examples": ["Exposure of personal data", "Unauthorized access to systems"]
                    },
                    {
                        "level": "high",
                        "description": "Major breach with serious consequences",
                        "examples": ["Exposure of financial data", "Widespread system compromise"]
                    }
                ],
                "response_steps": [
                    "Identify and assess the breach",
                    "Contain the breach",
                    "Notify IT security team",
                    "Preserve evidence",
                    "Investigate the breach",
                    "Notify affected individuals if required",
                    "Implement recovery procedures",
                    "Document lessons learned"
                ],
                "team_roles": [
                    {"role": "Cyber Incident Lead", "responsibilities": ["Overall coordination", "Technical assessment"]},
                    {"role": "IT Security Specialist", "responsibilities": ["Containment actions", "Technical investigation"]},
                    {"role": "Legal Advisor", "responsibilities": ["Compliance requirements", "Notification obligations"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Secure messaging platform", "Incident response hotline"],
                    "external_channels": ["Data protection authority", "Cyber security incident reporting"]
                },
                "equipment_needed": [
                    "Forensic analysis tools",
                    "Secure communication devices",
                    "Incident documentation templates",
                    "Data breach notification templates"
                ]
            })
        
        # Generate response team structure
        response_team = []
        
        # Core team members
        response_team.append({
            "role": "Incident Response Manager",
            "responsibilities": ["Overall coordination of incident response", "Decision making", "External communications"],
            "required_skills": ["Crisis management", "Leadership", "Communication"],
            "count": 1
        })
        
        response_team.append({
            "role": "Communications Coordinator",
            "responsibilities": ["Internal communications", "Updates to stakeholders", "Media liaison if needed"],
            "required_skills": ["Crisis communication", "Stakeholder management"],
            "count": 1
        })
        
        # Specialized team members based on incident types
        if "security_breach" in incident_types:
            response_team.append({
                "role": "Security Response Specialist",
                "responsibilities": ["Security breach response", "Physical security measures", "Coordination with security personnel"],
                "required_skills": ["Security management", "Threat assessment"],
                "count": max(1, response_team_size // 4)
            })
        
        if "medical_emergency" in incident_types:
            response_team.append({
                "role": "Medical Response Coordinator",
                "responsibilities": ["Medical emergency response", "Coordination with medical staff", "First aid provision"],
                "required_skills": ["First aid certification", "Emergency medical knowledge"],
                "count": max(1, response_team_size // 4)
            })
        
        if "fire" in incident_types or "evacuation" in incident_types:
            response_team.append({
                "role": "Evacuation Coordinator",
                "responsibilities": ["Evacuation procedures", "Assembly point management", "Coordination with emergency services"],
                "required_skills": ["Evacuation planning", "Emergency management"],
                "count": max(1, response_team_size // 4)
            })
        
        if "data_breach" in incident_types:
            response_team.append({
                "role": "Cyber Incident Responder",
                "responsibilities": ["Data breach response", "System security measures", "Digital evidence preservation"],
                "required_skills": ["IT security", "Data protection", "Forensic analysis"],
                "count": max(1, response_team_size // 4)
            })
        
        # Create an IncidentResponsePlan object
        plan = IncidentResponsePlan(
            name=f"Incident Response Plan for {event_type}",
            description=f"Comprehensive incident response plan for {event_type} at {venue_type} venue",
            incident_types_covered=incident_types,
            response_team=[{"role": member["role"], "responsibilities": member["responsibilities"]} for member in response_team],
            response_procedures=[{
                "incident_type": proc["incident_type"],
                "name": proc["name"],
                "description": proc["description"],
                "response_steps": proc["response_steps"]
            } for proc in procedures],
            communication_protocols={
                "emergency_contacts": [
                    {"name": "Event Manager", "contact": "Internal extension 100"},
                    {"name": "Security Lead", "contact": "Internal extension 101"},
                    {"name": "Medical Team", "contact": "Internal extension 102"},
                    {"name": "Local Emergency Services", "contact": "911/999/112"}
                ],
                "notification_procedures": [
                    "Initial notification to Incident Response Manager",
                    "Manager activates appropriate response team",
                    "Team communications via designated radio channel",
                    "Regular status updates to Event Manager",
                    "External communications via Communications Coordinator only"
                ]
            },
            status="draft"
        )
        
        # Generate an incident response plan ID
        plan_id = f"ir-{uuid.uuid4().hex[:8]}"
        
        return {
            "incident_response_plan": plan.dict(),
            "plan_id": plan_id,
            "team_size": sum(member["count"] for member in response_team),
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class SecurityReportingInput(BaseModel):
    """Input schema for the security reporting tool."""
    
    event_id: str = Field(..., description="ID of the event")
    report_type: str = Field(..., description="Type of report to generate")
    time_period: str = Field(..., description="Time period for the report")
    include_incidents: bool = Field(..., description="Whether to include security incidents in the report")
    include_compliance: bool = Field(..., description="Whether to include compliance status in the report")


class SecurityReportingTool(BaseTool):
    """Tool for generating security and compliance reports."""
    
    name: str = "security_reporting_tool"
    description: str = "Generate security and compliance reports for events"
    args_schema: Type[SecurityReportingInput] = SecurityReportingInput
    
    def _run(self, event_id: str, report_type: str, time_period: str,
             include_incidents: bool, include_compliance: bool) -> Dict[str, Any]:
        """
        Run the security reporting tool.
        
        Args:
            event_id: ID of the event
            report_type: Type of report to generate
            time_period: Time period for the report
            include_incidents: Whether to include security incidents in the report
            include_compliance: Whether to include compliance status in the report
            
        Returns:
            Dictionary with security report
        """
        # In a real implementation, this would generate an actual report based on data
        # For now, we'll return a mock report
        
        # Generate mock incidents if requested
        incidents = []
        if include_incidents:
            incidents = [
                SecurityIncident(
                    incident_type="unauthorized_access",
                    description="Unauthorized individual attempted to access VIP area",
                    severity="medium",
                    date_time=datetime.now() - datetime.timedelta(days=2, hours=3),
                    location="VIP entrance",
                    affected_assets=["VIP area"],
                    resolution_status="resolved",
                    resolution_details="Individual escorted from area, credentials verified"
                ).dict(),
                SecurityIncident(
                    incident_type="suspicious_activity",
                    description="Suspicious package left unattended",
                    severity="high",
                    date_time=datetime.now() - datetime.timedelta(days=1, hours=5),
                    location="Main hall entrance",
                    affected_assets=["Entrance area"],
                    resolution_status="resolved",
                    resolution_details="Package inspected by security, contained personal items"
                ).dict(),
                SecurityIncident(
                    incident_type="system_outage",
                    description="Brief outage of access control system",
                    severity="medium",
                    date_time=datetime.now() - datetime.timedelta(hours=12),
                    location="All access points",
                    affected_assets=["Access control system"],
                    resolution_status="resolved",
                    resolution_details="System restarted, backup procedures implemented during outage"
                ).dict()
            ]
        
        # Generate mock compliance status if requested
        compliance_status = {}
        if include_compliance:
            compliance_status = {
                "overall_status": "compliant",
                "requirements_met": 42,
                "requirements_pending": 3,
                "requirements_not_met": 0,
                "compliance_percentage": 93.3,
                "key_areas": [
                    {
                        "area": "Data Protection",
                        "status": "compliant",
                        "details": "All data protection measures implemented"
                    },
                    {
                        "area": "Physical Security",
                        "status": "compliant",
                        "details": "All physical security protocols in place"
                    },
                    {
                        "area": "Staff Training",
                        "status": "partially_compliant",
                        "details": "3 staff members pending security training completion"
                    }
                ]
            }
        
        # Create a ComplianceReport object
        report = ComplianceReport(
            report_type=report_type,
            event_id=event_id,
            time_period=time_period,
            generation_date=datetime.now(),
            summary=f"Security and compliance report for event {event_id} covering {time_period}",
            key_findings=[
                "Overall security posture is strong",
                "Minor incidents handled according to procedures",
                "Compliance requirements largely met with few pending items"
            ],
            recommendations=[
                "Complete remaining staff training",
                "Conduct follow-up audit on access control procedures",
                "Update incident response documentation based on recent experiences"
            ]
        )
        
        # Generate a report ID
        report_id = f"report-{uuid.uuid4().hex[:8]}"
        
        return {
            "report": report.dict(),
            "report_id": report_id,
            "incidents": incidents if include_incidents else [],
            "compliance_status": compliance_status if include_compliance else {},
            "generation_details": {
                "generated_at": datetime.now().isoformat(),
                "generated_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs)
    DataProtectionMeasure,
    ComplianceAudit,
    SecurityIncident,
    IncidentResponsePlan,
    ComplianceReport,
    RegulatoryUpdate
)


class RequirementTrackingInput(BaseModel):
    """Input schema for the requirement tracking tool."""
    
    name: str = Field(..., description="Name of the requirement")
    description: str = Field(..., description="Description of the requirement")
    category: str = Field(..., description="Category of the requirement")
    jurisdiction: str = Field(..., description="Jurisdiction where the requirement applies")
    applicable_event_types: List[str] = Field(..., description="Types of events to which this requirement applies")
    documentation_needed: Optional[List[str]] = Field(None, description="Documentation needed to demonstrate compliance")
    verification_steps: Optional[List[str]] = Field(None, description="Steps to verify compliance with this requirement")


class RequirementTrackingTool(BaseTool):
    """Tool for tracking legal and regulatory requirements."""
    
    name: str = "requirement_tracking_tool"
    description: str = "Track legal and regulatory requirements for an event"
    args_schema: Type[RequirementTrackingInput] = RequirementTrackingInput
    
    def _run(self, name: str, description: str, category: str, jurisdiction: str,
             applicable_event_types: List[str], documentation_needed: Optional[List[str]] = None,
             verification_steps: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the requirement tracking tool.
        
        Args:
            name: Name of the requirement
            description: Description of the requirement
            category: Category of the requirement
            jurisdiction: Jurisdiction where the requirement applies
            applicable_event_types: Types of events to which this requirement applies
            documentation_needed: Documentation needed to demonstrate compliance
            verification_steps: Steps to verify compliance with this requirement
            
        Returns:
            Dictionary with requirement details
        """
        # In a real implementation, this would store the requirement in a database
        # For now, we'll return a mock requirement
        
        # Set default values if not provided
        if documentation_needed is None:
            documentation_needed = [
                "Compliance policy document",
                "Signed acknowledgment forms",
                "Verification checklist"
            ]
        
        if verification_steps is None:
            verification_steps = [
                "Review documentation",
                "Conduct compliance check",
                "Obtain necessary approvals"
            ]
        
        # Create a ComplianceRequirement object
        requirement = ComplianceRequirement(
            name=name,
            description=description,
            category=category,
            jurisdiction=jurisdiction,
            applicable_event_types=applicable_event_types,
            documentation_needed=documentation_needed,
            verification_steps=verification_steps,
            status="not_started"
        )
        
        # Generate a requirement ID
        requirement_id = f"req-{uuid.uuid4().hex[:8]}"
        
        return {
            "requirement_id": requirement_id,
            "requirement": requirement.dict(),
            "tracking_details": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class DocumentationReviewInput(BaseModel):
    """Input schema for the documentation review tool."""
    
    document_type: str = Field(..., description="Type of document to review")
    document_content: str = Field(..., description="Content of the document to review")
    requirements: List[str] = Field(..., description="Requirements to check against")
    event_type: str = Field(..., description="Type of event for which the document is being reviewed")


class DocumentationReviewTool(BaseTool):
    """Tool for reviewing compliance documentation."""
    
    name: str = "documentation_review_tool"
    description: str = "Review documentation for compliance with requirements"
    args_schema: Type[DocumentationReviewInput] = DocumentationReviewInput
    
    def _run(self, document_type: str, document_content: str, requirements: List[str],
             event_type: str) -> Dict[str, Any]:
        """
        Run the documentation review tool.
        
        Args:
            document_type: Type of document to review
            document_content: Content of the document to review
            requirements: Requirements to check against
            event_type: Type of event for which the document is being reviewed
            
        Returns:
            Dictionary with review results
        """
        # In a real implementation, this would analyze the document against requirements
        # For now, we'll return mock review results
        
        # Generate mock findings
        findings = []
        
        # For demonstration purposes, we'll create some mock findings
        if "privacy" in document_type.lower() or "data" in document_type.lower():
            findings.append({
                "requirement": "Data Protection",
                "status": "compliant",
                "details": "Document includes appropriate data protection clauses"
            })
            findings.append({
                "requirement": "Consent Mechanisms",
                "status": "non_compliant",
                "details": "Document lacks clear consent mechanisms for data collection"
            })
        elif "security" in document_type.lower():
            findings.append({
                "requirement": "Access Controls",
                "status": "compliant",
                "details": "Document specifies appropriate access control measures"
            })
            findings.append({
                "requirement": "Incident Response",
                "status": "partially_compliant",
                "details": "Document includes incident response procedures but lacks specific timelines"
            })
        elif "contract" in document_type.lower() or "agreement" in document_type.lower():
            findings.append({
                "requirement": "Liability Clauses",
                "status": "compliant",
                "details": "Document includes appropriate liability clauses"
            })
            findings.append({
                "requirement": "Termination Provisions",
                "status": "compliant",
                "details": "Document includes clear termination provisions"
            })
        else:
            findings.append({
                "requirement": "General Compliance",
                "status": "needs_review",
                "details": "Document requires further review by compliance specialist"
            })
        
        # Generate recommendations based on findings
        recommendations = []
        for finding in findings:
            if finding["status"] == "non_compliant":
                recommendations.append(f"Address {finding['requirement']} issues: {finding['details']}")
            elif finding["status"] == "partially_compliant":
                recommendations.append(f"Improve {finding['requirement']}: {finding['details']}")
            elif finding["status"] == "needs_review":
                recommendations.append(f"Seek specialist review for {finding['requirement']}")
        
        # Calculate compliance score
        compliant_count = sum(1 for finding in findings if finding["status"] == "compliant")
        total_count = len(findings)
        compliance_score = (compliant_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "document_type": document_type,
            "event_type": event_type,
            "findings": findings,
            "recommendations": recommendations,
            "compliance_score": compliance_score,
            "review_details": {
                "reviewed_at": datetime.now().isoformat(),
                "reviewed_by": "Compliance & Security Agent",
                "requirements_checked": requirements
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class AuditSupportInput(BaseModel):
    """Input schema for the audit support tool."""
    
    audit_name: str = Field(..., description="Name of the audit")
    audit_description: str = Field(..., description="Description of the audit scope and purpose")
    requirements_to_check: List[str] = Field(..., description="Requirements to check in this audit")
    event_details: Dict[str, Any] = Field(..., description="Details of the event being audited")


class AuditSupportTool(BaseTool):
    """Tool for supporting compliance audits."""
    
    name: str = "audit_support_tool"
    description: str = "Support compliance audits for events"
    args_schema: Type[AuditSupportInput] = AuditSupportInput
    
    def _run(self, audit_name: str, audit_description: str, requirements_to_check: List[str],
             event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the audit support tool.
        
        Args:
            audit_name: Name of the audit
            audit_description: Description of the audit scope and purpose
            requirements_to_check: Requirements to check in this audit
            event_details: Details of the event being audited
            
        Returns:
            Dictionary with audit results
        """
        # In a real implementation, this would conduct an actual audit
        # For now, we'll return mock audit results
        
        # Generate mock findings
        findings = []
        
        # For demonstration purposes, we'll create some mock findings
        for i, requirement in enumerate(requirements_to_check):
            # Alternate between different statuses for demonstration
            if i % 3 == 0:
                status = "compliant"
                details = f"Requirement '{requirement}' is fully implemented and documented"
            elif i % 3 == 1:
                status = "partially_compliant"
                details = f"Requirement '{requirement}' is partially implemented but lacks complete documentation"
            else:
                status = "non_compliant"
                details = f"Requirement '{requirement}' is not implemented or documented"
            
            findings.append({
                "requirement": requirement,
                "status": status,
                "details": details,
                "evidence": f"Evidence for {requirement} compliance check"
            })
        
        # Generate recommendations based on findings
        recommendations = []
        for finding in findings:
            if finding["status"] == "non_compliant":
                recommendations.append(f"Implement and document {finding['requirement']}")
            elif finding["status"] == "partially_compliant":
                recommendations.append(f"Complete documentation for {finding['requirement']}")
        
        # Create a ComplianceAudit object
        audit = ComplianceAudit(
            name=audit_name,
            description=audit_description,
            requirements_checked=requirements_to_check,
            findings=findings,
            recommendations=recommendations,
            completion_date=datetime.now(),
            status="completed"
        )
        
        # Generate an audit ID
        audit_id = f"audit-{uuid.uuid4().hex[:8]}"
        
        return {
            "audit_id": audit_id,
            "audit": audit.dict(),
            "summary": {
                "total_requirements": len(requirements_to_check),
                "compliant": sum(1 for finding in findings if finding["status"] == "compliant"),
                "partially_compliant": sum(1 for finding in findings if finding["status"] == "partially_compliant"),
                "non_compliant": sum(1 for finding in findings if finding["status"] == "non_compliant"),
                "recommendations_count": len(recommendations)
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class RegulatoryUpdateInput(BaseModel):
    """Input schema for the regulatory update tool."""
    
    regulation_name: str = Field(..., description="Name of the regulation")
    update_description: str = Field(..., description="Description of the update")
    effective_date: str = Field(..., description="Date when the update becomes effective (YYYY-MM-DD)")
    jurisdiction: str = Field(..., description="Jurisdiction where the update applies")
    event_types_affected: List[str] = Field(..., description="Types of events affected by this update")


class RegulatoryUpdateTool(BaseTool):
    """Tool for monitoring regulatory updates."""
    
    name: str = "regulatory_update_tool"
    description: str = "Monitor and track regulatory updates relevant to events"
    args_schema: Type[RegulatoryUpdateInput] = RegulatoryUpdateInput
    
    def _run(self, regulation_name: str, update_description: str, effective_date: str,
             jurisdiction: str, event_types_affected: List[str]) -> Dict[str, Any]:
        """
        Run the regulatory update tool.
        
        Args:
            regulation_name: Name of the regulation
            update_description: Description of the update
            effective_date: Date when the update becomes effective
            jurisdiction: Jurisdiction where the update applies
            event_types_affected: Types of events affected by this update
            
        Returns:
            Dictionary with regulatory update details
        """
        # In a real implementation, this would store the update in a database
        # For now, we'll return a mock update
        
        # Parse the effective date
        effective_date_obj = datetime.strptime(effective_date, "%Y-%m-%d")
        
        # Generate impact assessment based on the update description
        impact_assessment = {
            "severity": "medium",
            "areas_affected": ["data_collection", "consent_management", "documentation"],
            "implementation_complexity": "moderate",
            "estimated_effort": "2-3 weeks",
            "cost_implications": "moderate"
        }
        
        # Generate required actions based on the update description
        required_actions = [
            f"Update privacy policies to comply with {regulation_name}",
            f"Revise consent forms to include new requirements",
            f"Train staff on {regulation_name} compliance",
            f"Update documentation to reflect new requirements",
            f"Conduct compliance audit after implementation"
        ]
        
        # Create a RegulatoryUpdate object
        regulatory_update = RegulatoryUpdate(
            regulation_name=regulation_name,
            update_description=update_description,
            effective_date=effective_date_obj,
            jurisdiction=jurisdiction,
            impact_assessment=impact_assessment,
            required_actions=required_actions,
            status="identified"
        )
        
        # Generate an update ID
        update_id = f"update-{uuid.uuid4().hex[:8]}"
        
        return {
            "update_id": update_id,
            "regulatory_update": regulatory_update.dict(),
            "time_to_compliance": (effective_date_obj - datetime.now()).days,
            "affected_event_types": event_types_affected,
            "tracking_details": {
                "identified_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "identified_by": "Compliance & Security Agent"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class AccessControlInput(BaseModel):
    """Input schema for the access control tool."""
    
    event_type: str = Field(..., description="Type of event")
    venue_type: str = Field(..., description="Type of venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    security_level: str = Field(..., description="Required security level (low, medium, high, critical)")
    special_requirements: Optional[List[str]] = Field(None, description="Special access control requirements")


class AccessControlTool(BaseTool):
    """Tool for planning and implementing access control."""
    
    name: str = "access_control_tool"
    description: str = "Plan and implement access control for events"
    args_schema: Type[AccessControlInput] = AccessControlInput
    
    def _run(self, event_type: str, venue_type: str, attendee_count: int,
             security_level: str, special_requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the access control tool.
        
        Args:
            event_type: Type of event
            venue_type: Type of venue
            attendee_count: Expected number of attendees
            security_level: Required security level
            special_requirements: Special access control requirements
            
        Returns:
            Dictionary with access control plan
        """
        # In a real implementation, this would generate an actual access control plan
        # For now, we'll return a mock plan
        
        # Set default special requirements if not provided
        if special_requirements is None:
            special_requirements = []
        
        # Generate access control protocols based on inputs
        protocols = []
        
        # Basic access control for all events
        protocols.append(
            SecurityProtocol(
                name="Attendee Identification",
                description="System for identifying and verifying attendees",
                category="access_control",
                risk_level="medium",
                implementation_steps=[
                    "Set up registration verification system",
                    "Prepare attendee badges or wristbands",
                    "Train staff on verification procedures"
                ],
                verification_method="Test verification process with sample attendees",
                status="not_implemented"
            ).dict()
        )
        
        # Add protocols based on security level
        if security_level.lower() in ["medium", "high", "critical"]:
            protocols.append(
                SecurityProtocol(
                    name="Perimeter Security",
                    description="Measures to secure the event perimeter",
                    category="physical",
                    risk_level="medium",
                    implementation_steps=[
                        "Define secure perimeter boundaries",
                        "Establish entry and exit points",
                        "Deploy security personnel at key points"
                    ],
                    verification_method="Conduct perimeter security walkthrough",
                    status="not_implemented"
                ).dict()
            )
        
        if security_level.lower() in ["high", "critical"]:
            protocols.append(
                SecurityProtocol(
                    name="Security Screening",
                    description="Screening process for attendees and items",
                    category="physical",
                    risk_level="high",
                    implementation_steps=[
                        "Set up screening equipment",
                        "Establish screening procedures",
                        "Train security personnel on screening protocols"
                    ],
                    verification_method="Test screening process with security team",
                    status="not_implemented"
                ).dict()
            )
        
        if security_level.lower() == "critical":
            protocols.append(
                SecurityProtocol(
                    name="Advanced Security Measures",
                    description="Advanced security measures for high-risk events",
                    category="physical",
                    risk_level="critical",
                    implementation_steps=[
                        "Coordinate with local law enforcement",
                        "Implement multi-layer security checks",
                        "Establish command center for security operations"
                    ],
                    verification_method="Conduct full security drill with all personnel",
                    status="not_implemented"
                ).dict()
            )
        
        # Add protocols for large events
        if attendee_count > 500:
            protocols.append(
                SecurityProtocol(
                    name="Crowd Management",
                    description="Measures for managing large crowds",
                    category="physical",
                    risk_level="medium",
                    implementation_steps=[
                        "Develop crowd flow plan",
                        "Establish capacity limits for different areas",
                        "Train staff on crowd management techniques"
                    ],
                    verification_method="Simulate crowd flow with staff",
                    status="not_implemented"
                ).dict()
            )
        
        # Add protocols for special requirements
        for requirement in special_requirements:
            if "vip" in requirement.lower():
                protocols.append(
                    SecurityProtocol(
                        name="VIP Security",
                        description="Special security measures for VIPs",
                        category="access_control",
                        risk_level="high",
                        implementation_steps=[
                            "Establish VIP-only areas",
                            "Assign dedicated security personnel to VIPs",
                            "Create separate entry and exit routes for VIPs"
                        ],
                        verification_method="Conduct VIP security walkthrough",
                        status="not_implemented"
                    ).dict()
                )
            elif "data" in requirement.lower() or "privacy" in requirement.lower():
                protocols.append(
                    SecurityProtocol(
                        name="Data Security",
                        description="Measures to protect sensitive data",
                        category="data",
                        risk_level="high",
                        implementation_steps=[
                            "Implement data encryption",
                            "Establish data access controls",
                            "Train staff on data handling procedures"
                        ],
                        verification_method="Conduct data security audit",
                        status="not_implemented"
                    ).dict()
                )
        
        # Generate staffing requirements based on attendee count and security level
        security_staff_count = max(2, attendee_count // 100)
        if security_level.lower() == "high":
            security_staff_count = max(4, attendee_count // 75)
        elif security_level.lower() == "critical":
            security_staff_count = max(6, attendee_count // 50)
        
        # Generate equipment requirements
        equipment_requirements = [
            {"name": "Attendee Badges", "quantity": attendee_count},
            {"name": "Badge Scanners", "quantity": max(2, attendee_count // 200)},
            {"name": "Two-way Radios", "quantity": security_staff_count + 2}
        ]
        
        if security_level.lower() in ["medium", "high", "critical"]:
            equipment_requirements.append({"name": "Security Barriers", "quantity": max(10, attendee_count // 100)})
        
        if security_level.lower() in ["high", "critical"]:
            equipment_requirements.append({"name": "Metal Detectors", "quantity": max(2, attendee_count // 300)})
            equipment_requirements.append({"name": "Security Cameras", "quantity": max(4, attendee_count // 200)})
        
        return {
            "access_control_plan": {
                "event_type": event_type,
                "venue_type": venue_type,
                "attendee_count": attendee_count,
                "security_level": security_level,
                "special_requirements": special_requirements,
                "protocols": protocols,
                "staffing_requirements": {
                    "security_staff": security_staff_count,
                    "access_control_staff": max(2, attendee_count // 200),
                    "supervisors": max(1, security_staff_count // 5)
                },
                "equipment_requirements": equipment_requirements
            },
            "plan_id": f"access-{uuid.uuid4().hex[:8]}",
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class DataProtectionInput(BaseModel):
    """Input schema for the data protection tool."""
    
    event_type: str = Field(..., description="Type of event")
    data_types_collected: List[str] = Field(..., description="Types of data collected for the event")
    jurisdictions: List[str] = Field(..., description="Jurisdictions where the event and data collection occur")
    processing_purposes: List[str] = Field(..., description="Purposes for processing the collected data")
    third_party_sharing: bool = Field(..., description="Whether data will be shared with third parties")
    retention_period: Optional[str] = Field(None, description="Period for which data will be retained")


class DataProtectionTool(BaseTool):
    """Tool for implementing data protection measures."""
    
    name: str = "data_protection_tool"
    description: str = "Implement data protection measures for events"
    args_schema: Type[DataProtectionInput] = DataProtectionInput
    
    def _run(self, event_type: str, data_types_collected: List[str], jurisdictions: List[str],
             processing_purposes: List[str], third_party_sharing: bool,
             retention_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the data protection tool.
        
        Args:
            event_type: Type of event
            data_types_collected: Types of data collected for the event
            jurisdictions: Jurisdictions where the event and data collection occur
            processing_purposes: Purposes for processing the collected data
            third_party_sharing: Whether data will be shared with third parties
            retention_period: Period for which data will be retained
            
        Returns:
            Dictionary with data protection plan
        """
        # In a real implementation, this would generate an actual data protection plan
        # For now, we'll return a mock plan
        
        # Set default retention period if not provided
        if retention_period is None:
            retention_period = "1 year after event"
        
        # Determine applicable regulations based on jurisdictions
        applicable_regulations = []
        for jurisdiction in jurisdictions:
            if jurisdiction.lower() in ["eu", "european union", "europe"]:
                applicable_regulations.append("GDPR")
            if jurisdiction.lower() in ["california", "ca", "us-ca"]:
                applicable_regulations.append("CCPA")
            if jurisdiction.lower() in ["us", "united states", "usa"]:
                applicable_regulations.append("US State Privacy Laws")
                if "health" in data_types_collected or "medical" in data_types_collected:
                    applicable_regulations.append("HIPAA")
            if jurisdiction.lower() in ["canada"]:
                applicable_regulations.append("PIPEDA")
            if jurisdiction.lower() in ["australia"]:
                applicable_regulations.append("Privacy Act 1988")
            if jurisdiction.lower() in ["uk", "united kingdom"]:
                applicable_regulations.append("UK GDPR")
                applicable_regulations.append("Data Protection Act 2018")
        
        # Remove duplicates
        applicable_regulations = list(set(applicable_regulations))
        
        # Generate data protection measures based on inputs
        measures = []
        
        # Basic data protection for all events
        measures.append(
            DataProtectionMeasure(
                name="Privacy Notice",
                description="Clear and comprehensive privacy notice for attendees",
                data_types_covered=data_types_collected,
                applicable_regulations=applicable_regulations,
                implementation_steps=[
                    "Draft privacy notice covering all required elements",
                    "Review privacy notice with legal team",
                    "Make privacy notice accessible to all attendees"
                ],
                status="not_implemented"
            ).dict()
        )
        
        measures.append(
            DataProtectionMeasure(
                name="Data Collection Consent",
                description="Mechanism for obtaining consent for data collection",
                data_types_covered=data_types_collected,
                applicable_regulations=applicable_regulations,
                implementation_steps=[
                    "Design consent mechanism",
                    "Ensure consent is freely given, specific, informed, and unambiguous",
                    "Implement consent recording system"
                ],
                status="not_implemented"
            ).dict()
        )
        
        # Add measures for specific data types
        if any(dt for dt in data_types_collected if "personal" in dt.lower()):
            measures.append(
                DataProtectionMeasure(
                    name="Personal Data Security",
                    description="Measures to secure personal data",
                    data_types_covered=[dt for dt in data_types_collected if "personal" in dt.lower()],
                    applicable_regulations=applicable_regulations,
                    implementation_steps=[
                        "Implement data encryption",
                        "Establish access controls",
                        "Set up secure data storage"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        if any(dt for dt in data_types_collected if "financial" in dt.lower() or "payment" in dt.lower()):
            measures.append(
                DataProtectionMeasure(
                    name="Financial Data Protection",
                    description="Measures to protect financial data",
                    data_types_covered=[dt for dt in data_types_collected if "financial" in dt.lower() or "payment" in dt.lower()],
                    applicable_regulations=applicable_regulations + ["PCI DSS"],
                    implementation_steps=[
                        "Implement PCI DSS compliant payment processing",
                        "Minimize storage of financial data",
                        "Secure transmission of financial information"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        if any(dt for dt in data_types_collected if "health" in dt.lower() or "medical" in dt.lower()):
            measures.append(
                DataProtectionMeasure(
                    name="Health Data Protection",
                    description="Measures to protect health-related data",
                    data_types_covered=[dt for dt in data_types_collected if "health" in dt.lower() or "medical" in dt.lower()],
                    applicable_regulations=[reg for reg in applicable_regulations if reg in ["HIPAA", "GDPR"]],
                    implementation_steps=[
                        "Implement enhanced security for health data",
                        "Obtain explicit consent for health data processing",
                        "Limit access to health data to authorized personnel only"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        # Add measures for third-party sharing
        if third_party_sharing:
            measures.append(
                DataProtectionMeasure(
                    name="Third-Party Data Sharing Controls",
                    description="Controls for sharing data with third parties",
                    data_types_covered=data_types_collected,
                    applicable_regulations=applicable_regulations,
                    implementation_steps=[
                        "Identify all third parties receiving data",
                        "Establish data processing agreements with third parties",
                        "Implement data transfer mechanisms for cross-border transfers",
                        "Ensure third parties maintain adequate security measures"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        # Add data retention measure
        measures.append(
            DataProtectionMeasure(
                name="Data Retention Controls",
                description=f"Controls for data retention and deletion after {retention_period}",
                data_types_covered=data_types_collected,
                applicable_regulations=applicable_regulations,
                implementation_steps=[
                    "Implement data retention policy",
                    f"Set up automated deletion after {retention_period}",
                    "Establish process for handling retention exceptions"
                ],
                status="not_implemented"
            ).dict()
        )
        
        # Add data subject rights measure if GDPR or CCPA applies
        if "GDPR" in applicable_regulations or "CCPA" in applicable_regulations:
            measures.append(
                DataProtectionMeasure(
                    name="Data Subject Rights Procedures",
                    description="Procedures for handling data subject rights requests",
                    data_types_covered=data_types_collected,
                    applicable_regulations=[reg for reg in applicable_regulations if reg in ["GDPR", "CCPA", "UK GDPR"]],
                    implementation_steps=[
                        "Establish process for receiving rights requests",
                        "Implement procedures for responding to access, deletion, and other requests",
                        "Train staff on handling rights requests",
                        "Set up record-keeping for rights requests"
                    ],
                    status="not_implemented"
                ).dict()
            )
        
        # Generate documentation requirements
        documentation_requirements = [
            "Privacy Notice",
            "Consent Forms",
            "Data Processing Inventory",
            "Data Protection Impact Assessment"
        ]
        
        if third_party_sharing:
            documentation_requirements.append("Third-Party Data Processing Agreements")
        
        if "GDPR" in applicable_regulations:
            documentation_requirements.append("Records of Processing Activities")
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)

class ThreatMonitoringInput(BaseModel):
    """Input schema for the threat monitoring tool."""
    
    event_type: str = Field(..., description="Type of event")
    venue_type: str = Field(..., description="Type of venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    event_duration: str = Field(..., description="Duration of the event (e.g., '3 days', '8 hours')")
    high_profile: bool = Field(..., description="Whether the event includes high-profile individuals")
    threat_categories: List[str] = Field(..., description="Categories of threats to monitor")


class ThreatMonitoringTool(BaseTool):
    """Tool for monitoring security threats."""
    
    name: str = "threat_monitoring_tool"
    description: str = "Monitor and assess security threats for events"
    args_schema: Type[ThreatMonitoringInput] = ThreatMonitoringInput
    
    def _run(self, event_type: str, venue_type: str, attendee_count: int,
             event_duration: str, high_profile: bool, threat_categories: List[str]) -> Dict[str, Any]:
        """
        Run the threat monitoring tool.
        
        Args:
            event_type: Type of event
            venue_type: Type of venue
            attendee_count: Expected number of attendees
            event_duration: Duration of the event
            high_profile: Whether the event includes high-profile individuals
            threat_categories: Categories of threats to monitor
            
        Returns:
            Dictionary with threat monitoring plan
        """
        # In a real implementation, this would generate an actual threat monitoring plan
        # For now, we'll return a mock plan
        
        # Generate threat assessment based on inputs
        threats = []
        
        # Physical security threats
        if "physical" in threat_categories:
            # Base risk level
            risk_level = "low"
            
            # Adjust risk level based on inputs
            if attendee_count > 1000:
                risk_level = "medium"
            if attendee_count > 5000:
                risk_level = "high"
            if high_profile:
                risk_level = "high" if risk_level != "critical" else risk_level
            if venue_type.lower() in ["outdoor", "public", "open"]:
                risk_level = "medium" if risk_level == "low" else risk_level
            
            threats.append({
                "category": "physical",
                "name": "Unauthorized Access",
                "description": "Risk of unauthorized individuals accessing restricted areas",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Access control systems at all entry points",
                    "Security personnel stationed at key locations",
                    "Regular perimeter checks"
                ],
                "response_procedures": [
                    "Immediate notification of security team",
                    "Escort unauthorized individuals out of restricted areas",
                    "Document incidents and review access control measures"
                ]
            })
            
            threats.append({
                "category": "physical",
                "name": "Crowd Management Incidents",
                "description": "Risk of overcrowding, stampedes, or other crowd-related incidents",
                "risk_level": "high" if attendee_count > 1000 else "medium",
                "monitoring_measures": [
                    "Real-time crowd density monitoring",
                    "CCTV surveillance of high-traffic areas",
                    "Regular headcounts in different zones"
                ],
                "response_procedures": [
                    "Implement crowd control measures",
                    "Open additional exits if necessary",
                    "Deploy security personnel to manage flow"
                ]
            })
        
        # Cyber security threats
        if "cyber" in threat_categories:
            # Base risk level
            risk_level = "medium"
            
            # Adjust risk level based on inputs
            if high_profile:
                risk_level = "high"
            if event_type.lower() in ["tech", "technology", "digital"]:
                risk_level = "high"
            
            threats.append({
                "category": "cyber",
                "name": "Data Breach",
                "description": "Risk of unauthorized access to attendee or event data",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Real-time monitoring of network traffic",
                    "Intrusion detection systems",
                    "Regular security scans"
                ],
                "response_procedures": [
                    "Isolate affected systems",
                    "Implement incident response plan",
                    "Notify affected individuals if necessary"
                ]
            })
            
            threats.append({
                "category": "cyber",
                "name": "Wi-Fi Security",
                "description": "Risk of attacks on event Wi-Fi networks",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Secure Wi-Fi configuration",
                    "Network traffic monitoring",
                    "Regular security scans"
                ],
                "response_procedures": [
                    "Shut down compromised networks",
                    "Switch to backup systems",
                    "Notify attendees of security issues"
                ]
            })
        
        # Health and safety threats
        if "health" in threat_categories:
            # Base risk level
            risk_level = "medium"
            
            # Adjust risk level based on inputs
            if attendee_count > 1000:
                risk_level = "medium" if risk_level == "low" else risk_level
            if event_duration.lower().find("day") != -1:
                risk_level = "medium" if risk_level == "low" else risk_level
            
            threats.append({
                "category": "health",
                "name": "Medical Emergencies",
                "description": "Risk of attendee medical emergencies",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Medical staff on site",
                    "First aid stations",
                    "Emergency response protocols"
                ],
                "response_procedures": [
                    "Immediate medical assistance",
                    "Clear area for medical personnel",
                    "Contact emergency services if necessary"
                ]
            })
            
            threats.append({
                "category": "health",
                "name": "Food Safety",
                "description": "Risk of foodborne illness from event catering",
                "risk_level": "medium",
                "monitoring_measures": [
                    "Food safety inspections",
                    "Temperature monitoring",
                    "Vendor certification verification"
                ],
                "response_procedures": [
                    "Remove affected food items",
                    "Provide medical assistance to affected individuals",
                    "Document incidents and notify health authorities if necessary"
                ]
            })
        
        # Weather-related threats for outdoor events
        if "weather" in threat_categories and venue_type.lower() in ["outdoor", "open"]:
            threats.append({
                "category": "weather",
                "name": "Severe Weather",
                "description": "Risk of severe weather affecting the event",
                "risk_level": "medium",
                "monitoring_measures": [
                    "Weather forecast monitoring",
                    "On-site weather stations",
                    "Lightning detection systems"
                ],
                "response_procedures": [
                    "Implement weather emergency plan",
                    "Move attendees to shelter if necessary",
                    "Postpone or cancel outdoor activities if required"
                ]
            })
        
        # Generate monitoring schedule
        monitoring_schedule = []
        
        # Pre-event monitoring
        monitoring_schedule.append({
            "phase": "pre-event",
            "timeframe": "1 week before event",
            "activities": [
                "Conduct initial threat assessment",
                "Test all monitoring systems",
                "Brief security personnel on monitoring protocols"
            ]
        })
        
        # During event monitoring
        monitoring_schedule.append({
            "phase": "during-event",
            "timeframe": "Throughout event duration",
            "activities": [
                "Continuous monitoring of all identified threats",
                "Regular security sweeps",
                "Shift changes for monitoring personnel"
            ]
        })
        
        # Post-event monitoring
        monitoring_schedule.append({
            "phase": "post-event",
            "timeframe": "24 hours after event",
            "activities": [
                "Final security sweep",
                "Data security verification",
                "Incident report compilation"
            ]
        })
        
        # Generate staffing requirements
        staffing_requirements = {
            "security_personnel": max(2, attendee_count // 100),
            "cyber_security_analysts": 2 if "cyber" in threat_categories else 0,
            "medical_staff": max(2, attendee_count // 500) if "health" in threat_categories else 0,
            "monitoring_center_staff": 2 + len(threat_categories)
        }
        
        return {
            "threat_monitoring_plan": {
                "event_type": event_type,
                "venue_type": venue_type,
                "attendee_count": attendee_count,
                "event_duration": event_duration,
                "high_profile": high_profile,
                "threat_categories": threat_categories,
                "identified_threats": threats,
                "monitoring_schedule": monitoring_schedule,
                "staffing_requirements": staffing_requirements,
                "equipment_requirements": [
                    {"name": "CCTV Cameras", "quantity": max(4, attendee_count // 250)},
                    {"name": "Two-way Radios", "quantity": staffing_requirements["security_personnel"] + 2},
                    {"name": "Network Monitoring Systems", "quantity": 1 if "cyber" in threat_categories else 0},
                    {"name": "Weather Monitoring Equipment", "quantity": 1 if "weather" in threat_categories else 0}
                ]
            },
            "plan_id": f"threat-{uuid.uuid4().hex[:8]}",
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class IncidentResponseInput(BaseModel):
    """Input schema for the incident response tool."""
    
    event_type: str = Field(..., description="Type of event")
    venue_type: str = Field(..., description="Type of venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    incident_types: List[str] = Field(..., description="Types of incidents to plan for")
    high_profile: bool = Field(..., description="Whether the event includes high-profile individuals")
    response_team_size: Optional[int] = Field(None, description="Size of the response team")


class IncidentResponseTool(BaseTool):
    """Tool for planning and executing incident response."""
    
    name: str = "incident_response_tool"
    description: str = "Plan and implement incident response procedures for events"
    args_schema: Type[IncidentResponseInput] = IncidentResponseInput
    
    def _run(self, event_type: str, venue_type: str, attendee_count: int,
             incident_types: List[str], high_profile: bool,
             response_team_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the incident response tool.
        
        Args:
            event_type: Type of event
            venue_type: Type of venue
            attendee_count: Expected number of attendees
            incident_types: Types of incidents to plan for
            high_profile: Whether the event includes high-profile individuals
            response_team_size: Size of the response team
            
        Returns:
            Dictionary with incident response plan
        """
        # In a real implementation, this would generate an actual incident response plan
        # For now, we'll return a mock plan
        
        # Set default response team size if not provided
        if response_team_size is None:
            response_team_size = max(3, attendee_count // 500)
        
        # Generate response procedures for each incident type
        procedures = []
        
        # Security breach procedures
        if "security_breach" in incident_types:
            procedures.append({
                "incident_type": "security_breach",
                "name": "Security Breach Response",
                "description": "Procedures for responding to unauthorized access or security breaches",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor breach with limited impact",
                        "examples": ["Unauthorized access to non-sensitive area", "Tailgating at entry point"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant breach with potential for harm",
                        "examples": ["Unauthorized access to restricted area", "Credential theft"]
                    },
                    {
                        "level": "high",
                        "description": "Major breach with immediate risk",
                        "examples": ["Armed intruder", "Coordinated breach of multiple security layers"]
                    }
                ],
                "response_steps": [
                    "Identify and assess the breach",
                    "Secure affected areas",
                    "Notify security team and event management",
                    "Document the incident",
                    "Implement containment measures",
                    "Investigate root cause",
                    "Restore normal operations"
                ],
                "team_roles": [
                    {"role": "Incident Commander", "responsibilities": ["Overall coordination", "Decision making"]},
                    {"role": "Security Lead", "responsibilities": ["Direct security personnel", "Implement containment"]},
                    {"role": "Communications Officer", "responsibilities": ["Internal notifications", "External communications if needed"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 1", "Emergency phone tree", "Secure messaging app"],
                    "external_channels": ["Local law enforcement hotline", "Event management contact"]
                },
                "equipment_needed": [
                    "Two-way radios",
                    "Access control override tools",
                    "Incident documentation forms",
                    "Emergency contact list"
                ]
            })
        
        # Medical emergency procedures
        if "medical_emergency" in incident_types:
            procedures.append({
                "incident_type": "medical_emergency",
                "name": "Medical Emergency Response",
                "description": "Procedures for responding to medical emergencies",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor medical issue requiring basic first aid",
                        "examples": ["Minor cuts or bruises", "Headache", "Mild dehydration"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant medical issue requiring medical attention",
                        "examples": ["Allergic reaction", "Sprain or fracture", "Heat exhaustion"]
                    },
                    {
                        "level": "high",
                        "description": "Life-threatening medical emergency",
                        "examples": ["Heart attack", "Severe allergic reaction", "Unconsciousness"]
                    }
                ],
                "response_steps": [
                    "Assess the situation and ensure scene safety",
                    "Provide immediate first aid",
                    "Notify medical team",
                    "Clear area for medical personnel",
                    "Coordinate with emergency services if needed",
                    "Document the incident",
                    "Follow up with affected individual"
                ],
                "team_roles": [
                    {"role": "Medical Lead", "responsibilities": ["Coordinate medical response", "Assess severity"]},
                    {"role": "First Aid Provider", "responsibilities": ["Deliver immediate care", "Monitor vital signs"]},
                    {"role": "Logistics Support", "responsibilities": ["Clear access routes", "Guide emergency services"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 2", "Medical emergency hotline"],
                    "external_channels": ["Emergency services (911/999/112)", "Local hospital contact"]
                },
                "equipment_needed": [
                    "First aid kits",
                    "AED (Automated External Defibrillator)",
                    "Emergency medical supplies",
                    "Medical incident documentation forms"
                ]
            })
        
        # Fire or evacuation procedures
        if "fire" in incident_types or "evacuation" in incident_types:
            procedures.append({
                "incident_type": "evacuation",
                "name": "Fire and Evacuation Response",
                "description": "Procedures for responding to fires or other incidents requiring evacuation",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Localized incident with limited evacuation needed",
                        "examples": ["Small fire contained to one area", "Localized hazardous material spill"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant incident requiring partial evacuation",
                        "examples": ["Fire affecting multiple areas", "Structural damage to part of venue"]
                    },
                    {
                        "level": "high",
                        "description": "Major incident requiring full evacuation",
                        "examples": ["Large fire", "Major structural damage", "Widespread hazardous material release"]
                    }
                ],
                "response_steps": [
                    "Activate alarm system",
                    "Notify emergency response team",
                    "Begin evacuation procedures",
                    "Guide attendees to emergency exits",
                    "Conduct sweep of affected areas",
                    "Account for all attendees and staff",
                    "Coordinate with emergency services",
                    "Provide updates and instructions to evacuees"
                ],
                "team_roles": [
                    {"role": "Evacuation Coordinator", "responsibilities": ["Overall evacuation management", "Coordination with emergency services"]},
                    {"role": "Zone Marshals", "responsibilities": ["Guide evacuation in assigned zones", "Conduct sweeps"]},
                    {"role": "Assembly Point Coordinator", "responsibilities": ["Manage assembly points", "Account for evacuees"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 3", "Emergency announcement system"],
                    "external_channels": ["Emergency services", "Local authority emergency management"]
                },
                "equipment_needed": [
                    "Evacuation maps and signage",
                    "Emergency lighting",
                    "Megaphones",
                    "High-visibility vests for response team"
                ]
            })
        
        # Data breach procedures
        if "data_breach" in incident_types:
            procedures.append({
                "incident_type": "data_breach",
                "name": "Data Breach Response",
                "description": "Procedures for responding to data breaches or cyber security incidents",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor breach with limited data exposure",
                        "examples": ["Exposure of non-sensitive data", "Brief system outage"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant breach with potential for harm",
                        "examples": ["Exposure of personal data", "Unauthorized access to systems"]
                    },
                    {
                        "level": "high",
                        "description": "Major breach with serious consequences",
                        "examples": ["Exposure of financial data", "Widespread system compromise"]
                    }
                ],
                "response_steps": [
                    "Identify and assess the breach",
                    "Contain the breach",
                    "Notify IT security team",
                    "Preserve evidence",
                    "Investigate the breach",
                    "Notify affected individuals if required",
                    "Implement recovery procedures",
                    "Document lessons learned"
                ],
                "team_roles": [
                    {"role": "Cyber Incident Lead", "responsibilities": ["Overall coordination", "Technical assessment"]},
                    {"role": "IT Security Specialist", "responsibilities": ["Containment actions", "Technical investigation"]},
                    {"role": "Legal Advisor", "responsibilities": ["Compliance requirements", "Notification obligations"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Secure messaging platform", "Incident response hotline"],
                    "external_channels": ["Data protection authority", "Cyber security incident reporting"]
                },
                "equipment_needed": [
                    "Forensic analysis tools",
                    "Secure communication devices",
                    "Incident documentation templates",
                    "Data breach notification templates"
                ]
            })
        
        # Generate response team structure
        response_team = []
        
        # Core team members
        response_team.append({
            "role": "Incident Response Manager",
            "responsibilities": ["Overall coordination of incident response", "Decision making", "External communications"],
            "required_skills": ["Crisis management", "Leadership", "Communication"],
            "count": 1
        })
        
        response_team.append({
            "role": "Communications Coordinator",
            "responsibilities": ["Internal communications", "Updates to stakeholders", "Media liaison if needed"],
            "required_skills": ["Crisis communication", "Stakeholder management"],
            "count": 1
        })
        
        # Specialized team members based on incident types
        if "security_breach" in incident_types:
            response_team.append({
                "role": "Security Response Specialist",
                "responsibilities": ["Security breach response", "Physical security measures", "Coordination with security personnel"],
                "required_skills": ["Security management", "Threat assessment"],
                "count": max(1, response_team_size // 4)
            })
        
        if "medical_emergency" in incident_types:
            response_team.append({
                "role": "Medical Response Coordinator",
                "responsibilities": ["Medical emergency response", "Coordination with medical staff", "First aid provision"],
                "required_skills": ["First aid certification", "Emergency medical knowledge"],
                "count": max(1, response_team_size // 4)
            })
        
        if "fire" in incident_types or "evacuation" in incident_types:
            response_team.append({
                "role": "Evacuation Coordinator",
                "responsibilities": ["Evacuation procedures", "Assembly point management", "Coordination with emergency services"],
                "required_skills": ["Evacuation planning", "Emergency management"],
                "count": max(1, response_team_size // 4)
            })
        
        if "data_breach" in incident_types:
            response_team.append({
                "role": "Cyber Incident Responder",
                "responsibilities": ["Data breach response", "System security measures", "Digital evidence preservation"],
                "required_skills": ["IT security", "Data protection", "Forensic analysis"],
                "count": max(1, response_team_size // 4)
            })
        
        # Create an IncidentResponsePlan object
        plan = IncidentResponsePlan(
            name=f"Incident Response Plan for {event_type}",
            description=f"Comprehensive incident response plan for {event_type} at {venue_type} venue",
            incident_types_covered=incident_types,
            response_team=[{"role": member["role"], "responsibilities": member["responsibilities"]} for member in response_team],
            response_procedures=[{
                "incident_type": proc["incident_type"],
                "name": proc["name"],
                "description": proc["description"],
                "response_steps": proc["response_steps"]
            } for proc in procedures],
            communication_protocols={
                "emergency_contacts": [
                    {"name": "Event Manager", "contact": "Internal extension 100"},
                    {"name": "Security Lead", "contact": "Internal extension 101"},
                    {"name": "Medical Team", "contact": "Internal extension 102"},
                    {"name": "Local Emergency Services", "contact": "911/999/112"}
                ],
                "notification_procedures": [
                    "Initial notification to Incident Response Manager",
                    "Manager activates appropriate response team",
                    "Team communications via designated radio channel",
                    "Regular status updates to Event Manager",
                    "External communications via Communications Coordinator only"
                ]
            },
            status="draft"
        )
        
        # Generate an incident response plan ID
        plan_id = f"ir-{uuid.uuid4().hex[:8]}"
        
        return {
            "incident_response_plan": plan.dict(),
            "plan_id": plan_id,
            "team_size": sum(member["count"] for member in response_team),
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class SecurityReportingInput(BaseModel):
    """Input schema for the security reporting tool."""
    
    event_id: str = Field(..., description="ID of the event")
    report_type: str = Field(..., description="Type of report to generate")
    time_period: str = Field(..., description="Time period for the report")
    include_incidents: bool = Field(..., description="Whether to include security incidents in the report")
    include_compliance: bool = Field(..., description="Whether to include compliance status in the report")


class SecurityReportingTool(BaseTool):
    """Tool for generating security and compliance reports."""
    
    name: str = "security_reporting_tool"
    description: str = "Generate security and compliance reports for events"
    args_schema: Type[SecurityReportingInput] = SecurityReportingInput
    
    def _run(self, event_id: str, report_type: str, time_period: str,
             include_incidents: bool, include_compliance: bool) -> Dict[str, Any]:
        """
        Run the security reporting tool.
        
        Args:
            event_id: ID of the event
            report_type: Type of report to generate
            time_period: Time period for the report
            include_incidents: Whether to include security incidents in the report
            include_compliance: Whether to include compliance status in the report
            
        Returns:
            Dictionary with security report
        """
        # In a real implementation, this would generate an actual report based on data
        # For now, we'll return a mock report
        
        # Generate mock incidents if requested
        incidents = []
        if include_incidents:
            incidents = [
                SecurityIncident(
                    incident_type="unauthorized_access",
                    description="Unauthorized individual attempted to access VIP area",
                    severity="medium",
                    date_time=datetime.now() - timedelta(days=2, hours=3),
                    location="VIP entrance",
                    affected_assets=["VIP area"],
                    resolution_status="resolved",
                    resolution_details="Individual escorted from area, credentials verified"
                ).dict(),
                SecurityIncident(
                    incident_type="suspicious_activity",
                    description="Suspicious package left unattended",
                    severity="high",
                    date_time=datetime.now() - timedelta(days=1, hours=5),
                    location="Main hall entrance",
                    affected_assets=["Entrance area"],
                    resolution_status="resolved",
                    resolution_details="Package inspected by security, contained personal items"
                ).dict(),
                SecurityIncident(
                    incident_type="system_outage",
                    description="Brief outage of access control system",
                    severity="medium",
                    date_time=datetime.now() - timedelta(hours=12),
                    location="All access points",
                    affected_assets=["Access control system"],
                    resolution_status="resolved",
                    resolution_details="System restarted, backup procedures implemented during outage"
                ).dict()
            ]
        
        # Generate mock compliance status if requested
        compliance_status = {}
        if include_compliance:
            compliance_status = {
                "overall_status": "compliant",
                "requirements_met": 42,
                "requirements_pending": 3,
                "requirements_not_met": 0,
                "compliance_percentage": 93.3,
                "key_areas": [
                    {
                        "area": "Data Protection",
                        "status": "compliant",
                        "details": "All data protection measures implemented"
                    },
                    {
                        "area": "Physical Security",
                        "status": "compliant",
                        "details": "All physical security protocols in place"
                    },
                    {
                        "area": "Staff Training",
                        "status": "partially_compliant",
                        "details": "3 staff members pending security training completion"
                    }
                ]
            }
        
        # Create a ComplianceReport object
        report = ComplianceReport(
            report_type=report_type,
            event_id=event_id,
            time_period=time_period,
            generation_date=datetime.now(),
            summary=f"Security and compliance report for event {event_id} covering {time_period}",
            key_findings=[
                "Overall security posture is strong",
                "Minor incidents handled according to procedures",
                "Compliance requirements largely met with few pending items"
            ],
            recommendations=[
                "Complete remaining staff training",
                "Conduct follow-up audit on access control procedures",
                "Update incident response documentation based on recent experiences"
            ]
        )
        
        # Generate a report ID
        report_id = f"report-{uuid.uuid4().hex[:8]}"
        
        return {
            "report": report.dict(),
            "report_id": report_id,
            "incidents": incidents if include_incidents else [],
            "compliance_status": compliance_status if include_compliance else {},
            "generation_details": {
                "generated_at": datetime.now().isoformat(),
                "generated_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)

class ThreatMonitoringInput(BaseModel):
    """Input schema for the threat monitoring tool."""
    
    event_type: str = Field(..., description="Type of event")
    venue_type: str = Field(..., description="Type of venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    event_duration: str = Field(..., description="Duration of the event (e.g., '3 days', '8 hours')")
    high_profile: bool = Field(..., description="Whether the event includes high-profile individuals")
    threat_categories: List[str] = Field(..., description="Categories of threats to monitor")


class ThreatMonitoringTool(BaseTool):
    """Tool for monitoring security threats."""
    
    name: str = "threat_monitoring_tool"
    description: str = "Monitor and assess security threats for events"
    args_schema: Type[ThreatMonitoringInput] = ThreatMonitoringInput
    
    def _run(self, event_type: str, venue_type: str, attendee_count: int,
             event_duration: str, high_profile: bool, threat_categories: List[str]) -> Dict[str, Any]:
        """
        Run the threat monitoring tool.
        
        Args:
            event_type: Type of event
            venue_type: Type of venue
            attendee_count: Expected number of attendees
            event_duration: Duration of the event
            high_profile: Whether the event includes high-profile individuals
            threat_categories: Categories of threats to monitor
            
        Returns:
            Dictionary with threat monitoring plan
        """
        # In a real implementation, this would generate an actual threat monitoring plan
        # For now, we'll return a mock plan
        
        # Generate threat assessment based on inputs
        threats = []
        
        # Physical security threats
        if "physical" in threat_categories:
            # Base risk level
            risk_level = "low"
            
            # Adjust risk level based on inputs
            if attendee_count > 1000:
                risk_level = "medium"
            if attendee_count > 5000:
                risk_level = "high"
            if high_profile:
                risk_level = "high" if risk_level != "critical" else risk_level
            if venue_type.lower() in ["outdoor", "public", "open"]:
                risk_level = "medium" if risk_level == "low" else risk_level
            
            threats.append({
                "category": "physical",
                "name": "Unauthorized Access",
                "description": "Risk of unauthorized individuals accessing restricted areas",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Access control systems at all entry points",
                    "Security personnel stationed at key locations",
                    "Regular perimeter checks"
                ],
                "response_procedures": [
                    "Immediate notification of security team",
                    "Escort unauthorized individuals out of restricted areas",
                    "Document incidents and review access control measures"
                ]
            })
            
            threats.append({
                "category": "physical",
                "name": "Crowd Management Incidents",
                "description": "Risk of overcrowding, stampedes, or other crowd-related incidents",
                "risk_level": "high" if attendee_count > 1000 else "medium",
                "monitoring_measures": [
                    "Real-time crowd density monitoring",
                    "CCTV surveillance of high-traffic areas",
                    "Regular headcounts in different zones"
                ],
                "response_procedures": [
                    "Implement crowd control measures",
                    "Open additional exits if necessary",
                    "Deploy security personnel to manage flow"
                ]
            })
        
        # Cyber security threats
        if "cyber" in threat_categories:
            # Base risk level
            risk_level = "medium"
            
            # Adjust risk level based on inputs
            if high_profile:
                risk_level = "high"
            if event_type.lower() in ["tech", "technology", "digital"]:
                risk_level = "high"
            
            threats.append({
                "category": "cyber",
                "name": "Data Breach",
                "description": "Risk of unauthorized access to attendee or event data",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Real-time monitoring of network traffic",
                    "Intrusion detection systems",
                    "Regular security scans"
                ],
                "response_procedures": [
                    "Isolate affected systems",
                    "Implement incident response plan",
                    "Notify affected individuals if necessary"
                ]
            })
            
            threats.append({
                "category": "cyber",
                "name": "Wi-Fi Security",
                "description": "Risk of attacks on event Wi-Fi networks",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Secure Wi-Fi configuration",
                    "Network traffic monitoring",
                    "Regular security scans"
                ],
                "response_procedures": [
                    "Shut down compromised networks",
                    "Switch to backup systems",
                    "Notify attendees of security issues"
                ]
            })
        
        # Health and safety threats
        if "health" in threat_categories:
            # Base risk level
            risk_level = "medium"
            
            # Adjust risk level based on inputs
            if attendee_count > 1000:
                risk_level = "medium" if risk_level == "low" else risk_level
            if event_duration.lower().find("day") != -1:
                risk_level = "medium" if risk_level == "low" else risk_level
            
            threats.append({
                "category": "health",
                "name": "Medical Emergencies",
                "description": "Risk of attendee medical emergencies",
                "risk_level": risk_level,
                "monitoring_measures": [
                    "Medical staff on site",
                    "First aid stations",
                    "Emergency response protocols"
                ],
                "response_procedures": [
                    "Immediate medical assistance",
                    "Clear area for medical personnel",
                    "Contact emergency services if necessary"
                ]
            })
            
            threats.append({
                "category": "health",
                "name": "Food Safety",
                "description": "Risk of foodborne illness from event catering",
                "risk_level": "medium",
                "monitoring_measures": [
                    "Food safety inspections",
                    "Temperature monitoring",
                    "Vendor certification verification"
                ],
                "response_procedures": [
                    "Remove affected food items",
                    "Provide medical assistance to affected individuals",
                    "Document incidents and notify health authorities if necessary"
                ]
            })
        
        # Weather-related threats for outdoor events
        if "weather" in threat_categories and venue_type.lower() in ["outdoor", "open"]:
            threats.append({
                "category": "weather",
                "name": "Severe Weather",
                "description": "Risk of severe weather affecting the event",
                "risk_level": "medium",
                "monitoring_measures": [
                    "Weather forecast monitoring",
                    "On-site weather stations",
                    "Lightning detection systems"
                ],
                "response_procedures": [
                    "Implement weather emergency plan",
                    "Move attendees to shelter if necessary",
                    "Postpone or cancel outdoor activities if required"
                ]
            })
        
        # Generate monitoring schedule
        monitoring_schedule = []
        
        # Pre-event monitoring
        monitoring_schedule.append({
            "phase": "pre-event",
            "timeframe": "1 week before event",
            "activities": [
                "Conduct initial threat assessment",
                "Test all monitoring systems",
                "Brief security personnel on monitoring protocols"
            ]
        })
        
        # During event monitoring
        monitoring_schedule.append({
            "phase": "during-event",
            "timeframe": "Throughout event duration",
            "activities": [
                "Continuous monitoring of all identified threats",
                "Regular security sweeps",
                "Shift changes for monitoring personnel"
            ]
        })
        
        # Post-event monitoring
        monitoring_schedule.append({
            "phase": "post-event",
            "timeframe": "24 hours after event",
            "activities": [
                "Final security sweep",
                "Data security verification",
                "Incident report compilation"
            ]
        })
        
        # Generate staffing requirements
        staffing_requirements = {
            "security_personnel": max(2, attendee_count // 100),
            "cyber_security_analysts": 2 if "cyber" in threat_categories else 0,
            "medical_staff": max(2, attendee_count // 500) if "health" in threat_categories else 0,
            "monitoring_center_staff": 2 + len(threat_categories)
        }
        
        return {
            "threat_monitoring_plan": {
                "event_type": event_type,
                "venue_type": venue_type,
                "attendee_count": attendee_count,
                "event_duration": event_duration,
                "high_profile": high_profile,
                "threat_categories": threat_categories,
                "identified_threats": threats,
                "monitoring_schedule": monitoring_schedule,
                "staffing_requirements": staffing_requirements,
                "equipment_requirements": [
                    {"name": "CCTV Cameras", "quantity": max(4, attendee_count // 250)},
                    {"name": "Two-way Radios", "quantity": staffing_requirements["security_personnel"] + 2},
                    {"name": "Network Monitoring Systems", "quantity": 1 if "cyber" in threat_categories else 0},
                    {"name": "Weather Monitoring Equipment", "quantity": 1 if "weather" in threat_categories else 0}
                ]
            },
            "plan_id": f"threat-{uuid.uuid4().hex[:8]}",
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class IncidentResponseInput(BaseModel):
    """Input schema for the incident response tool."""
    
    event_type: str = Field(..., description="Type of event")
    venue_type: str = Field(..., description="Type of venue")
    attendee_count: int = Field(..., description="Expected number of attendees")
    incident_types: List[str] = Field(..., description="Types of incidents to plan for")
    high_profile: bool = Field(..., description="Whether the event includes high-profile individuals")
    response_team_size: Optional[int] = Field(None, description="Size of the response team")


class IncidentResponseTool(BaseTool):
    """Tool for planning and executing incident response."""
    
    name: str = "incident_response_tool"
    description: str = "Plan and implement incident response procedures for events"
    args_schema: Type[IncidentResponseInput] = IncidentResponseInput
    
    def _run(self, event_type: str, venue_type: str, attendee_count: int,
             incident_types: List[str], high_profile: bool,
             response_team_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Run the incident response tool.
        
        Args:
            event_type: Type of event
            venue_type: Type of venue
            attendee_count: Expected number of attendees
            incident_types: Types of incidents to plan for
            high_profile: Whether the event includes high-profile individuals
            response_team_size: Size of the response team
            
        Returns:
            Dictionary with incident response plan
        """
        # In a real implementation, this would generate an actual incident response plan
        # For now, we'll return a mock plan
        
        # Set default response team size if not provided
        if response_team_size is None:
            response_team_size = max(3, attendee_count // 500)
        
        # Generate response procedures for each incident type
        procedures = []
        
        # Security breach procedures
        if "security_breach" in incident_types:
            procedures.append({
                "incident_type": "security_breach",
                "name": "Security Breach Response",
                "description": "Procedures for responding to unauthorized access or security breaches",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor breach with limited impact",
                        "examples": ["Unauthorized access to non-sensitive area", "Tailgating at entry point"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant breach with potential for harm",
                        "examples": ["Unauthorized access to restricted area", "Credential theft"]
                    },
                    {
                        "level": "high",
                        "description": "Major breach with immediate risk",
                        "examples": ["Armed intruder", "Coordinated breach of multiple security layers"]
                    }
                ],
                "response_steps": [
                    "Identify and assess the breach",
                    "Secure affected areas",
                    "Notify security team and event management",
                    "Document the incident",
                    "Implement containment measures",
                    "Investigate root cause",
                    "Restore normal operations"
                ],
                "team_roles": [
                    {"role": "Incident Commander", "responsibilities": ["Overall coordination", "Decision making"]},
                    {"role": "Security Lead", "responsibilities": ["Direct security personnel", "Implement containment"]},
                    {"role": "Communications Officer", "responsibilities": ["Internal notifications", "External communications if needed"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 1", "Emergency phone tree", "Secure messaging app"],
                    "external_channels": ["Local law enforcement hotline", "Event management contact"]
                },
                "equipment_needed": [
                    "Two-way radios",
                    "Access control override tools",
                    "Incident documentation forms",
                    "Emergency contact list"
                ]
            })
        
        # Medical emergency procedures
        if "medical_emergency" in incident_types:
            procedures.append({
                "incident_type": "medical_emergency",
                "name": "Medical Emergency Response",
                "description": "Procedures for responding to medical emergencies",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor medical issue requiring basic first aid",
                        "examples": ["Minor cuts or bruises", "Headache", "Mild dehydration"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant medical issue requiring medical attention",
                        "examples": ["Allergic reaction", "Sprain or fracture", "Heat exhaustion"]
                    },
                    {
                        "level": "high",
                        "description": "Life-threatening medical emergency",
                        "examples": ["Heart attack", "Severe allergic reaction", "Unconsciousness"]
                    }
                ],
                "response_steps": [
                    "Assess the situation and ensure scene safety",
                    "Provide immediate first aid",
                    "Notify medical team",
                    "Clear area for medical personnel",
                    "Coordinate with emergency services if needed",
                    "Document the incident",
                    "Follow up with affected individual"
                ],
                "team_roles": [
                    {"role": "Medical Lead", "responsibilities": ["Coordinate medical response", "Assess severity"]},
                    {"role": "First Aid Provider", "responsibilities": ["Deliver immediate care", "Monitor vital signs"]},
                    {"role": "Logistics Support", "responsibilities": ["Clear access routes", "Guide emergency services"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 2", "Medical emergency hotline"],
                    "external_channels": ["Emergency services (911/999/112)", "Local hospital contact"]
                },
                "equipment_needed": [
                    "First aid kits",
                    "AED (Automated External Defibrillator)",
                    "Emergency medical supplies",
                    "Medical incident documentation forms"
                ]
            })
        
        # Fire or evacuation procedures
        if "fire" in incident_types or "evacuation" in incident_types:
            procedures.append({
                "incident_type": "evacuation",
                "name": "Fire and Evacuation Response",
                "description": "Procedures for responding to fires or other incidents requiring evacuation",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Localized incident with limited evacuation needed",
                        "examples": ["Small fire contained to one area", "Localized hazardous material spill"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant incident requiring partial evacuation",
                        "examples": ["Fire affecting multiple areas", "Structural damage to part of venue"]
                    },
                    {
                        "level": "high",
                        "description": "Major incident requiring full evacuation",
                        "examples": ["Large fire", "Major structural damage", "Widespread hazardous material release"]
                    }
                ],
                "response_steps": [
                    "Activate alarm system",
                    "Notify emergency response team",
                    "Begin evacuation procedures",
                    "Guide attendees to emergency exits",
                    "Conduct sweep of affected areas",
                    "Account for all attendees and staff",
                    "Coordinate with emergency services",
                    "Provide updates and instructions to evacuees"
                ],
                "team_roles": [
                    {"role": "Evacuation Coordinator", "responsibilities": ["Overall evacuation management", "Coordination with emergency services"]},
                    {"role": "Zone Marshals", "responsibilities": ["Guide evacuation in assigned zones", "Conduct sweeps"]},
                    {"role": "Assembly Point Coordinator", "responsibilities": ["Manage assembly points", "Account for evacuees"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Radio channel 3", "Emergency announcement system"],
                    "external_channels": ["Emergency services", "Local authority emergency management"]
                },
                "equipment_needed": [
                    "Evacuation maps and signage",
                    "Emergency lighting",
                    "Megaphones",
                    "High-visibility vests for response team"
                ]
            })
        
        # Data breach procedures
        if "data_breach" in incident_types:
            procedures.append({
                "incident_type": "data_breach",
                "name": "Data Breach Response",
                "description": "Procedures for responding to data breaches or cyber security incidents",
                "severity_levels": [
                    {
                        "level": "low",
                        "description": "Minor breach with limited data exposure",
                        "examples": ["Exposure of non-sensitive data", "Brief system outage"]
                    },
                    {
                        "level": "medium",
                        "description": "Significant breach with potential for harm",
                        "examples": ["Exposure of personal data", "Unauthorized access to systems"]
                    },
                    {
                        "level": "high",
                        "description": "Major breach with serious consequences",
                        "examples": ["Exposure of financial data", "Widespread system compromise"]
                    }
                ],
                "response_steps": [
                    "Identify and assess the breach",
                    "Contain the breach",
                    "Notify IT security team",
                    "Preserve evidence",
                    "Investigate the breach",
                    "Notify affected individuals if required",
                    "Implement recovery procedures",
                    "Document lessons learned"
                ],
                "team_roles": [
                    {"role": "Cyber Incident Lead", "responsibilities": ["Overall coordination", "Technical assessment"]},
                    {"role": "IT Security Specialist", "responsibilities": ["Containment actions", "Technical investigation"]},
                    {"role": "Legal Advisor", "responsibilities": ["Compliance requirements", "Notification obligations"]}
                ],
                "communication_protocol": {
                    "internal_channels": ["Secure messaging platform", "Incident response hotline"],
                    "external_channels": ["Data protection authority", "Cyber security incident reporting"]
                },
                "equipment_needed": [
                    "Forensic analysis tools",
                    "Secure communication devices",
                    "Incident documentation templates",
                    "Data breach notification templates"
                ]
            })
        
        # Generate response team structure
        response_team = []
        
        # Core team members
        response_team.append({
            "role": "Incident Response Manager",
            "responsibilities": ["Overall coordination of incident response", "Decision making", "External communications"],
            "required_skills": ["Crisis management", "Leadership", "Communication"],
            "count": 1
        })
        
        response_team.append({
            "role": "Communications Coordinator",
            "responsibilities": ["Internal communications", "Updates to stakeholders", "Media liaison if needed"],
            "required_skills": ["Crisis communication", "Stakeholder management"],
            "count": 1
        })
        
        # Specialized team members based on incident types
        if "security_breach" in incident_types:
            response_team.append({
                "role": "Security Response Specialist",
                "responsibilities": ["Security breach response", "Physical security measures", "Coordination with security personnel"],
                "required_skills": ["Security management", "Threat assessment"],
                "count": max(1, response_team_size // 4)
            })
        
        if "medical_emergency" in incident_types:
            response_team.append({
                "role": "Medical Response Coordinator",
                "responsibilities": ["Medical emergency response", "Coordination with medical staff", "First aid provision"],
                "required_skills": ["First aid certification", "Emergency medical knowledge"],
                "count": max(1, response_team_size // 4)
            })
        
        if "fire" in incident_types or "evacuation" in incident_types:
            response_team.append({
                "role": "Evacuation Coordinator",
                "responsibilities": ["Evacuation procedures", "Assembly point management", "Coordination with emergency services"],
                "required_skills": ["Evacuation planning", "Emergency management"],
                "count": max(1, response_team_size // 4)
            })
        
        if "data_breach" in incident_types:
            response_team.append({
                "role": "Cyber Incident Responder",
                "responsibilities": ["Data breach response", "System security measures", "Digital evidence preservation"],
                "required_skills": ["IT security", "Data protection", "Forensic analysis"],
                "count": max(1, response_team_size // 4)
            })
        
        # Create an IncidentResponsePlan object
        plan = IncidentResponsePlan(
            name=f"Incident Response Plan for {event_type}",
            description=f"Comprehensive incident response plan for {event_type} at {venue_type} venue",
            incident_types_covered=incident_types,
            response_team=[{"role": member["role"], "responsibilities": member["responsibilities"]} for member in response_team],
            response_procedures=[{
                "incident_type": proc["incident_type"],
                "name": proc["name"],
                "description": proc["description"],
                "response_steps": proc["response_steps"]
            } for proc in procedures],
            communication_protocols={
                "emergency_contacts": [
                    {"name": "Event Manager", "contact": "Internal extension 100"},
                    {"name": "Security Lead", "contact": "Internal extension 101"},
                    {"name": "Medical Team", "contact": "Internal extension 102"},
                    {"name": "Local Emergency Services", "contact": "911/999/112"}
                ],
                "notification_procedures": [
                    "Initial notification to Incident Response Manager",
                    "Manager activates appropriate response team",
                    "Team communications via designated radio channel",
                    "Regular status updates to Event Manager",
                    "External communications via Communications Coordinator only"
                ]
            },
            status="draft"
        )
        
        # Generate an incident response plan ID
        plan_id = f"ir-{uuid.uuid4().hex[:8]}"
        
        return {
            "incident_response_plan": plan.dict(),
            "plan_id": plan_id,
            "team_size": sum(member["count"] for member in response_team),
            "creation_details": {
                "created_at": datetime.now().isoformat(),
                "created_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)


class SecurityReportingInput(BaseModel):
    """Input schema for the security reporting tool."""
    
    event_id: str = Field(..., description="ID of the event")
    report_type: str = Field(..., description="Type of report to generate")
    time_period: str = Field(..., description="Time period for the report")
    include_incidents: bool = Field(..., description="Whether to include security incidents in the report")
    include_compliance: bool = Field(..., description="Whether to include compliance status in the report")


class SecurityReportingTool(BaseTool):
    """Tool for generating security and compliance reports."""
    
    name: str = "security_reporting_tool"
    description: str = "Generate security and compliance reports for events"
    args_schema: Type[SecurityReportingInput] = SecurityReportingInput
    
    def _run(self, event_id: str, report_type: str, time_period: str,
             include_incidents: bool, include_compliance: bool) -> Dict[str, Any]:
        """
        Run the security reporting tool.
        
        Args:
            event_id: ID of the event
            report_type: Type of report to generate
            time_period: Time period for the report
            include_incidents: Whether to include security incidents in the report
            include_compliance: Whether to include compliance status in the report
            
        Returns:
            Dictionary with security report
        """
        # In a real implementation, this would generate an actual report based on data
        # For now, we'll return a mock report
        
        # Generate mock incidents if requested
        incidents = []
        if include_incidents:
            incidents = [
                SecurityIncident(
                    incident_type="unauthorized_access",
                    description="Unauthorized individual attempted to access VIP area",
                    severity="medium",
                    date_time=datetime.now() - timedelta(days=2, hours=3),
                    location="VIP entrance",
                    affected_assets=["VIP area"],
                    resolution_status="resolved",
                    resolution_details="Individual escorted from area, credentials verified"
                ).dict(),
                SecurityIncident(
                    incident_type="suspicious_activity",
                    description="Suspicious package left unattended",
                    severity="high",
                    date_time=datetime.now() - timedelta(days=1, hours=5),
                    location="Main hall entrance",
                    affected_assets=["Entrance area"],
                    resolution_status="resolved",
                    resolution_details="Package inspected by security, contained personal items"
                ).dict(),
                SecurityIncident(
                    incident_type="system_outage",
                    description="Brief outage of access control system",
                    severity="medium",
                    date_time=datetime.now() - timedelta(hours=12),
                    location="All access points",
                    affected_assets=["Access control system"],
                    resolution_status="resolved",
                    resolution_details="System restarted, backup procedures implemented during outage"
                ).dict()
            ]
        
        # Generate mock compliance status if requested
        compliance_status = {}
        if include_compliance:
            compliance_status = {
                "overall_status": "compliant",
                "requirements_met": 42,
                "requirements_pending": 3,
                "requirements_not_met": 0,
                "compliance_percentage": 93.3,
                "key_areas": [
                    {
                        "area": "Data Protection",
                        "status": "compliant",
                        "details": "All data protection measures implemented"
                    },
                    {
                        "area": "Physical Security",
                        "status": "compliant",
                        "details": "All physical security protocols in place"
                    },
                    {
                        "area": "Staff Training",
                        "status": "partially_compliant",
                        "details": "3 staff members pending security training completion"
                    }
                ]
            }
        
        # Create a ComplianceReport object
        report = ComplianceReport(
            report_type=report_type,
            event_id=event_id,
            time_period=time_period,
            generation_date=datetime.now(),
            summary=f"Security and compliance report for event {event_id} covering {time_period}",
            key_findings=[
                "Overall security posture is strong",
                "Minor incidents handled according to procedures",
                "Compliance requirements largely met with few pending items"
            ],
            recommendations=[
                "Complete remaining staff training",
                "Conduct follow-up audit on access control procedures",
                "Update incident response documentation based on recent experiences"
            ]
        )
        
        # Generate a report ID
        report_id = f"report-{uuid.uuid4().hex[:8]}"
        
        return {
            "report": report.dict(),
            "report_id": report_id,
            "incidents": incidents if include_incidents else [],
            "compliance_status": compliance_status if include_compliance else {},
            "generation_details": {
                "generated_at": datetime.now().isoformat(),
                "generated_by": "Compliance & Security Agent",
                "version": "1.0"
            }
        }
    
    async def _arun(self, **kwargs) -> Dict[str, Any]:
        """Async implementation of the tool."""
        return self._run(**kwargs)
