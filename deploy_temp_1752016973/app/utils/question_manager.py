"""
Question Management System for Conversational Agent

This module provides intelligent question management for the conversational event planning agent.
It handles question prioritization, follow-up generation, and information completeness assessment.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class QuestionManager:
    """
    Manages the question flow for conversational event planning.
    
    Handles question prioritization, follow-up generation, and tracks
    information completeness across different event planning categories.
    """
    
    def __init__(self):
        """Initialize the QuestionManager with question templates and logic."""
        self.question_templates = {
            "basic_details": [
                {
                    "id": "event_type",
                    "text": "What type of event are you planning? (e.g., conference, workshop, wedding, corporate meeting, etc.)",
                    "category": "basic_details",
                    "priority": 1,
                    "required": True,
                    "follow_up_triggers": ["corporate", "wedding", "conference", "workshop", "party"]
                },
                {
                    "id": "event_goal",
                    "text": "What's the main goal you want to achieve with this event?",
                    "category": "basic_details",
                    "priority": 2,
                    "required": True,
                    "follow_up_triggers": ["networking", "education", "celebration", "sales", "team building"]
                },
                {
                    "id": "attendee_count",
                    "text": "How many people do you expect to attend?",
                    "category": "basic_details",
                    "priority": 3,
                    "required": True,
                    "follow_up_triggers": ["small", "large", "intimate", "massive"]
                },
                {
                    "id": "event_title",
                    "text": "What would you like to call your event? (This helps us understand the tone and style)",
                    "category": "basic_details",
                    "priority": 4,
                    "required": False,
                    "follow_up_triggers": []
                }
            ],
            "timeline": [
                {
                    "id": "event_date",
                    "text": "When would you like to hold this event? (specific date or time range)",
                    "category": "timeline",
                    "priority": 1,
                    "required": True,
                    "follow_up_triggers": ["flexible", "fixed", "urgent", "soon"]
                },
                {
                    "id": "event_duration",
                    "text": "How long should the event last? (hours, days, etc.)",
                    "category": "timeline",
                    "priority": 2,
                    "required": True,
                    "follow_up_triggers": ["multi-day", "half-day", "full-day", "evening"]
                },
                {
                    "id": "planning_timeline",
                    "text": "How much time do you have for planning? When do you need everything finalized?",
                    "category": "timeline",
                    "priority": 3,
                    "required": False,
                    "follow_up_triggers": ["rush", "plenty", "tight", "flexible"]
                }
            ],
            "budget": [
                {
                    "id": "budget_range",
                    "text": "What's your budget range for this event? (This helps me recommend appropriate options)",
                    "category": "budget",
                    "priority": 1,
                    "required": True,
                    "follow_up_triggers": ["tight", "flexible", "unlimited", "corporate"]
                },
                {
                    "id": "budget_priorities",
                    "text": "What are your budget priorities? (e.g., venue, catering, entertainment, speakers)",
                    "category": "budget",
                    "priority": 2,
                    "required": False,
                    "follow_up_triggers": ["venue", "catering", "entertainment", "speakers"]
                }
            ],
            "location": [
                {
                    "id": "location_preference",
                    "text": "Where would you like to hold the event? (city, region, or specific venue preferences)",
                    "category": "location",
                    "priority": 1,
                    "required": True,
                    "follow_up_triggers": ["local", "destination", "specific", "flexible"]
                },
                {
                    "id": "venue_type",
                    "text": "What type of venue are you envisioning? (hotel, conference center, outdoor, unique venue, etc.)",
                    "category": "location",
                    "priority": 2,
                    "required": True,
                    "follow_up_triggers": ["hotel", "conference", "outdoor", "unique", "traditional"]
                },
                {
                    "id": "accessibility_needs",
                    "text": "Are there any accessibility requirements or special accommodations needed?",
                    "category": "location",
                    "priority": 3,
                    "required": False,
                    "follow_up_triggers": ["wheelchair", "hearing", "dietary", "special"]
                }
            ],
            "stakeholders": [
                {
                    "id": "key_stakeholders",
                    "text": "Who are the key stakeholders or decision-makers for this event?",
                    "category": "stakeholders",
                    "priority": 1,
                    "required": False,
                    "follow_up_triggers": ["executives", "board", "committee", "family"]
                },
                {
                    "id": "speakers_needed",
                    "text": "Do you need speakers, presenters, or special guests for your event?",
                    "category": "stakeholders",
                    "priority": 2,
                    "required": False,
                    "follow_up_triggers": ["keynote", "panel", "workshop", "celebrity"]
                },
                {
                    "id": "sponsors_needed",
                    "text": "Are you looking for sponsors or partners for this event?",
                    "category": "stakeholders",
                    "priority": 3,
                    "required": False,
                    "follow_up_triggers": ["corporate", "local", "industry", "media"]
                }
            ],
            "resources": [
                {
                    "id": "catering_needs",
                    "text": "What are your catering needs? (meals, snacks, dietary restrictions, etc.)",
                    "category": "resources",
                    "priority": 1,
                    "required": False,
                    "follow_up_triggers": ["formal", "casual", "dietary", "alcohol"]
                },
                {
                    "id": "av_equipment",
                    "text": "What audio/visual equipment will you need? (projectors, microphones, lighting, etc.)",
                    "category": "resources",
                    "priority": 2,
                    "required": False,
                    "follow_up_triggers": ["presentation", "music", "lighting", "recording"]
                },
                {
                    "id": "transportation",
                    "text": "Do you need transportation arrangements for attendees? (shuttles, parking, etc.)",
                    "category": "resources",
                    "priority": 3,
                    "required": False,
                    "follow_up_triggers": ["shuttle", "parking", "airport", "hotel"]
                }
            ],
            "success_criteria": [
                {
                    "id": "success_metrics",
                    "text": "How will you measure the success of this event? What are your key objectives?",
                    "category": "success_criteria",
                    "priority": 1,
                    "required": False,
                    "follow_up_triggers": ["attendance", "satisfaction", "leads", "revenue"]
                },
                {
                    "id": "must_have_elements",
                    "text": "What are the absolute must-have elements for your event to be successful?",
                    "category": "success_criteria",
                    "priority": 2,
                    "required": False,
                    "follow_up_triggers": ["networking", "education", "entertainment", "branding"]
                }
            ],
            "risks": [
                {
                    "id": "potential_challenges",
                    "text": "Are there any potential challenges or concerns you're worried about?",
                    "category": "risks",
                    "priority": 1,
                    "required": False,
                    "follow_up_triggers": ["weather", "attendance", "budget", "logistics"]
                },
                {
                    "id": "backup_plans",
                    "text": "Do you need backup plans for any aspects of the event? (weather, venue, etc.)",
                    "category": "risks",
                    "priority": 2,
                    "required": False,
                    "follow_up_triggers": ["outdoor", "weather", "venue", "speaker"]
                }
            ]
        }
        
        # Define question flow priorities - which categories to ask first
        self.category_priority = [
            "basic_details",
            "timeline", 
            "budget",
            "location",
            "stakeholders",
            "resources",
            "success_criteria",
            "risks"
        ]
        
        # Define follow-up question templates
        self.follow_up_templates = {
            "event_type": {
                "corporate": "What's the business objective for this corporate event? (team building, client relations, product launch, etc.)",
                "wedding": "What's your vision for the wedding style? (traditional, modern, destination, intimate, etc.)",
                "conference": "What's the main theme or focus of your conference? What industry or topic?",
                "workshop": "What skills or knowledge will participants gain from this workshop?",
                "party": "What's the occasion for this celebration? (birthday, anniversary, holiday, etc.)"
            },
            "attendee_count": {
                "small": "For an intimate gathering like this, are you looking for a more personal, interactive experience?",
                "large": "With a large group, how important is networking and interaction between attendees?",
                "corporate": "Will all attendees be from your organization, or will there be external guests?"
            },
            "event_date": {
                "flexible": "What time of year works best? Are there any dates or seasons to avoid?",
                "urgent": "Given the tight timeline, what aspects of the event are most critical to get right?",
                "seasonal": "Are there any seasonal considerations that might affect your event?"
            },
            "budget_range": {
                "tight": "Let's focus on the most impactful elements. What's absolutely essential for your event?",
                "corporate": "Is this budget approved, or do we need to prepare a business case for additional funding?",
                "flexible": "Are there any premium elements you'd like to consider if budget allows?"
            },
            "location_preference": {
                "destination": "Will you be providing travel assistance for attendees? How will this affect your budget?",
                "local": "Do you have any preferred venues in the area, or would you like recommendations?",
                "flexible": "Are you open to unique or non-traditional venues that might offer better value?"
            }
        }
    
    def get_next_question(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Determine the next best question to ask based on current state.
        
        Args:
            state: Current conversation state
            
        Returns:
            Next question dictionary or None if no more questions needed
        """
        # Get questions already asked
        asked_questions = {q.get("id") for q in state.get("question_history", [])}
        
        # Find the next question to ask based on priority and completeness
        for category in self.category_priority:
            category_questions = self.question_templates.get(category, [])
            
            # Sort questions by priority within category
            sorted_questions = sorted(category_questions, key=lambda x: x.get("priority", 999))
            
            for question in sorted_questions:
                question_id = question.get("id")
                
                # Skip if already asked
                if question_id in asked_questions:
                    continue
                
                # Check if this is a required question or if we should ask it
                if question.get("required", False) or self._should_ask_question(question, state):
                    # Create a copy of the question with timestamp
                    next_question = question.copy()
                    next_question["asked_at"] = datetime.utcnow().isoformat()
                    next_question["answered"] = False
                    
                    return next_question
        
        # No more questions to ask
        return None
    
    def _should_ask_question(self, question: Dict[str, Any], state: Dict[str, Any]) -> bool:
        """
        Determine if a non-required question should be asked based on context.
        
        Args:
            question: Question to evaluate
            state: Current conversation state
            
        Returns:
            True if question should be asked
        """
        # Always ask required questions
        if question.get("required", False):
            return True
        
        # For optional questions, use some logic to determine relevance
        question_id = question.get("id")
        category = question.get("category")
        
        # Check if we have enough basic information to ask more detailed questions
        basic_completeness = state.get("information_completeness", {}).get("basic_details", 0.0)
        
        # Don't ask detailed questions until we have basic info
        if basic_completeness < 0.5 and category != "basic_details":
            return False
        
        # Ask stakeholder questions for larger events
        if category == "stakeholders":
            attendee_count = state.get("event_details", {}).get("attendee_count")
            if attendee_count and attendee_count > 50:
                return True
        
        # Ask resource questions based on event type
        if category == "resources":
            event_type = state.get("event_details", {}).get("event_type", "").lower()
            if any(keyword in event_type for keyword in ["conference", "workshop", "corporate", "wedding"]):
                return True
        
        # Ask success criteria for business events
        if category == "success_criteria":
            event_type = state.get("event_details", {}).get("event_type", "").lower()
            user_goals = state.get("user_goals", [])
            if any(keyword in event_type for keyword in ["corporate", "conference", "business"]) or \
               any(goal in user_goals for goal in ["lead_generation", "networking", "education"]):
                return True
        
        # Ask risk questions for outdoor or large events
        if category == "risks":
            event_type = state.get("event_details", {}).get("event_type", "").lower()
            attendee_count = state.get("event_details", {}).get("attendee_count", 0)
            venue_type = state.get("requirements", {}).get("location", {}).get("venue_type", "").lower()
            
            if "outdoor" in event_type or "outdoor" in venue_type or attendee_count > 100:
                return True
        
        # Default to asking the question if we're not sure
        return True
    
    def generate_follow_up(self, answer: str, category: str, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate a smart follow-up question based on the user's answer.
        
        Args:
            answer: User's answer to the previous question
            category: Category of the previous question
            question_id: ID of the previous question
            
        Returns:
            Follow-up question dictionary or None
        """
        answer_lower = answer.lower()
        
        # Check if we have follow-up templates for this question
        if question_id in self.follow_up_templates:
            templates = self.follow_up_templates[question_id]
            
            # Look for trigger words in the answer
            for trigger, follow_up_text in templates.items():
                if trigger in answer_lower:
                    return {
                        "id": f"{question_id}_followup_{trigger}",
                        "text": follow_up_text,
                        "category": category,
                        "priority": 999,  # Follow-ups have lower priority
                        "required": False,
                        "is_follow_up": True,
                        "parent_question": question_id,
                        "asked_at": datetime.utcnow().isoformat(),
                        "answered": False
                    }
        
        # Generate smart contextual follow-ups based on answer content
        follow_up = self._generate_smart_follow_up(answer, category, question_id)
        if follow_up:
            return follow_up
        
        # No follow-up needed
        return None
    
    def _generate_smart_follow_up(self, answer: str, category: str, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate intelligent follow-up questions using advanced analysis.
        
        Args:
            answer: User's answer to analyze
            category: Category of the previous question
            question_id: ID of the previous question
            
        Returns:
            Smart follow-up question or None
        """
        answer_lower = answer.lower()
        
        # Attendee count analysis
        if question_id == "attendee_count":
            numbers = re.findall(r'\d+', answer)
            if numbers:
                count = int(numbers[0])
                
                # Very large events (500+)
                if count > 500:
                    return self._create_follow_up(
                        question_id, "large_event_logistics", category,
                        "With such a large event, logistics become critical. Do you have experience managing events of this size, or would you like recommendations for professional event management support?"
                    )
                
                # Large events (200-500)
                elif count > 200:
                    return self._create_follow_up(
                        question_id, "large_event_planning", category,
                        "For an event of this size, we'll need to plan for crowd management and multiple service stations. Have you considered how attendees will register and check in?"
                    )
                
                # Medium events (50-200)
                elif count >= 50:
                    return self._create_follow_up(
                        question_id, "medium_event_format", category,
                        "With this group size, you have flexibility in format. Are you planning for everyone to be together, or would you like breakout sessions or smaller group activities?"
                    )
                
                # Small events (20-50)
                elif count >= 20:
                    return self._create_follow_up(
                        question_id, "small_event_interaction", category,
                        "This size is perfect for interactive experiences. How important is it that attendees get to know each other personally?"
                    )
                
                # Intimate events (<20)
                else:
                    return self._create_follow_up(
                        question_id, "intimate_event_style", category,
                        "For an intimate gathering like this, you have great flexibility in venue and format. Are you looking for something more formal or casual?"
                    )
        
        # Budget analysis
        elif question_id == "budget_range":
            # Budget concerns
            if any(word in answer_lower for word in ["tight", "limited", "small", "low", "minimal", "cheap"]):
                return self._create_follow_up(
                    question_id, "budget_optimization", category,
                    "I understand budget is a concern. Would you like me to focus on cost-effective solutions and identify areas where we can maximize impact while minimizing expense?"
                )
            
            # High budget indicators
            elif any(word in answer_lower for word in ["unlimited", "generous", "flexible", "premium", "luxury"]):
                return self._create_follow_up(
                    question_id, "premium_options", category,
                    "With a flexible budget, we can explore premium options. What aspects of the event are most important to invest in for maximum impact?"
                )
            
            # Specific budget mentioned
            elif re.search(r'\$[\d,]+', answer) or re.search(r'\d+k', answer_lower):
                return self._create_follow_up(
                    question_id, "budget_allocation", category,
                    "Thanks for the budget range. What are your priorities for budget allocation? For example, is it more important to invest in the venue, speakers, catering, or marketing?"
                )
        
        # Timeline analysis
        elif question_id == "event_date":
            # Urgency indicators
            if any(word in answer_lower for word in ["soon", "urgent", "asap", "quickly", "rush", "immediate"]):
                return self._create_follow_up(
                    question_id, "urgent_planning", category,
                    "Given the urgent timeline, we'll need to prioritize the most critical elements first. What aspects of the event are absolutely non-negotiable?"
                )
            
            # Flexibility indicators
            elif any(word in answer_lower for word in ["flexible", "anytime", "whenever", "open"]):
                return self._create_follow_up(
                    question_id, "optimal_timing", category,
                    "Since you have flexibility with timing, would you like me to recommend optimal dates based on your event type and target audience?"
                )
            
            # Seasonal mentions
            elif any(season in answer_lower for season in ["spring", "summer", "fall", "autumn", "winter"]):
                season = next(s for s in ["spring", "summer", "fall", "autumn", "winter"] if s in answer_lower)
                return self._create_follow_up(
                    question_id, f"seasonal_{season}", category,
                    f"Great choice for {season}! Are there any specific considerations for {season} events that are important to you, such as weather contingencies or seasonal themes?"
                )
        
        # Event type analysis
        elif question_id == "event_type":
            # Corporate events
            if any(word in answer_lower for word in ["corporate", "business", "company", "professional", "work"]):
                return self._create_follow_up(
                    question_id, "corporate_objectives", category,
                    "For corporate events, it's important to align with business objectives. What specific business goals do you hope to achieve with this event?"
                )
            
            # Social events
            elif any(word in answer_lower for word in ["wedding", "party", "celebration", "birthday", "anniversary"]):
                return self._create_follow_up(
                    question_id, "celebration_style", category,
                    "Celebrations are special! What kind of atmosphere are you hoping to create? More formal and elegant, or casual and fun?"
                )
            
            # Educational events
            elif any(word in answer_lower for word in ["conference", "workshop", "seminar", "training", "education"]):
                return self._create_follow_up(
                    question_id, "learning_objectives", category,
                    "Educational events are most successful when they have clear learning objectives. What specific knowledge or skills should attendees gain?"
                )
            
            # Networking events
            elif any(word in answer_lower for word in ["networking", "mixer", "meetup", "connect"]):
                return self._create_follow_up(
                    question_id, "networking_goals", category,
                    "Networking events work best with clear connection goals. What types of connections are you hoping attendees will make?"
                )
        
        # Location analysis
        elif question_id == "location_preference":
            # Destination events
            if any(word in answer_lower for word in ["destination", "travel", "resort", "retreat", "away"]):
                return self._create_follow_up(
                    question_id, "destination_logistics", category,
                    "Destination events can be very impactful! Will you be providing travel assistance or accommodation recommendations for attendees?"
                )
            
            # Local events
            elif any(word in answer_lower for word in ["local", "nearby", "here", "close", "convenient"]):
                return self._create_follow_up(
                    question_id, "local_advantages", category,
                    "Local events have great advantages for attendance. Are there any specific local venues or areas you'd prefer, or should I recommend options based on your other requirements?"
                )
            
            # Outdoor preferences
            elif any(word in answer_lower for word in ["outdoor", "outside", "garden", "park", "beach"]):
                return self._create_follow_up(
                    question_id, "outdoor_contingency", category,
                    "Outdoor events can be wonderful! What's your plan for weather contingencies? Should we also consider indoor backup options?"
                )
        
        # Venue type analysis
        elif question_id == "venue_type":
            # Unique venues
            if any(word in answer_lower for word in ["unique", "unusual", "different", "special", "memorable"]):
                return self._create_follow_up(
                    question_id, "unique_venue_requirements", category,
                    "Unique venues create memorable experiences! Are there any specific requirements or limitations we should consider for non-traditional venues?"
                )
            
            # Traditional venues
            elif any(word in answer_lower for word in ["hotel", "conference", "traditional", "standard", "conventional"]):
                return self._create_follow_up(
                    question_id, "traditional_venue_priorities", category,
                    "Traditional venues offer reliability and full services. What amenities are most important to you - catering capabilities, AV equipment, parking, or something else?"
                )
        
        # Goal analysis
        elif question_id == "event_goal":
            # Multiple goals mentioned
            goal_keywords = ["network", "learn", "celebrate", "launch", "train", "connect", "promote", "sell"]
            mentioned_goals = [goal for goal in goal_keywords if goal in answer_lower]
            
            if len(mentioned_goals) > 1:
                return self._create_follow_up(
                    question_id, "goal_prioritization", category,
                    "I can see you have multiple objectives for this event. Which goal is most important to you, as this will help me prioritize recommendations?"
                )
            
            # Vague goals
            elif any(word in answer_lower for word in ["fun", "good", "successful", "nice", "great"]):
                return self._create_follow_up(
                    question_id, "goal_clarification", category,
                    "I'd love to help make your event successful! Could you be more specific about what success looks like? For example, are you hoping for strong attendance, positive feedback, business outcomes, or something else?"
                )
        
        return None
    
    def _create_follow_up(self, parent_question_id: str, follow_up_id: str, category: str, text: str) -> Dict[str, Any]:
        """
        Create a follow-up question dictionary.
        
        Args:
            parent_question_id: ID of the parent question
            follow_up_id: ID for the follow-up question
            category: Category of the question
            text: Question text
            
        Returns:
            Follow-up question dictionary
        """
        return {
            "id": f"{parent_question_id}_followup_{follow_up_id}",
            "text": text,
            "category": category,
            "priority": 999,  # Follow-ups have lower priority
            "required": False,
            "is_follow_up": True,
            "parent_question": parent_question_id,
            "asked_at": datetime.utcnow().isoformat(),
            "answered": False
        }
    
    def assess_completeness(self, state: Dict[str, Any]) -> Dict[str, float]:
        """
        Assess how complete each information category is (0.0 to 1.0).
        
        Args:
            state: Current conversation state
            
        Returns:
            Dictionary mapping categories to completeness scores
        """
        completeness = {}
        asked_questions = {q.get("id"): q for q in state.get("question_history", [])}
        
        for category in self.category_priority:
            category_questions = self.question_templates.get(category, [])
            
            if not category_questions:
                completeness[category] = 1.0
                continue
            
            # Calculate completeness based on answered questions
            total_questions = len(category_questions)
            required_questions = [q for q in category_questions if q.get("required", False)]
            answered_questions = []
            answered_required = []
            
            for question in category_questions:
                question_id = question.get("id")
                if question_id in asked_questions and asked_questions[question_id].get("answered", False):
                    answered_questions.append(question)
                    if question.get("required", False):
                        answered_required.append(question)
            
            # Calculate score based on required vs optional questions
            if required_questions:
                # If there are required questions, they must be answered for high completeness
                required_score = len(answered_required) / len(required_questions)
                optional_questions = [q for q in category_questions if not q.get("required", False)]
                
                if optional_questions:
                    answered_optional = [q for q in answered_questions if not q.get("required", False)]
                    optional_score = len(answered_optional) / len(optional_questions)
                    # Weight required questions more heavily
                    completeness[category] = (required_score * 0.7) + (optional_score * 0.3)
                else:
                    completeness[category] = required_score
            else:
                # No required questions, base on total answered
                completeness[category] = len(answered_questions) / total_questions if total_questions > 0 else 1.0
        
        return completeness
    
    def is_information_sufficient_for_proposal(self, state: Dict[str, Any]) -> bool:
        """
        Determine if we have sufficient information to generate a proposal.
        
        Args:
            state: Current conversation state
            
        Returns:
            True if sufficient information is available
        """
        completeness = self.assess_completeness(state)
        
        # Check if we have the minimum required information
        required_categories = ["basic_details", "timeline", "budget", "location"]
        
        for category in required_categories:
            if completeness.get(category, 0.0) < 0.7:  # 70% threshold
                return False
        
        # Also check that we have meaningful event details
        event_details = state.get("event_details", {})
        
        # Must have event type and some timeline info
        if not event_details.get("event_type") or not (
            event_details.get("timeline_start") or event_details.get("timeline_end")
        ):
            return False
        
        # Must have some budget information
        budget_info = state.get("requirements", {}).get("budget", {})
        if not budget_info:
            return False
        
        return True
    
    def get_question_recommendations(self, question: Dict[str, Any], state: Dict[str, Any]) -> str:
        """
        Get contextual recommendations for a specific question.
        
        Args:
            question: The question being asked
            state: Current conversation state
            
        Returns:
            Recommendation text
        """
        question_id = question.get("id")
        category = question.get("category")
        
        # Event type recommendations
        if question_id == "event_type":
            return "Popular event types include corporate conferences, workshops, product launches, team building retreats, and networking events. Each has different requirements and best practices."
        
        # Attendee count recommendations
        elif question_id == "attendee_count":
            return "Consider that 10-15% of invited guests typically don't attend. For networking events, 50-150 people works well. For workshops, 20-30 is optimal for interaction."
        
        # Timeline recommendations
        elif question_id == "event_date":
            event_type = state.get("event_details", {}).get("event_type", "").lower()
            if "corporate" in event_type or "business" in event_type:
                return "Tuesday-Thursday are typically best for business events. Avoid major holidays and industry conference dates."
            else:
                return "Consider your target audience's schedule and any competing events. Weekend events work well for social gatherings."
        
        # Budget recommendations
        elif question_id == "budget_range":
            return "A typical breakdown: 40% venue & catering, 20% speakers/entertainment, 15% marketing, 10% AV/tech, 15% miscellaneous. Always include a 10-15% contingency."
        
        # Location recommendations
        elif question_id == "venue_type":
            attendee_count = state.get("event_details", {}).get("attendee_count", 0)
            if attendee_count > 200:
                return "For large events, consider convention centers or hotels with multiple breakout rooms. Ensure adequate parking and accessibility."
            elif attendee_count < 50:
                return "Smaller venues like boutique hotels, restaurants with private rooms, or unique spaces can create more intimate experiences."
            else:
                return "Mid-size venues like hotel conference rooms, corporate event spaces, or community centers offer good flexibility and value."
        
        # Default recommendations by category
        elif category == "stakeholders":
            return "Key stakeholders should be involved early in planning. Consider their availability, preferences, and any special requirements."
        
        elif category == "resources":
            return "Plan resources based on your event goals. Interactive events need more AV equipment, while networking events focus on space layout and catering."
        
        elif category == "success_criteria":
            return "Clear success metrics help guide all planning decisions. Common metrics include attendance rate, satisfaction scores, lead generation, and ROI."
        
        elif category == "risks":
            return "Common event risks include weather (for outdoor events), low attendance, speaker cancellations, and technical issues. Having backup plans is essential."
        
        return ""
