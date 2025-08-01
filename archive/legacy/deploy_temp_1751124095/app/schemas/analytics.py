from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DataSource(BaseModel):
    """Data source model."""
    
    name: str = Field(..., description="Name of the data source")
    type: str = Field(..., description="Type of data source (registration, survey, tracking, etc.)")
    description: Optional[str] = Field(None, description="Description of the data source")
    connection_details: Optional[Dict[str, Any]] = Field(None, description="Connection details for the data source")


class Metric(BaseModel):
    """Metric model."""
    
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of what the metric measures")
    value: float = Field(..., description="Current value of the metric")
    target: Optional[float] = Field(None, description="Target value for the metric")
    unit: str = Field("count", description="Unit of measurement")
    data_source: str = Field(..., description="Source of the metric data")
    timestamp: datetime = Field(..., description="When the metric was last updated")


class Segment(BaseModel):
    """Attendee segment model."""
    
    name: str = Field(..., description="Name of the segment")
    criteria: Dict[str, Any] = Field(..., description="Criteria defining the segment")
    size: int = Field(..., description="Number of attendees in the segment")
    percentage: float = Field(..., description="Percentage of total attendees")


class Survey(BaseModel):
    """Survey model."""
    
    title: str = Field(..., description="Survey title")
    description: str = Field(..., description="Survey description")
    questions: List[Dict[str, Any]] = Field(..., description="Survey questions")
    target_audience: Optional[str] = Field(None, description="Target audience for the survey")
    distribution_channel: str = Field(..., description="How the survey will be distributed")
    status: str = Field("draft", description="Survey status (draft, active, closed)")


class SurveyResponse(BaseModel):
    """Survey response model."""
    
    survey_id: str = Field(..., description="ID of the survey")
    respondent_id: str = Field(..., description="ID of the respondent")
    responses: Dict[str, Any] = Field(..., description="Survey responses")
    submission_time: datetime = Field(..., description="When the response was submitted")
    completion_rate: float = Field(..., description="Percentage of questions answered")


class AnalyticsReport(BaseModel):
    """Analytics report model."""
    
    title: str = Field(..., description="Report title")
    description: str = Field(..., description="Report description")
    metrics: List[Metric] = Field(..., description="Metrics included in the report")
    segments: Optional[List[Segment]] = Field(None, description="Attendee segments analyzed")
    insights: List[str] = Field(..., description="Key insights from the analysis")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations based on the analysis")
    generated_at: datetime = Field(..., description="When the report was generated")


class ROIAnalysis(BaseModel):
    """ROI analysis model."""
    
    total_cost: float = Field(..., description="Total cost of the event")
    total_revenue: float = Field(..., description="Total revenue generated")
    roi_percentage: float = Field(..., description="ROI as a percentage")
    cost_breakdown: Dict[str, float] = Field(..., description="Breakdown of costs by category")
    revenue_breakdown: Dict[str, float] = Field(..., description="Breakdown of revenue by source")
    non_financial_benefits: Optional[List[str]] = Field(None, description="Non-financial benefits")


class AttendeeAnalytics(BaseModel):
    """Attendee analytics model."""
    
    total_attendees: int = Field(..., description="Total number of attendees")
    registration_rate: float = Field(..., description="Percentage of invitees who registered")
    attendance_rate: float = Field(..., description="Percentage of registrants who attended")
    demographics: Dict[str, Dict[str, float]] = Field(..., description="Demographic breakdown of attendees")
    engagement_metrics: Dict[str, float] = Field(..., description="Engagement metrics for attendees")
    acquisition_channels: Dict[str, float] = Field(..., description="Breakdown of how attendees were acquired")


class EngagementMetrics(BaseModel):
    """Engagement metrics model."""
    
    session_attendance: Dict[str, float] = Field(..., description="Attendance rates for different sessions")
    content_engagement: Dict[str, float] = Field(..., description="Engagement rates with different content")
    interaction_rates: Dict[str, float] = Field(..., description="Rates of different types of interactions")
    feedback_scores: Dict[str, float] = Field(..., description="Feedback scores for different aspects")
    net_promoter_score: float = Field(..., description="Net Promoter Score")


class PerformanceInsight(BaseModel):
    """Performance insight model."""
    
    title: str = Field(..., description="Title of the insight")
    description: str = Field(..., description="Detailed description of the insight")
    related_metrics: List[str] = Field(..., description="Metrics related to this insight")
    impact_level: str = Field(..., description="Impact level (high, medium, low)")
    action_items: Optional[List[str]] = Field(None, description="Suggested actions based on the insight")
    generated_at: datetime = Field(..., description="When the insight was generated")
