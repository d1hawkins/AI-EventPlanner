from typing import Dict, List, Any, TypedDict, Literal, Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.utils.llm_factory import get_llm
from app.tools.analytics_tools import (
    DataCollectionTool,
    MetricDefinitionTool,
    SegmentationTool,
    SurveyCreationTool,
    ReportGenerationTool,
    ROICalculationTool,
    AttendeeAnalyticsTool,
    InsightGenerationTool
)
from app.tools.analytics_search_tool import AnalyticsSearchTool
from app.schemas.analytics import (
    DataSource,
    Metric,
    Segment,
    Survey,
    AnalyticsReport,
    ROIAnalysis,
    AttendeeAnalytics,
    PerformanceInsight
)


# Define the state schema for the Analytics Agent
class AnalyticsStateDict(TypedDict):
    """State for the analytics agent."""
    
    messages: List[Dict[str, str]]
    event_details: Dict[str, Any]
    data_sources: List[Dict[str, Any]]
    metrics: List[Dict[str, Any]]
    segments: List[Dict[str, Any]]
    surveys: List[Dict[str, Any]]
    reports: List[Dict[str, Any]]
    roi_analysis: Optional[Dict[str, Any]]
    attendee_analytics: Optional[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    current_phase: str
    next_steps: List[str]


# Define the system prompt for the Analytics Agent
ANALYTICS_SYSTEM_PROMPT = """You are the Analytics Agent for an event planning system. Your role is to:

1. Collect and analyze data about events
2. Define and track key performance metrics
3. Create and analyze attendee segments
4. Design and manage surveys
5. Generate analytics reports
6. Calculate and analyze ROI
7. Generate insights and recommendations

Your primary responsibilities include:

Data Collection:
- Configure data sources
- Ensure data quality
- Integrate data from multiple sources

Metric Tracking:
- Define key performance indicators
- Track metrics over time
- Compare metrics to benchmarks

Segmentation:
- Create attendee segments
- Analyze segment behavior
- Identify high-value segments

Survey Management:
- Design effective surveys
- Distribute surveys to attendees
- Analyze survey results

Reporting:
- Generate comprehensive reports
- Visualize data effectively
- Provide actionable insights

ROI Analysis:
- Calculate event ROI
- Analyze cost-effectiveness
- Identify revenue opportunities

Your current state:
Current phase: {current_phase}
Event details: {event_details}
Data sources: {data_sources}
Metrics: {metrics}
Segments: {segments}
Surveys: {surveys}
Reports: {reports}
ROI analysis: {roi_analysis}
Attendee analytics: {attendee_analytics}
Insights: {insights}
Next steps: {next_steps}

Follow these guidelines:
1. Analyze the event requirements to understand the analytics needs
2. Configure appropriate data sources based on the event type and scale
3. Define relevant metrics that align with event goals
4. Create segments to better understand attendee behavior
5. Design surveys to gather feedback at appropriate points
6. Generate reports that provide actionable insights
7. Calculate ROI to demonstrate event value
8. Generate insights that can improve future events

Respond to the coordinator agent or user in a helpful, professional manner. Ask clarifying questions when needed to gather complete analytics requirements.
"""


def create_analytics_graph():
    """
    Create the analytics agent graph.
    
    Returns:
        Compiled LangGraph for the analytics agent
    """
    # Initialize the LLM
    llm = get_llm(temperature=0.2)
    
    # Initialize tools
    tools = [
        DataCollectionTool(),
        MetricDefinitionTool(),
        SegmentationTool(),
        SurveyCreationTool(),
        ReportGenerationTool(),
        ROICalculationTool(),
        AttendeeAnalyticsTool(),
        InsightGenerationTool(),
        AnalyticsSearchTool()
    ]
    
    # Create the tool node
    tool_node = ToolNode(tools)
    
    # Define the nodes
    def analyze_data_requirements(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Analyze event requirements to determine data needs.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Get the last message
        last_message = state["messages"][-1]["content"] if state["messages"] else ""
        
        # Create a prompt for the LLM to analyze data requirements
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps analyze event analytics requirements.
Based on the event details and conversation, extract key information about:
1. Data collection needs
2. Metrics to track
3. Segments to analyze
4. Survey requirements
5. Reporting needs
6. ROI analysis requirements

Provide a structured analysis of the analytics requirements for this event."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Analyze these event details and the conversation to determine the analytics requirements for this event. Focus on data sources, metrics, segments, and reporting needs.""")
        ])
        
        # Analyze requirements using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the analysis to messages
        state["messages"].append({
            "role": "assistant",
            "content": result.content
        })
        
        # Update phase and next steps
        state["current_phase"] = "requirements_analysis"
        state["next_steps"] = ["configure_data_sources", "define_metrics", "create_segments", "design_surveys"]
        
        return state
    
    def configure_data_sources(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Configure data sources for analytics.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine data sources
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps determine appropriate data sources for event analytics.
Based on the event details and conversation, identify the data sources needed for comprehensive analytics.
Common data sources include:
1. Registration data
2. Attendance tracking
3. Survey responses
4. Website analytics
5. Social media metrics
6. Mobile app usage
7. Session feedback

For each data source, provide a name, type, and brief description."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Identify the data sources needed for analytics for this event. For each source, provide a name, type, and brief description.""")
        ])
        
        # Determine data sources using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the DataCollectionTool to configure data sources
        data_collection_tool = DataCollectionTool()
        
        # Configure standard data sources
        standard_sources = [
            {"name": "Registration System", "type": "registration", "description": "Attendee registration data including contact information and ticket types"},
            {"name": "Check-in System", "type": "tracking", "description": "Attendance tracking data from event check-in"},
            {"name": "Post-Event Survey", "type": "survey", "description": "Feedback collected from attendees after the event"},
            {"name": "Session Feedback", "type": "feedback", "description": "Ratings and comments for individual sessions"}
        ]
        
        # Add data sources to state
        if "data_sources" not in state:
            state["data_sources"] = []
        
        for source in standard_sources:
            # Configure the data source
            source_result = data_collection_tool._run(
                source_name=source["name"],
                source_type=source["type"],
                description=source["description"]
            )
            
            # Add the data source to the state
            state["data_sources"].append(source_result["data_source"])
        
        # Add data source configuration to messages
        data_sources_summary = "Configured Data Sources:\n"
        for source in state["data_sources"]:
            data_sources_summary += f"- {source['name']} ({source['type']}): {source['description'] or 'No description'}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"I've configured the following data sources for analytics:\n\n{data_sources_summary}\n\nThese sources will provide the data needed for comprehensive event analytics."
        })
        
        # Update phase and next steps
        state["current_phase"] = "data_configuration"
        state["next_steps"] = ["define_metrics", "create_segments", "design_surveys"]
        
        return state
    
    def define_metrics(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Define key performance metrics.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine metrics
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps define key performance metrics for event analytics.
Based on the event details and conversation, identify the metrics that should be tracked.
Common metrics include:
1. Registration rate
2. Attendance rate
3. Session attendance
4. Satisfaction ratings
5. Net Promoter Score (NPS)
6. Engagement metrics
7. ROI
8. Conversion rates

For each metric, provide a name, description, and unit of measurement."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Data sources: {state['data_sources']}

Identify the key performance metrics that should be tracked for this event. For each metric, provide a name, description, and unit of measurement.""")
        ])
        
        # Determine metrics using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the MetricDefinitionTool to define metrics
        metric_definition_tool = MetricDefinitionTool()
        
        # Define standard metrics
        standard_metrics = [
            {"name": "Registration Rate", "description": "Percentage of invitees who registered", "data_source": "Registration System", "unit": "percentage"},
            {"name": "Attendance Rate", "description": "Percentage of registrants who attended", "data_source": "Check-in System", "unit": "percentage"},
            {"name": "Overall Satisfaction", "description": "Average satisfaction rating from post-event survey", "data_source": "Post-Event Survey", "unit": "rating"},
            {"name": "Net Promoter Score", "description": "Likelihood to recommend the event to others", "data_source": "Post-Event Survey", "unit": "score"},
            {"name": "Session Engagement", "description": "Average attendance across all sessions", "data_source": "Session Feedback", "unit": "percentage"}
        ]
        
        # Add metrics to state
        if "metrics" not in state:
            state["metrics"] = []
        
        for metric_def in standard_metrics:
            # Define the metric
            metric_result = metric_definition_tool._run(
                name=metric_def["name"],
                description=metric_def["description"],
                data_source=metric_def["data_source"],
                unit=metric_def["unit"]
            )
            
            # Add the metric to the state
            state["metrics"].append(metric_result["metric"])
        
        # Add metric definitions to messages
        metrics_summary = "Defined Metrics:\n"
        for metric in state["metrics"]:
            metrics_summary += f"- {metric['name']}: {metric['value']} {metric['unit']} - {metric['description']}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"I've defined the following key performance metrics for the event:\n\n{metrics_summary}\n\nThese metrics will help measure the success of the event and identify areas for improvement."
        })
        
        # Update phase and next steps
        state["current_phase"] = "metric_definition"
        state["next_steps"] = ["create_segments", "design_surveys", "generate_reports"]
        
        return state
    
    def create_segments(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Create attendee segments for analysis.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine segments
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps define attendee segments for event analytics.
Based on the event details and conversation, identify the segments that should be analyzed.
Common segments include:
1. VIPs
2. First-time attendees
3. Returning attendees
4. Early registrants
5. Speakers
6. Sponsors
7. Industry segments
8. Job role segments

For each segment, provide a name and criteria for inclusion."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Data sources: {state['data_sources']}

Identify the attendee segments that should be analyzed for this event. For each segment, provide a name and criteria for inclusion.""")
        ])
        
        # Determine segments using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the SegmentationTool to create segments
        segmentation_tool = SegmentationTool()
        
        # Create standard segments
        standard_segments = [
            {"name": "VIPs", "criteria": {"status": "VIP"}},
            {"name": "First-time Attendees", "criteria": {"previous_attendance": 0}},
            {"name": "Returning Attendees", "criteria": {"previous_attendance": {"$gt": 0}}},
            {"name": "Early Registrants", "criteria": {"registration_date": {"$lt": "event_date-30d"}}}
        ]
        
        # Add segments to state
        if "segments" not in state:
            state["segments"] = []
        
        # Estimate total attendees from event details
        total_attendees = state["event_details"].get("attendee_count", 300)
        
        for segment_def in standard_segments:
            # Create the segment
            segment_result = segmentation_tool._run(
                name=segment_def["name"],
                criteria=segment_def["criteria"],
                total_attendees=total_attendees
            )
            
            # Add the segment to the state
            state["segments"].append(segment_result["segment"])
        
        # Add segment creation to messages
        segments_summary = "Created Segments:\n"
        for segment in state["segments"]:
            segments_summary += f"- {segment['name']}: {segment['size']} attendees ({segment['percentage']:.1f}% of total)\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"I've created the following attendee segments for analysis:\n\n{segments_summary}\n\nThese segments will help understand different attendee groups and their behavior."
        })
        
        # Update phase and next steps
        state["current_phase"] = "segmentation"
        state["next_steps"] = ["design_surveys", "generate_reports", "calculate_roi"]
        
        return state
    
    def design_surveys(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Design surveys for feedback collection.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine survey needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps design surveys for event feedback.
Based on the event details and conversation, identify the surveys that should be created.
Common surveys include:
1. Pre-event survey
2. Post-event survey
3. Session feedback
4. Speaker evaluation
5. Exhibitor feedback

For each survey, provide a title, description, target audience, and distribution channel."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Data sources: {state['data_sources']}

Identify the surveys that should be created for this event. For each survey, provide a title, description, target audience, and distribution channel.""")
        ])
        
        # Determine surveys using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the SurveyCreationTool to create surveys
        survey_creation_tool = SurveyCreationTool()
        
        # Create standard surveys
        standard_surveys = [
            {
                "title": "Post-Event Satisfaction Survey",
                "description": "Collect feedback on overall event experience",
                "target_audience": "All Attendees",
                "distribution_channel": "Email",
                "question_types": ["multiple_choice", "rating", "open_ended", "nps"]
            },
            {
                "title": "Session Feedback Survey",
                "description": "Collect feedback on individual sessions",
                "target_audience": "Session Attendees",
                "distribution_channel": "Mobile App",
                "question_types": ["rating", "open_ended", "yes_no"]
            }
        ]
        
        # Add surveys to state
        if "surveys" not in state:
            state["surveys"] = []
        
        for survey_def in standard_surveys:
            # Create the survey
            survey_result = survey_creation_tool._run(
                title=survey_def["title"],
                description=survey_def["description"],
                target_audience=survey_def["target_audience"],
                distribution_channel=survey_def["distribution_channel"],
                question_types=survey_def["question_types"]
            )
            
            # Add the survey to the state
            state["surveys"].append(survey_result["survey"])
        
        # Add survey creation to messages
        surveys_summary = "Created Surveys:\n"
        for survey in state["surveys"]:
            surveys_summary += f"- {survey['title']}: {len(survey['questions'])} questions - {survey['distribution_channel']}\n"
            surveys_summary += f"  Description: {survey['description']}\n"
            surveys_summary += f"  Target: {survey['target_audience'] or 'All Attendees'}\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"I've designed the following surveys for feedback collection:\n\n{surveys_summary}\n\nThese surveys will help gather valuable feedback from attendees."
        })
        
        # Update phase and next steps
        state["current_phase"] = "survey_design"
        state["next_steps"] = ["generate_reports", "calculate_roi", "analyze_attendees"]
        
        return state
    
    def generate_reports(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Generate analytics reports.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine report needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps define analytics reports for events.
Based on the event details, metrics, and segments, identify the reports that should be generated.
Common reports include:
1. Executive summary
2. Attendance report
3. Engagement report
4. Satisfaction report
5. ROI report
6. Segment comparison report

For each report, provide a title, description, and the metrics to include."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Metrics: {state['metrics']}
Segments: {state['segments']}

Identify the analytics reports that should be generated for this event. For each report, provide a title, description, and the metrics to include.""")
        ])
        
        # Determine reports using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the ReportGenerationTool to create reports
        report_generation_tool = ReportGenerationTool()
        
        # Create standard reports
        standard_reports = [
            {
                "title": "Event Performance Summary",
                "description": "Overview of key event performance metrics",
                "metrics": ["Registration Rate", "Attendance Rate", "Overall Satisfaction", "Net Promoter Score"],
                "segments": ["VIPs", "First-time Attendees"]
            },
            {
                "title": "Attendee Engagement Report",
                "description": "Analysis of attendee engagement throughout the event",
                "metrics": ["Session Engagement", "Feedback Submission Rate", "Content Download Rate"],
                "segments": ["Returning Attendees", "Early Registrants"]
            }
        ]
        
        # Add reports to state
        if "reports" not in state:
            state["reports"] = []
        
        for report_def in standard_reports:
            # Create the report
            report_result = report_generation_tool._run(
                title=report_def["title"],
                description=report_def["description"],
                metrics=report_def["metrics"],
                segments=report_def.get("segments")
            )
            
            # Add the report to the state
            state["reports"].append(report_result["report"])
        
        # Add report generation to messages
        reports_summary = "Generated Reports:\n"
        for report in state["reports"]:
            reports_summary += f"- {report['title']}: {report['description']}\n"
            reports_summary += f"  Key Metrics: {', '.join([metric['name'] for metric in report['metrics']])}\n"
            if report.get('segments'):
                reports_summary += f"  Segments Analyzed: {', '.join([segment['name'] for segment in report['segments']])}\n"
            reports_summary += f"  Key Insights: {len(report['insights'])} insights\n"
        
        state["messages"].append({
            "role": "assistant",
            "content": f"I've generated the following analytics reports:\n\n{reports_summary}\n\nThese reports provide comprehensive insights into the event performance."
        })
        
        # Update phase and next steps
        state["current_phase"] = "reporting"
        state["next_steps"] = ["calculate_roi", "analyze_attendees", "generate_insights"]
        
        return state
    
    def calculate_roi(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Calculate and analyze ROI.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine ROI calculation needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps calculate ROI for events.
Based on the event details and conversation, identify the costs and revenue sources for ROI calculation.
Common costs include:
1. Venue
2. Catering
3. Marketing
4. Speakers
5. Staff
6. Technology

Common revenue sources include:
1. Ticket sales
2. Sponsorships
3. Exhibitor fees
4. Merchandise sales
5. Post-event sales

Also identify non-financial benefits that should be considered."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}

Identify the costs, revenue sources, and non-financial benefits for ROI calculation for this event.""")
        ])
        
        # Determine ROI calculation needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the ROICalculationTool to calculate ROI
        roi_calculation_tool = ROICalculationTool()
        
        # Estimate total cost from event details
        event_scale = state["event_details"].get("scale", "medium").lower()
        attendee_count = state["event_details"].get("attendee_count", 300)
        
        if event_scale == "small" or attendee_count < 100:
            total_cost = 25000.0
        elif event_scale == "medium" or attendee_count < 500:
            total_cost = 75000.0
        else:
            total_cost = 150000.0
        
        # Define revenue sources
        revenue_sources = {
            "Ticket Sales": total_cost * 0.6,
            "Sponsorships": total_cost * 0.3,
            "Exhibitor Fees": total_cost * 0.2,
            "Merchandise": total_cost * 0.05
        }
        
        # Define non-financial benefits
        non_financial_benefits = [
            "Brand awareness and recognition",
            "Relationship building with key stakeholders",
            "Knowledge sharing and education",
            "Community building",
            "Lead generation for future business"
        ]
        
        # Calculate ROI
        roi_result = roi_calculation_tool._run(
            total_cost=total_cost,
            revenue_sources=revenue_sources,
            non_financial_benefits=non_financial_benefits
        )
        
        # Update state with ROI analysis
        state["roi_analysis"] = roi_result["roi_analysis"]
        
        # Add ROI calculation to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've calculated the ROI for the event:\n\n{roi_result['summary']}\n\nThis analysis helps demonstrate the value of the event in financial terms, while also acknowledging the non-financial benefits."
        })
        
        # Update phase and next steps
        state["current_phase"] = "roi_analysis"
        state["next_steps"] = ["analyze_attendees", "generate_insights"]
        
        return state
    
    def analyze_attendees(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Analyze attendee data.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine attendee analysis needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps analyze attendee data for events.
Based on the event details and conversation, identify the attendee metrics that should be analyzed.
Common metrics include:
1. Registration rate
2. Attendance rate
3. Demographic breakdown
4. Acquisition channels
5. Engagement metrics

Also identify the demographic categories and acquisition channels that should be analyzed."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Segments: {state['segments']}

Identify the attendee metrics, demographic categories, and acquisition channels that should be analyzed for this event.""")
        ])
        
        # Determine attendee analysis needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the AttendeeAnalyticsTool to analyze attendees
        attendee_analytics_tool = AttendeeAnalyticsTool()
        
        # Estimate attendee numbers from event details
        attendee_count = state["event_details"].get("attendee_count", 300)
        total_invitees = int(attendee_count * 1.5)  # 50% more invitees than attendees
        total_registrants = int(attendee_count * 1.2)  # 20% more registrants than attendees
        
        # Analyze attendees
        attendee_result = attendee_analytics_tool._run(
            total_invitees=total_invitees,
            total_registrants=total_registrants,
            total_attendees=attendee_count
        )
        
        # Update state with attendee analytics
        state["attendee_analytics"] = attendee_result["attendee_analytics"]
        
        # Add attendee analysis to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've analyzed the attendee data for the event:\n\n{attendee_result['summary']}\n\nThis analysis provides insights into attendee demographics, acquisition channels, and engagement metrics."
        })
        
        # Update phase and next steps
        state["current_phase"] = "attendee_analysis"
        state["next_steps"] = ["generate_insights"]
        
        return state
    
    def generate_insights(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Generate insights from analytics data.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create a prompt for the LLM to determine insight generation needs
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps generate insights from event analytics data.
Based on the metrics, segments, reports, and ROI analysis, identify the key insights that should be highlighted.
Focus on:
1. Performance against goals
2. Unexpected findings
3. Correlations between metrics
4. Segment comparisons
5. Opportunities for improvement
6. Recommendations for future events

For each insight, provide a clear description and actionable recommendations."""),
            MessagesPlaceholder(variable_name="messages"),
            HumanMessage(content=f"""Event details: {state['event_details']}
Metrics: {state['metrics']}
Segments: {state['segments']}
Reports: {state['reports']}
ROI analysis: {state['roi_analysis']}
Attendee analytics: {state['attendee_analytics']}

Identify the key insights that should be highlighted from this analytics data.""")
        ])
        
        # Determine insight generation needs using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Use the InsightGenerationTool to generate insights
        insight_generation_tool = InsightGenerationTool()
        
        # Generate insights
        insight_result = insight_generation_tool._run(
            metrics=state["metrics"],
            segments=state["segments"] if "segments" in state else None,
            insight_count=5
        )
        
        # Update state with insights
        if "insights" not in state:
            state["insights"] = []
        
        state["insights"].extend(insight_result["insights"])
        
        # Add insight generation to messages
        state["messages"].append({
            "role": "assistant",
            "content": f"I've generated the following insights from the analytics data:\n\n{insight_result['summary']}\n\nThese insights provide actionable recommendations to improve future events."
        })
        
        # Update phase and next steps
        state["current_phase"] = "insight_generation"
        state["next_steps"] = ["finalize_analytics"]
        
        return state
    
    def generate_response(state: AnalyticsStateDict) -> AnalyticsStateDict:
        """
        Generate a response to the user or coordinator agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        # Create the analytics prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=ANALYTICS_SYSTEM_PROMPT.format(
                current_phase=state["current_phase"],
                event_details=state["event_details"],
                data_sources=state["data_sources"] if "data_sources" in state else [],
                metrics=state["metrics"] if "metrics" in state else [],
                segments=state["segments"] if "segments" in state else [],
                surveys=state["surveys"] if "surveys" in state else [],
                reports=state["reports"] if "reports" in state else [],
                roi_analysis=state["roi_analysis"] if "roi_analysis" in state else None,
                attendee_analytics=state["attendee_analytics"] if "attendee_analytics" in state else None,
                insights=state["insights"] if "insights" in state else [],
                next_steps=state["next_steps"]
            )),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        # Generate response using the LLM
        chain = prompt | llm
        result = chain.invoke({"messages": [{"role": m["role"], "content": m["content"]} for m in state["messages"]]})
        
        # Add the response to messages
        new_message = {
            "role": "assistant",
            "content": result.content
        }
        state["messages"].append(new_message)
        
        return state
    
    # Create the graph
    workflow = StateGraph(AnalyticsStateDict)
    
    # Add nodes
    workflow.add_node("analyze_data_requirements", analyze_data_requirements)
    workflow.add_node("configure_data_sources", configure_data_sources)
    workflow.add_node("define_metrics", define_metrics)
    workflow.add_node("create_segments", create_segments)
    workflow.add_node("design_surveys", design_surveys)
    workflow.add_node("generate_reports", generate_reports)
    workflow.add_node("calculate_roi", calculate_roi)
    workflow.add_node("analyze_attendees", analyze_attendees)
    workflow.add_node("generate_insights", generate_insights)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_edge("analyze_data_requirements", "configure_data_sources")
    workflow.add_edge("configure_data_sources", "define_metrics")
    workflow.add_edge("define_metrics", "create_segments")
    workflow.add_edge("create_segments", "design_surveys")
    workflow.add_edge("design_surveys", "generate_reports")
    workflow.add_edge("generate_reports", "calculate_roi")
    workflow.add_edge("calculate_roi", "analyze_attendees")
    workflow.add_edge("analyze_attendees", "generate_insights")
    workflow.add_edge("generate_insights", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_data_requirements")
    
    return workflow.compile()


def create_initial_state() -> AnalyticsStateDict:
    """
    Create the initial state for the analytics agent.
    
    Returns:
        Initial state dictionary
    """
    return {
        "messages": [],
        "event_details": {
            "event_type": None,
            "title": None,
            "description": None,
            "attendee_count": None,
            "scale": None,
            "timeline_start": None,
            "timeline_end": None,
            "budget": None,
            "location": None
        },
        "data_sources": [],
        "metrics": [],
        "segments": [],
        "surveys": [],
        "reports": [],
        "roi_analysis": None,
        "attendee_analytics": None,
        "insights": [],
        "current_phase": "initial_assessment",
        "next_steps": ["analyze_data_requirements"]
    }
