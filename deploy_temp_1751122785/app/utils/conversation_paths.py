"""
Goal-Oriented Conversation Paths for Conversational Agent
Defines conversation flows and question sequences based on user goals.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class ConversationPathManager:
    """
    Manages goal-oriented conversation paths and adaptive questioning.
    Provides structured conversation flows based on user goals and event types.
    """
    
    def __init__(self):
        """Initialize conversation paths and goal-specific configurations."""
        
        # Define conversation paths for different goals
        self.conversation_paths = {
            "networking": {
                "priority_questions": [
                    "attendee_count",
                    "attendee_profile", 
                    "venue_type",
                    "event_duration",
                    "catering_needs",
                    "interaction_format",
                    "follow_up_strategy"
                ],
                "recommendations": [
                    "interactive_sessions",
                    "structured_networking", 
                    "contact_exchange",
                    "icebreaker_activities",
                    "networking_apps"
                ],
                "conversation_flow": {
                    "discovery": [
                        "What's your primary networking goal? (building partnerships, finding clients, industry connections, etc.)",
                        "Who is your target audience for networking?",
                        "What industries or roles do you want to connect with?"
                    ],
                    "format_planning": [
                        "What networking format interests you most? (cocktail reception, structured sessions, speed networking)",
                        "How much time do you want to dedicate to networking activities?",
                        "Do you prefer formal introductions or organic mingling?"
                    ],
                    "logistics": [
                        "What tools will help facilitate connections? (name tags, networking apps, conversation starters)",
                        "How will attendees exchange contact information?",
                        "What follow-up strategy will you implement?"
                    ]
                },
                "success_metrics": [
                    "Number of meaningful connections made",
                    "Quality of conversations and interactions", 
                    "Follow-up meetings scheduled",
                    "Business cards or contacts exchanged",
                    "Post-event collaboration initiated"
                ]
            },
            
            "lead_generation": {
                "priority_questions": [
                    "target_audience",
                    "attendee_count",
                    "conversion_goals",
                    "speakers_needed",
                    "av_equipment",
                    "success_metrics",
                    "follow_up_process"
                ],
                "recommendations": [
                    "demos",
                    "lead_capture",
                    "qualification_process",
                    "interactive_exhibits",
                    "crm_integration"
                ],
                "conversation_flow": {
                    "discovery": [
                        "What specific leads are you trying to generate? (sales prospects, partnership opportunities, etc.)",
                        "Who is your ideal customer profile for this event?",
                        "What's your target number of qualified leads?"
                    ],
                    "strategy_planning": [
                        "What lead magnets will you offer? (demos, consultations, resources, trials)",
                        "How will you qualify leads during the event?",
                        "What information do you need to collect from prospects?"
                    ],
                    "conversion_planning": [
                        "What's your lead scoring criteria?",
                        "How quickly will you follow up with leads?",
                        "What's your conversion process after the event?"
                    ]
                },
                "success_metrics": [
                    "Number of qualified leads generated",
                    "Lead quality score",
                    "Conversion rate from lead to opportunity",
                    "Cost per lead acquired",
                    "Pipeline value generated"
                ]
            },
            
            "education": {
                "priority_questions": [
                    "learning_objectives",
                    "speakers_needed",
                    "av_equipment",
                    "space_requirements",
                    "event_duration",
                    "attendee_count",
                    "materials_needed"
                ],
                "recommendations": [
                    "workshop_format",
                    "interactive_learning",
                    "resource_materials",
                    "hands_on_activities",
                    "knowledge_assessment"
                ],
                "conversation_flow": {
                    "discovery": [
                        "What specific knowledge or skills do you want attendees to gain?",
                        "What's the current skill level of your target audience?",
                        "What learning outcomes are most important to achieve?"
                    ],
                    "content_planning": [
                        "What teaching methods work best for your audience? (lectures, workshops, hands-on, discussions)",
                        "Do you need expert speakers or can you provide internal expertise?",
                        "What materials or resources will attendees need?"
                    ],
                    "engagement_planning": [
                        "How will you keep attendees engaged throughout the session?",
                        "What interactive elements will you include?",
                        "How will you assess learning and provide feedback?"
                    ]
                },
                "success_metrics": [
                    "Learning objectives achieved",
                    "Attendee engagement levels",
                    "Knowledge retention assessment",
                    "Skill application post-event",
                    "Attendee satisfaction with content"
                ]
            },
            
            "brand_awareness": {
                "priority_questions": [
                    "target_audience",
                    "attendee_count",
                    "sponsors_needed",
                    "success_metrics",
                    "venue_type",
                    "marketing_strategy",
                    "media_coverage"
                ],
                "recommendations": [
                    "media_coverage",
                    "social_media",
                    "branded_experiences",
                    "influencer_partnerships",
                    "photo_opportunities"
                ],
                "conversation_flow": {
                    "discovery": [
                        "What specific brand message do you want to communicate?",
                        "Who is your target audience for brand awareness?",
                        "What brand perception do you want to create or change?"
                    ],
                    "experience_planning": [
                        "What memorable brand experiences will you create?",
                        "How will you incorporate your brand into the event naturally?",
                        "What photo and social media opportunities will you provide?"
                    ],
                    "amplification_planning": [
                        "How will you amplify your brand message beyond the event?",
                        "What media coverage are you targeting?",
                        "How will you measure brand awareness impact?"
                    ]
                },
                "success_metrics": [
                    "Brand mention volume and sentiment",
                    "Social media engagement and reach",
                    "Media coverage quality and quantity",
                    "Brand recall and recognition surveys",
                    "Website traffic and inquiries generated"
                ]
            },
            
            "team_building": {
                "priority_questions": [
                    "team_size",
                    "attendee_count",
                    "venue_type",
                    "event_duration",
                    "catering_needs",
                    "activity_preferences",
                    "team_challenges"
                ],
                "recommendations": [
                    "interactive_activities",
                    "group_exercises",
                    "informal_bonding",
                    "collaborative_challenges",
                    "reflection_sessions"
                ],
                "conversation_flow": {
                    "discovery": [
                        "What specific team dynamics do you want to improve?",
                        "What challenges is your team currently facing?",
                        "What team strengths do you want to build upon?"
                    ],
                    "activity_planning": [
                        "What types of activities does your team enjoy? (physical, creative, problem-solving)",
                        "Do you prefer structured activities or organic team bonding?",
                        "How competitive or collaborative should the activities be?"
                    ],
                    "outcome_planning": [
                        "What specific team improvements do you want to see?",
                        "How will you reinforce team building lessons back at work?",
                        "What follow-up activities will you implement?"
                    ]
                },
                "success_metrics": [
                    "Team cohesion improvement",
                    "Communication effectiveness",
                    "Trust and collaboration levels",
                    "Employee engagement scores",
                    "Workplace productivity improvements"
                ]
            },
            
            "product_launch": {
                "priority_questions": [
                    "product_details",
                    "target_audience",
                    "attendee_count",
                    "av_equipment",
                    "venue_type",
                    "success_metrics",
                    "media_strategy"
                ],
                "recommendations": [
                    "demo_stations",
                    "media_kit",
                    "follow_up_strategy",
                    "influencer_engagement",
                    "product_trials"
                ],
                "conversation_flow": {
                    "discovery": [
                        "What product are you launching and what makes it unique?",
                        "Who is your primary target market for this product?",
                        "What key messages do you want to communicate about the product?"
                    ],
                    "experience_planning": [
                        "How will attendees experience your product? (demos, trials, presentations)",
                        "What proof points and testimonials will you share?",
                        "How will you handle questions and objections?"
                    ],
                    "conversion_planning": [
                        "What actions do you want attendees to take after the launch?",
                        "How will you capture interest and convert to sales?",
                        "What follow-up process will you implement?"
                    ]
                },
                "success_metrics": [
                    "Product trial sign-ups",
                    "Pre-orders or sales generated",
                    "Media coverage and mentions",
                    "Social media buzz and engagement",
                    "Lead generation and pipeline impact"
                ]
            },
            
            "fundraising": {
                "priority_questions": [
                    "fundraising_goal",
                    "target_audience",
                    "attendee_count",
                    "venue_type",
                    "catering_needs",
                    "entertainment",
                    "donation_process"
                ],
                "recommendations": [
                    "compelling_storytelling",
                    "donation_stations",
                    "auction_items",
                    "sponsor_recognition",
                    "impact_demonstration"
                ],
                "conversation_flow": {
                    "discovery": [
                        "What is your fundraising goal and what will the funds support?",
                        "Who are your target donors and what motivates them?",
                        "What compelling story will you tell about your cause?"
                    ],
                    "engagement_planning": [
                        "How will you engage donors emotionally with your cause?",
                        "What donation opportunities will you provide? (auction, direct giving, sponsorships)",
                        "How will you recognize and thank donors?"
                    ],
                    "conversion_planning": [
                        "What donation methods will you accept?",
                        "How will you follow up with donors after the event?",
                        "What ongoing engagement strategy do you have?"
                    ]
                },
                "success_metrics": [
                    "Total funds raised",
                    "Number of new donors acquired",
                    "Average donation amount",
                    "Donor retention rate",
                    "Cost per dollar raised"
                ]
            }
        }
        
        # Event type specific conversation modifications
        self.event_type_modifiers = {
            "conference": {
                "additional_priorities": ["speakers_needed", "av_equipment", "space_requirements"],
                "conversation_additions": {
                    "content_planning": [
                        "What topics and themes will your conference cover?",
                        "Do you need keynote speakers or breakout session leaders?",
                        "What level of interactivity do you want in sessions?"
                    ]
                }
            },
            "wedding": {
                "additional_priorities": ["catering_needs", "venue_type", "photography"],
                "conversation_additions": {
                    "celebration_planning": [
                        "What style and atmosphere do you want for your celebration?",
                        "What traditions or customs are important to include?",
                        "How formal or casual should the event be?"
                    ]
                }
            },
            "corporate": {
                "additional_priorities": ["stakeholders", "success_metrics", "budget_range"],
                "conversation_additions": {
                    "business_planning": [
                        "What business objectives does this event support?",
                        "Who are the key stakeholders that need to be involved?",
                        "How will you measure ROI and business impact?"
                    ]
                }
            }
        }
    
    def get_conversation_path(self, user_goals: List[str], event_type: str = "") -> Dict[str, Any]:
        """
        Get the conversation path configuration for given goals and event type.
        
        Args:
            user_goals: List of user goals
            event_type: Type of event being planned
            
        Returns:
            Combined conversation path configuration
        """
        if not user_goals:
            return self._get_default_path()
        
        # Start with the primary goal's path
        primary_goal = user_goals[0].lower()
        if primary_goal not in self.conversation_paths:
            return self._get_default_path()
        
        path_config = self.conversation_paths[primary_goal].copy()
        
        # Merge additional goals
        for goal in user_goals[1:]:
            goal_lower = goal.lower()
            if goal_lower in self.conversation_paths:
                additional_path = self.conversation_paths[goal_lower]
                
                # Merge priority questions (avoid duplicates)
                for question in additional_path["priority_questions"]:
                    if question not in path_config["priority_questions"]:
                        path_config["priority_questions"].append(question)
                
                # Merge recommendations
                path_config["recommendations"].extend(additional_path["recommendations"])
                
                # Merge conversation flow
                for stage, questions in additional_path["conversation_flow"].items():
                    if stage not in path_config["conversation_flow"]:
                        path_config["conversation_flow"][stage] = []
                    path_config["conversation_flow"][stage].extend(questions)
        
        # Apply event type modifications
        if event_type:
            path_config = self._apply_event_type_modifiers(path_config, event_type)
        
        return path_config
    
    def _apply_event_type_modifiers(self, path_config: Dict[str, Any], event_type: str) -> Dict[str, Any]:
        """Apply event type specific modifications to the conversation path."""
        event_type_lower = event_type.lower()
        
        # Find matching event type modifier
        matching_modifier = None
        for event_key, modifier in self.event_type_modifiers.items():
            if event_key in event_type_lower or event_type_lower in event_key:
                matching_modifier = modifier
                break
        
        if not matching_modifier:
            return path_config
        
        # Add additional priority questions
        if "additional_priorities" in matching_modifier:
            for question in matching_modifier["additional_priorities"]:
                if question not in path_config["priority_questions"]:
                    path_config["priority_questions"].append(question)
        
        # Add conversation additions
        if "conversation_additions" in matching_modifier:
            for stage, questions in matching_modifier["conversation_additions"].items():
                if stage not in path_config["conversation_flow"]:
                    path_config["conversation_flow"][stage] = []
                path_config["conversation_flow"][stage].extend(questions)
        
        return path_config
    
    def _get_default_path(self) -> Dict[str, Any]:
        """Get default conversation path when no specific goals are identified."""
        return {
            "priority_questions": [
                "event_type",
                "event_goal", 
                "attendee_count",
                "event_date",
                "budget_range",
                "venue_type"
            ],
            "recommendations": [
                "professional_planning",
                "timeline_management",
                "vendor_coordination"
            ],
            "conversation_flow": {
                "discovery": [
                    "What type of event are you planning?",
                    "What's the main goal you want to achieve?",
                    "Who is your target audience?"
                ],
                "logistics": [
                    "When would you like to hold this event?",
                    "What's your budget range?",
                    "Where would you like to hold the event?"
                ]
            },
            "success_metrics": [
                "Event attendance",
                "Attendee satisfaction",
                "Goal achievement",
                "Budget adherence"
            ]
        }
    
    def get_next_question_for_path(self, path_config: Dict[str, Any], current_state: Dict[str, Any]) -> Optional[str]:
        """
        Get the next question based on the conversation path and current state.
        
        Args:
            path_config: Conversation path configuration
            current_state: Current conversation state
            
        Returns:
            Next question ID or None if path is complete
        """
        priority_questions = path_config.get("priority_questions", [])
        question_history = current_state.get("question_history", [])
        asked_question_ids = {q.get("id") for q in question_history if q.get("id")}
        
        # Find the next priority question that hasn't been asked
        for question_id in priority_questions:
            if question_id not in asked_question_ids:
                return question_id
        
        return None
    
    def get_conversation_stage_questions(self, path_config: Dict[str, Any], stage: str) -> List[str]:
        """
        Get questions for a specific conversation stage.
        
        Args:
            path_config: Conversation path configuration
            stage: Conversation stage (discovery, planning, logistics, etc.)
            
        Returns:
            List of questions for the stage
        """
        conversation_flow = path_config.get("conversation_flow", {})
        return conversation_flow.get(stage, [])
    
    def determine_conversation_stage(self, current_state: Dict[str, Any], path_config: Dict[str, Any]) -> str:
        """
        Determine the current conversation stage based on state and path.
        
        Args:
            current_state: Current conversation state
            path_config: Conversation path configuration
            
        Returns:
            Current conversation stage
        """
        question_history = current_state.get("question_history", [])
        event_details = current_state.get("event_details", {})
        
        # Count answered questions by category
        basic_questions_answered = sum(1 for q in question_history 
                                     if q.get("category") == "basic_details" and q.get("answered"))
        
        # Determine stage based on progress
        if basic_questions_answered < 2:
            return "discovery"
        elif not event_details.get("event_date") or not event_details.get("budget"):
            return "logistics"
        elif len(question_history) < 6:
            return "planning"
        else:
            return "finalization"
    
    def get_stage_recommendations(self, stage: str, path_config: Dict[str, Any]) -> List[str]:
        """
        Get recommendations specific to a conversation stage.
        
        Args:
            stage: Current conversation stage
            path_config: Conversation path configuration
            
        Returns:
            List of stage-specific recommendations
        """
        recommendations = path_config.get("recommendations", [])
        
        # Filter recommendations by stage
        stage_recommendations = {
            "discovery": recommendations[:2],  # First 2 recommendations
            "planning": recommendations[2:4] if len(recommendations) > 2 else recommendations,
            "logistics": recommendations[4:] if len(recommendations) > 4 else recommendations[-2:],
            "finalization": recommendations[-2:]  # Last 2 recommendations
        }
        
        return stage_recommendations.get(stage, recommendations[:2])
    
    def get_success_metrics(self, path_config: Dict[str, Any]) -> List[str]:
        """
        Get success metrics for the conversation path.
        
        Args:
            path_config: Conversation path configuration
            
        Returns:
            List of success metrics
        """
        return path_config.get("success_metrics", [])
    
    def is_path_complete(self, path_config: Dict[str, Any], current_state: Dict[str, Any]) -> bool:
        """
        Check if the conversation path is complete.
        
        Args:
            path_config: Conversation path configuration
            current_state: Current conversation state
            
        Returns:
            True if path is complete
        """
        priority_questions = path_config.get("priority_questions", [])
        question_history = current_state.get("question_history", [])
        answered_questions = {q.get("id") for q in question_history if q.get("answered")}
        
        # Check if all priority questions have been answered
        required_answered = sum(1 for q_id in priority_questions if q_id in answered_questions)
        
        # Path is complete if at least 80% of priority questions are answered
        completion_threshold = max(1, int(len(priority_questions) * 0.8))
        return required_answered >= completion_threshold
    
    def get_path_progress(self, path_config: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get progress information for the current conversation path.
        
        Args:
            path_config: Conversation path configuration
            current_state: Current conversation state
            
        Returns:
            Progress information including completion percentage and next steps
        """
        priority_questions = path_config.get("priority_questions", [])
        question_history = current_state.get("question_history", [])
        answered_questions = {q.get("id") for q in question_history if q.get("answered")}
        
        total_questions = len(priority_questions)
        answered_count = sum(1 for q_id in priority_questions if q_id in answered_questions)
        
        completion_percentage = (answered_count / total_questions * 100) if total_questions > 0 else 0
        
        # Get next steps
        remaining_questions = [q_id for q_id in priority_questions if q_id not in answered_questions]
        next_steps = remaining_questions[:3]  # Next 3 questions
        
        return {
            "completion_percentage": completion_percentage,
            "answered_count": answered_count,
            "total_questions": total_questions,
            "next_steps": next_steps,
            "current_stage": self.determine_conversation_stage(current_state, path_config),
            "is_complete": self.is_path_complete(path_config, current_state)
        }
