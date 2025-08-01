"""
Proactive Suggestion System for Conversational Agent
Provides contextual suggestions and proactive recommendations during conversations.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re


class ProactiveSuggestionEngine:
    """
    Generates proactive suggestions based on conversation context, user responses,
    and event planning best practices. Provides timely recommendations to enhance
    the planning process.
    """
    
    def __init__(self):
        """Initialize the proactive suggestion engine with triggers and templates."""
        
        # Suggestion triggers based on user responses
        self.response_triggers = {
            "budget_concerns": {
                "keywords": ["tight", "limited", "small", "low", "budget", "cheap", "affordable", "cost"],
                "suggestions": [
                    "Consider hosting during off-peak times for better venue rates",
                    "Partner with local businesses for sponsorship opportunities",
                    "Focus your budget on elements that directly impact your main goal",
                    "Look into venues that include AV equipment to reduce rental costs"
                ],
                "confidence": 0.8
            },
            "large_event_concerns": {
                "keywords": ["500", "1000", "large", "big", "huge", "massive", "many people"],
                "suggestions": [
                    "Consider professional event management for events over 500 people",
                    "Plan for 15-20% no-show rate with large events",
                    "Multiple registration waves can help manage capacity",
                    "Ensure your venue has adequate parking and accessibility"
                ],
                "confidence": 0.9
            },
            "time_pressure": {
                "keywords": ["soon", "quickly", "urgent", "asap", "rush", "short notice", "weeks", "month"],
                "suggestions": [
                    "Focus on venues with immediate availability",
                    "Consider digital invitations to save time on printing",
                    "Prioritize vendors who can deliver on short timelines",
                    "Simple catering options can be arranged more quickly"
                ],
                "confidence": 0.85
            },
            "first_time_planner": {
                "keywords": ["first time", "never done", "new to", "don't know", "not sure", "help"],
                "suggestions": [
                    "Start with a detailed timeline working backwards from your event date",
                    "Consider hiring a day-of coordinator even if you plan everything yourself",
                    "Create a master checklist to track all planning elements",
                    "Book your venue and catering first as these have the biggest impact"
                ],
                "confidence": 0.9
            },
            "outdoor_event": {
                "keywords": ["outdoor", "outside", "garden", "park", "beach", "patio", "rooftop"],
                "suggestions": [
                    "Always have a weather backup plan for outdoor events",
                    "Consider tent rentals for shade and weather protection",
                    "Plan for additional restroom facilities if needed",
                    "Check permit requirements for outdoor venues"
                ],
                "confidence": 0.95
            },
            "networking_focus": {
                "keywords": ["networking", "connections", "meet people", "business cards", "contacts"],
                "suggestions": [
                    "Standing reception format encourages more mingling than seated dinner",
                    "Name tags with company/role help facilitate introductions",
                    "Consider a networking app for easy contact exchange",
                    "Plan 60-90 minutes minimum for meaningful networking"
                ],
                "confidence": 0.9
            },
            "corporate_event": {
                "keywords": ["corporate", "company", "business", "professional", "work", "office"],
                "suggestions": [
                    "Tuesday-Thursday typically have the best attendance for business events",
                    "Include your company branding subtly throughout the event",
                    "Plan for dietary restrictions common in professional settings",
                    "Consider live streaming for remote team members"
                ],
                "confidence": 0.85
            },
            "wedding_planning": {
                "keywords": ["wedding", "bride", "groom", "marriage", "ceremony", "reception"],
                "suggestions": [
                    "Book your photographer and venue first as they're hardest to change",
                    "Consider Friday or Sunday for better pricing than Saturday",
                    "Plan for 5-10% guest declines when setting final headcount",
                    "Create a wedding website for easy guest communication"
                ],
                "confidence": 0.9
            }
        }
        
        # Context-based suggestion triggers
        self.context_triggers = {
            "venue_selection": {
                "suggestions": [
                    "Visit venues in person before making final decisions",
                    "Ask about included amenities to avoid surprise costs",
                    "Check the venue's cancellation and weather policies",
                    "Ensure the venue matches your event's style and atmosphere"
                ],
                "timing": "when_discussing_venue"
            },
            "catering_planning": {
                "suggestions": [
                    "Buffet style is often more cost-effective than plated meals",
                    "Always plan for dietary restrictions and allergies",
                    "Consider the timing of your event when planning the menu",
                    "Ask for a tasting before finalizing your catering choice"
                ],
                "timing": "when_discussing_food"
            },
            "timeline_planning": {
                "suggestions": [
                    "Send save-the-dates 6-8 weeks before the event",
                    "Confirm final headcount one week prior",
                    "Plan setup to begin 2-3 hours before guest arrival",
                    "Build buffer time into your schedule for unexpected delays"
                ],
                "timing": "when_discussing_dates"
            },
            "budget_allocation": {
                "suggestions": [
                    "Allocate 10-15% of your budget for unexpected expenses",
                    "Get quotes from multiple vendors before making decisions",
                    "Consider which elements are most important to your goals",
                    "Track expenses throughout the planning process"
                ],
                "timing": "when_discussing_budget"
            }
        }
        
        # Proactive recommendations based on event progress
        self.progress_triggers = {
            "early_stage": {
                "condition": "less_than_3_questions_answered",
                "suggestions": [
                    "Let's start by clarifying your main goal - this will guide all our other decisions",
                    "Understanding your target audience will help us choose the right format and venue",
                    "Having a rough timeline helps prioritize which decisions need to be made first"
                ]
            },
            "mid_stage": {
                "condition": "3_to_6_questions_answered",
                "suggestions": [
                    "Now that we have your basics, let's think about the experience you want to create",
                    "Consider what will make your event memorable and different from others",
                    "Think about how you'll measure success - this helps with planning decisions"
                ]
            },
            "late_stage": {
                "condition": "more_than_6_questions_answered",
                "suggestions": [
                    "We're making great progress! Let's focus on the details that will ensure smooth execution",
                    "Consider creating a day-of timeline to coordinate all the moving pieces",
                    "Think about contingency plans for your most critical elements"
                ]
            }
        }
        
        # Seasonal and timing-based suggestions
        self.seasonal_suggestions = {
            "spring": [
                "Spring is wedding season - book venues early for May-June dates",
                "Consider outdoor options as weather becomes more predictable",
                "Spring themes work well for corporate events and product launches"
            ],
            "summer": [
                "Summer events work great outdoors but plan for heat management",
                "Many people travel in summer - send invitations extra early",
                "Consider morning or evening events to avoid peak heat"
            ],
            "fall": [
                "Fall is peak season for corporate events and conferences",
                "Beautiful season for outdoor events with natural decorations",
                "Holiday season approaches - avoid conflicts with major holidays"
            ],
            "winter": [
                "Indoor venues are essential - book early for holiday season",
                "Consider weather delays in your planning timeline",
                "Holiday themes can add warmth to winter events"
            ]
        }
    
    def get_proactive_suggestions(self, user_response: str, context: str, 
                                current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get proactive suggestions based on user response and context.
        
        Args:
            user_response: User's latest response
            context: Current conversation context
            current_state: Current conversation state
            
        Returns:
            List of suggestion dictionaries with text and confidence scores
        """
        suggestions = []
        
        # Get response-triggered suggestions
        response_suggestions = self._get_response_triggered_suggestions(user_response)
        suggestions.extend(response_suggestions)
        
        # Get context-triggered suggestions
        context_suggestions = self._get_context_triggered_suggestions(context, current_state)
        suggestions.extend(context_suggestions)
        
        # Get progress-triggered suggestions
        progress_suggestions = self._get_progress_triggered_suggestions(current_state)
        suggestions.extend(progress_suggestions)
        
        # Get seasonal suggestions if relevant
        seasonal_suggestions = self._get_seasonal_suggestions(current_state)
        suggestions.extend(seasonal_suggestions)
        
        # Remove duplicates and sort by confidence
        unique_suggestions = self._deduplicate_suggestions(suggestions)
        sorted_suggestions = sorted(unique_suggestions, key=lambda x: x.get("confidence", 0.5), reverse=True)
        
        # Return top 3 suggestions
        return sorted_suggestions[:3]
    
    def _get_response_triggered_suggestions(self, user_response: str) -> List[Dict[str, Any]]:
        """Get suggestions triggered by keywords in user response."""
        suggestions = []
        response_lower = user_response.lower()
        
        for trigger_name, trigger_config in self.response_triggers.items():
            keywords = trigger_config["keywords"]
            
            # Check if any keywords match
            if any(keyword in response_lower for keyword in keywords):
                for suggestion_text in trigger_config["suggestions"]:
                    suggestions.append({
                        "text": suggestion_text,
                        "confidence": trigger_config["confidence"],
                        "trigger": trigger_name,
                        "type": "response_triggered"
                    })
        
        return suggestions
    
    def _get_context_triggered_suggestions(self, context: str, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suggestions based on current conversation context."""
        suggestions = []
        
        # Map context to trigger categories
        context_mapping = {
            "venue_type": "venue_selection",
            "location": "venue_selection",
            "catering_needs": "catering_planning",
            "event_date": "timeline_planning",
            "timeline": "timeline_planning",
            "budget_range": "budget_allocation",
            "budget": "budget_allocation"
        }
        
        trigger_category = context_mapping.get(context)
        if trigger_category and trigger_category in self.context_triggers:
            trigger_config = self.context_triggers[trigger_category]
            
            for suggestion_text in trigger_config["suggestions"]:
                suggestions.append({
                    "text": suggestion_text,
                    "confidence": 0.7,
                    "trigger": trigger_category,
                    "type": "context_triggered"
                })
        
        return suggestions
    
    def _get_progress_triggered_suggestions(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suggestions based on conversation progress."""
        suggestions = []
        question_history = current_state.get("question_history", [])
        answered_count = sum(1 for q in question_history if q.get("answered", False))
        
        # Determine progress stage
        if answered_count < 3:
            stage = "early_stage"
        elif answered_count <= 6:
            stage = "mid_stage"
        else:
            stage = "late_stage"
        
        if stage in self.progress_triggers:
            trigger_config = self.progress_triggers[stage]
            
            for suggestion_text in trigger_config["suggestions"]:
                suggestions.append({
                    "text": suggestion_text,
                    "confidence": 0.6,
                    "trigger": stage,
                    "type": "progress_triggered"
                })
        
        return suggestions
    
    def _get_seasonal_suggestions(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get seasonal suggestions based on event timing."""
        suggestions = []
        event_details = current_state.get("event_details", {})
        
        # Try to extract season from event date
        event_date_str = event_details.get("timeline_start") or event_details.get("event_date")
        if event_date_str:
            season = self._determine_season(event_date_str)
            if season and season in self.seasonal_suggestions:
                for suggestion_text in self.seasonal_suggestions[season]:
                    suggestions.append({
                        "text": suggestion_text,
                        "confidence": 0.5,
                        "trigger": f"seasonal_{season}",
                        "type": "seasonal"
                    })
        
        return suggestions
    
    def _determine_season(self, date_str: str) -> Optional[str]:
        """Determine season from date string."""
        try:
            # Try to extract month from various date formats
            month_patterns = [
                r'\b(january|jan)\b',
                r'\b(february|feb)\b', 
                r'\b(march|mar)\b',
                r'\b(april|apr)\b',
                r'\b(may)\b',
                r'\b(june|jun)\b',
                r'\b(july|jul)\b',
                r'\b(august|aug)\b',
                r'\b(september|sep)\b',
                r'\b(october|oct)\b',
                r'\b(november|nov)\b',
                r'\b(december|dec)\b'
            ]
            
            date_lower = date_str.lower()
            
            for i, pattern in enumerate(month_patterns):
                if re.search(pattern, date_lower):
                    month = i + 1
                    if month in [12, 1, 2]:
                        return "winter"
                    elif month in [3, 4, 5]:
                        return "spring"
                    elif month in [6, 7, 8]:
                        return "summer"
                    elif month in [9, 10, 11]:
                        return "fall"
            
            # Try numeric date formats
            numeric_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', date_str)
            if numeric_match:
                month = int(numeric_match.group(1))
                if 1 <= month <= 12:
                    if month in [12, 1, 2]:
                        return "winter"
                    elif month in [3, 4, 5]:
                        return "spring"
                    elif month in [6, 7, 8]:
                        return "summer"
                    elif month in [9, 10, 11]:
                        return "fall"
        
        except:
            pass
        
        return None
    
    def _deduplicate_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate suggestions while preserving highest confidence."""
        seen_texts = {}
        unique_suggestions = []
        
        for suggestion in suggestions:
            text = suggestion["text"]
            confidence = suggestion.get("confidence", 0.5)
            
            if text not in seen_texts or confidence > seen_texts[text]["confidence"]:
                seen_texts[text] = suggestion
        
        return list(seen_texts.values())
    
    def get_suggestion_confidence(self, suggestion_text: str, context: str, 
                                user_response: str) -> float:
        """
        Calculate confidence score for a specific suggestion.
        
        Args:
            suggestion_text: The suggestion text
            context: Current conversation context
            user_response: User's latest response
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.5
        
        # Increase confidence based on context relevance
        context_keywords = {
            "venue": ["venue", "location", "space", "place"],
            "budget": ["budget", "cost", "price", "money", "expensive"],
            "timing": ["date", "time", "when", "schedule"],
            "catering": ["food", "catering", "meal", "dining", "eat"]
        }
        
        suggestion_lower = suggestion_text.lower()
        response_lower = user_response.lower()
        
        for category, keywords in context_keywords.items():
            if any(keyword in suggestion_lower for keyword in keywords):
                if any(keyword in response_lower for keyword in keywords):
                    base_confidence += 0.2
                if category in context.lower():
                    base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def should_suggest_now(self, current_state: Dict[str, Any], last_suggestion_time: Optional[datetime] = None) -> bool:
        """
        Determine if it's appropriate to provide suggestions now.
        
        Args:
            current_state: Current conversation state
            last_suggestion_time: When suggestions were last provided
            
        Returns:
            True if suggestions should be provided
        """
        # Don't suggest too frequently
        if last_suggestion_time:
            time_since_last = datetime.now() - last_suggestion_time
            if time_since_last < timedelta(minutes=2):
                return False
        
        # Suggest after user provides substantial response
        messages = current_state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if last_message.get("role") == "user":
                content = last_message.get("content", "")
                # Suggest if response is substantial (more than 10 words)
                if len(content.split()) > 10:
                    return True
        
        # Suggest at key conversation milestones
        question_history = current_state.get("question_history", [])
        answered_count = sum(1 for q in question_history if q.get("answered", False))
        
        # Suggest at milestones: 2, 5, 8 questions answered
        if answered_count in [2, 5, 8]:
            return True
        
        return False
    
    def format_suggestions_for_display(self, suggestions: List[Dict[str, Any]], 
                                     max_suggestions: int = 3) -> str:
        """
        Format suggestions for display in conversation.
        
        Args:
            suggestions: List of suggestion dictionaries
            max_suggestions: Maximum number of suggestions to display
            
        Returns:
            Formatted suggestion text
        """
        if not suggestions:
            return ""
        
        # Take top suggestions
        top_suggestions = suggestions[:max_suggestions]
        
        # Format as bullet points
        formatted_suggestions = []
        for suggestion in top_suggestions:
            text = suggestion["text"]
            confidence = suggestion.get("confidence", 0.5)
            
            # Add confidence indicator for high-confidence suggestions
            if confidence > 0.8:
                formatted_suggestions.append(f"💡 {text}")
            else:
                formatted_suggestions.append(f"• {text}")
        
        return "\n".join(formatted_suggestions)
    
    def get_contextual_tips(self, event_type: str, user_goals: List[str]) -> List[str]:
        """
        Get contextual tips based on event type and goals.
        
        Args:
            event_type: Type of event being planned
            user_goals: List of user goals
            
        Returns:
            List of contextual tips
        """
        tips = []
        
        # Event type specific tips
        event_tips = {
            "conference": [
                "Plan for 15-minute breaks between sessions to avoid delays",
                "Provide charging stations for attendee devices",
                "Consider live streaming for broader reach"
            ],
            "wedding": [
                "Create a timeline and share it with all vendors",
                "Assign someone to handle vendor questions on the day",
                "Plan for photos during golden hour for best lighting"
            ],
            "corporate": [
                "Include company branding subtly throughout the event",
                "Plan networking time for relationship building",
                "Consider follow-up actions to maintain momentum"
            ],
            "workshop": [
                "Prepare materials and handouts in advance",
                "Plan interactive elements every 20-30 minutes",
                "Have backup activities if sessions run short"
            ]
        }
        
        event_type_lower = event_type.lower()
        for event_key, event_tips_list in event_tips.items():
            if event_key in event_type_lower:
                tips.extend(event_tips_list[:2])  # Add top 2 tips
                break
        
        # Goal-specific tips
        goal_tips = {
            "networking": [
                "Create conversation starters or icebreaker activities",
                "Use name tags with titles to facilitate introductions"
            ],
            "lead_generation": [
                "Prepare qualifying questions for potential leads",
                "Have a clear follow-up process ready"
            ],
            "education": [
                "Provide take-home resources for continued learning",
                "Include time for Q&A and discussion"
            ],
            "team_building": [
                "Mix different departments or teams in activities",
                "Include reflection time to discuss learnings"
            ]
        }
        
        for goal in user_goals:
            goal_lower = goal.lower()
            if goal_lower in goal_tips:
                tips.extend(goal_tips[goal_lower])
        
        return tips[:4]  # Return top 4 tips
