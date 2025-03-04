import asyncio
import json
from datetime import datetime

from app.graphs.analytics_graph import create_analytics_graph, create_initial_state
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
from app.config import OPENAI_API_KEY, LLM_MODEL


async def test_analytics_agent():
    """
    Test the Analytics Agent's functionality.
    """
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    print(f"Using LLM model: {LLM_MODEL}")
    
    # Create the analytics graph
    print("Initializing Analytics Agent...")
    analytics_graph = create_analytics_graph()
    
    # Create initial state with some predefined event details
    state = create_initial_state()
    
    # Add initial system message
    state["messages"].append({
        "role": "system",
        "content": "The conversation has started. The Analytics Agent will help analyze data for your event.",
        "ephemeral": True
    })
    
    # Set some event details for testing
    state["event_details"] = {
        "event_type": "conference",
        "title": "Tech Innovation Summit 2025",
        "description": "A conference focused on emerging technologies and innovation",
        "attendee_count": 300,
        "scale": "medium",
        "timeline_start": "2025-06-15",
        "timeline_end": "2025-06-17",
        "budget": 75000,
        "location": "San Francisco"
    }
    
    # Test 1: Data Source Configuration
    print("\n=== Test 1: Data Source Configuration ===")
    
    # Add a user message to trigger data source configuration
    state["messages"].append({
        "role": "user",
        "content": "I need to set up data sources for our Tech Innovation Summit. We need to track registrations, attendance, and feedback."
    })
    
    # Run the analytics graph to configure data sources
    result = analytics_graph.invoke(state, {"override_next": "configure_data_sources"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent (Data Sources):", assistant_messages[-1]["content"])
    
    # Test 2: Metric Definition
    print("\n=== Test 2: Metric Definition ===")
    
    # Add a user message to trigger metric definition
    result["messages"].append({
        "role": "user",
        "content": "I need to define key performance metrics for the event. We want to track registration rate, attendance rate, satisfaction, and engagement."
    })
    
    # Run the analytics graph to define metrics
    result = analytics_graph.invoke(result, {"override_next": "define_metrics"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent (Metrics):", assistant_messages[-1]["content"])
    
    # Test 3: Segmentation
    print("\n=== Test 3: Segmentation ===")
    
    # Add a user message to trigger segmentation
    result["messages"].append({
        "role": "user",
        "content": "I want to create segments for our attendees. We should have segments for VIPs, first-time attendees, and returning attendees."
    })
    
    # Run the analytics graph to create segments
    result = analytics_graph.invoke(result, {"override_next": "create_segments"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent (Segmentation):", assistant_messages[-1]["content"])
    
    # Test 4: Survey Design
    print("\n=== Test 4: Survey Design ===")
    
    # Add a user message to trigger survey design
    result["messages"].append({
        "role": "user",
        "content": "I need to create a post-event satisfaction survey for all attendees."
    })
    
    # Run the analytics graph to design surveys
    result = analytics_graph.invoke(result, {"override_next": "design_surveys"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent (Surveys):", assistant_messages[-1]["content"])
    
    # Test 5: Report Generation
    print("\n=== Test 5: Report Generation ===")
    
    # Add a user message to trigger report generation
    result["messages"].append({
        "role": "user",
        "content": "Can you generate an event performance report based on our metrics?"
    })
    
    # Run the analytics graph to generate reports
    result = analytics_graph.invoke(result, {"override_next": "generate_reports"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent (Reports):", assistant_messages[-1]["content"])
    
    # Test 6: ROI Calculation
    print("\n=== Test 6: ROI Calculation ===")
    
    # Add a user message to trigger ROI calculation
    result["messages"].append({
        "role": "user",
        "content": "I need to calculate the ROI for this event. Our total cost is $75,000 and we expect to generate $100,000 in revenue from ticket sales and sponsorships."
    })
    
    # Run the analytics graph to calculate ROI
    result = analytics_graph.invoke(result, {"override_next": "calculate_roi"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent (ROI):", assistant_messages[-1]["content"])
    
    # Test 7: Attendee Analysis
    print("\n=== Test 7: Attendee Analysis ===")
    
    # Add a user message to trigger attendee analysis
    result["messages"].append({
        "role": "user",
        "content": "Can you analyze our attendee data? We invited 450 people, 360 registered, and 300 attended."
    })
    
    # Run the analytics graph to analyze attendees
    result = analytics_graph.invoke(result, {"override_next": "analyze_attendees"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent (Attendee Analysis):", assistant_messages[-1]["content"])
    
    # Test 8: Insight Generation
    print("\n=== Test 8: Insight Generation ===")
    
    # Add a user message to trigger insight generation
    result["messages"].append({
        "role": "user",
        "content": "Can you generate insights based on our analytics data?"
    })
    
    # Run the analytics graph to generate insights
    result = analytics_graph.invoke(result, {"override_next": "generate_insights"})
    
    # Print the assistant's response
    assistant_messages = [m for m in result["messages"] if m["role"] == "assistant"]
    if assistant_messages:
        print("\nAnalytics Agent (Insights):", assistant_messages[-1]["content"])
    
    # Print the final state for debugging
    print("\n=== Final State ===")
    print("Data Sources:", f"{len(result['data_sources'])} data sources configured" if "data_sources" in result and result["data_sources"] else "None")
    print("Metrics:", f"{len(result['metrics'])} metrics defined" if "metrics" in result and result["metrics"] else "None")
    print("Segments:", f"{len(result['segments'])} segments created" if "segments" in result and result["segments"] else "None")
    print("Surveys:", f"{len(result['surveys'])} surveys designed" if "surveys" in result and result["surveys"] else "None")
    print("Reports:", f"{len(result['reports'])} reports generated" if "reports" in result and result["reports"] else "None")
    print("ROI Analysis:", "Calculated" if "roi_analysis" in result and result["roi_analysis"] else "None")
    print("Attendee Analytics:", "Analyzed" if "attendee_analytics" in result and result["attendee_analytics"] else "None")
    print("Insights:", f"{len(result['insights'])} insights generated" if "insights" in result and result["insights"] else "None")
    
    # Test individual tools directly
    print("\n=== Testing Individual Tools ===")
    
    # Test DataCollectionTool
    print("\nTesting DataCollectionTool:")
    data_collection_tool = DataCollectionTool()
    data_source_result = data_collection_tool._run(
        source_name="Registration System",
        source_type="registration",
        description="Attendee registration data including contact information and ticket types"
    )
    print(f"Data source configured: {data_source_result['data_source']['name']} ({data_source_result['data_source']['type']})")
    print(f"Sample data records: {len(data_source_result['sample_data'])}")
    
    # Test MetricDefinitionTool
    print("\nTesting MetricDefinitionTool:")
    metric_definition_tool = MetricDefinitionTool()
    metric_result = metric_definition_tool._run(
        name="Registration Rate",
        description="Percentage of invitees who registered",
        data_source="Registration System",
        unit="percentage"
    )
    print(f"Metric defined: {metric_result['metric']['name']} - {metric_result['metric']['value']} {metric_result['metric']['unit']}")
    print(f"Historical values: {len(metric_result['historical_values'])}")
    
    # Test SegmentationTool
    print("\nTesting SegmentationTool:")
    segmentation_tool = SegmentationTool()
    segment_result = segmentation_tool._run(
        name="VIPs",
        criteria={"status": "VIP"},
        total_attendees=300
    )
    print(f"Segment created: {segment_result['segment']['name']} - {segment_result['segment']['size']} attendees ({segment_result['segment']['percentage']:.1f}%)")
    print(f"Engagement metrics: {len(segment_result['engagement_metrics'])}")
    
    # Test SurveyCreationTool
    print("\nTesting SurveyCreationTool:")
    survey_creation_tool = SurveyCreationTool()
    survey_result = survey_creation_tool._run(
        title="Post-Event Satisfaction Survey",
        description="Collect feedback on overall event experience",
        distribution_channel="Email",
        question_types=["multiple_choice", "rating", "open_ended", "nps"]
    )
    print(f"Survey created: {survey_result['survey']['title']} - {len(survey_result['survey']['questions'])} questions")
    print(f"Distribution channel: {survey_result['survey']['distribution_channel']}")
    
    # Test ReportGenerationTool
    print("\nTesting ReportGenerationTool:")
    report_generation_tool = ReportGenerationTool()
    report_result = report_generation_tool._run(
        title="Event Performance Summary",
        description="Overview of key event performance metrics",
        metrics=["Registration Rate", "Attendance Rate", "Overall Satisfaction", "Net Promoter Score"]
    )
    print(f"Report generated: {report_result['report']['title']}")
    print(f"Metrics included: {len(report_result['report']['metrics'])}")
    print(f"Insights: {len(report_result['report']['insights'])}")
    
    # Test ROICalculationTool
    print("\nTesting ROICalculationTool:")
    roi_calculation_tool = ROICalculationTool()
    roi_result = roi_calculation_tool._run(
        total_cost=75000.0,
        revenue_sources={
            "Ticket Sales": 60000.0,
            "Sponsorships": 30000.0,
            "Exhibitor Fees": 15000.0
        },
        non_financial_benefits=[
            "Brand awareness and recognition",
            "Relationship building with key stakeholders",
            "Knowledge sharing and education"
        ]
    )
    print(f"ROI calculated: {roi_result['roi_analysis']['roi_percentage']:.1f}%")
    print(f"Total cost: ${roi_result['roi_analysis']['total_cost']:,.2f}")
    print(f"Total revenue: ${roi_result['roi_analysis']['total_revenue']:,.2f}")
    
    # Test AttendeeAnalyticsTool
    print("\nTesting AttendeeAnalyticsTool:")
    attendee_analytics_tool = AttendeeAnalyticsTool()
    attendee_result = attendee_analytics_tool._run(
        total_invitees=450,
        total_registrants=360,
        total_attendees=300
    )
    print(f"Registration rate: {attendee_result['attendee_analytics']['registration_rate']:.1f}%")
    print(f"Attendance rate: {attendee_result['attendee_analytics']['attendance_rate']:.1f}%")
    print(f"Demographics: {len(attendee_result['attendee_analytics']['demographics'])}")
    
    # Test InsightGenerationTool
    print("\nTesting InsightGenerationTool:")
    insight_generation_tool = InsightGenerationTool()
    insight_result = insight_generation_tool._run(
        metrics=[
            {"name": "Registration Rate", "value": 80.0, "unit": "percentage"},
            {"name": "Attendance Rate", "value": 83.3, "unit": "percentage"},
            {"name": "Overall Satisfaction", "value": 4.2, "unit": "rating"}
        ],
        insight_count=3
    )
    print(f"Insights generated: {len(insight_result['insights'])}")
    print(f"Action items: {len(insight_result['action_items'])}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_analytics_agent())
