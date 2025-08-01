"""
Recommendation Engine for Conversational Agent

This module provides intelligent recommendations and proactive suggestions
for event planning based on user context, goals, and best practices.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class RecommendationEngine:
    """
    Provides contextual recommendations and proactive suggestions for event planning.
    
    Uses event type, user goals, and industry best practices to generate
    relevant recommendations throughout the conversation.
    """
    
    def __init__(self):
        """Initialize the RecommendationEngine with best practices and recommendation logic."""
        
        # Event type-specific best practices and recommendations
        self.best_practices = {
            "corporate_conference": {
                "timing": {
                    "recommendation": "Tuesday-Thursday for best attendance",
                    "details": "Business professionals are most available mid-week. Avoid Mondays (travel/catch-up) and Fridays (early departures)."
                },
                "duration": {
                    "recommendation": "1-2 days optimal for engagement",
                    "details": "Single day for focused topics, 2 days for comprehensive programs. Longer events see declining attendance."
                },
                "capacity": {
                    "recommendation": "Plan for 15% no-shows",
                    "details": "Corporate events typically see 10-20% no-show rate. Factor this into venue and catering planning."
                },
                "budget_allocation": {
                    "venue": 25,
                    "catering": 30,
                    "speakers": 20,
                    "av_tech": 10,
                    "marketing": 10,
                    "contingency": 5
                },
                "key_elements": ["keynote speakers", "networking breaks", "interactive sessions", "branded materials"]
            },
            "workshop": {
                "timing": {
                    "recommendation": "Mid-week, 9 AM - 4 PM for maximum focus",
                    "details": "Participants are most engaged during business hours. Avoid early morning or late evening sessions."
                },
                "duration": {
                    "recommendation": "4-8 hours with breaks every 90 minutes",
                    "details": "Adult learning attention spans require regular breaks. Include hands-on activities to maintain engagement."
                },
                "capacity": {
                    "recommendation": "15-25 participants for optimal interaction",
                    "details": "Small groups enable personalized attention and active participation from all attendees."
                },
                "budget_allocation": {
                    "venue": 20,
                    "materials": 25,
                    "instructor": 30,
                    "catering": 15,
                    "marketing": 5,
                    "contingency": 5
                },
                "key_elements": ["hands-on activities", "take-home materials", "small group exercises", "Q&A sessions"]
            },
            "wedding": {
                "timing": {
                    "recommendation": "Saturday afternoon/evening most popular",
                    "details": "Saturdays allow guests to travel and recover. Spring and fall are peak seasons with higher costs."
                },
                "duration": {
                    "recommendation": "4-6 hours including ceremony and reception",
                    "details": "Ceremony (30-60 min), cocktail hour (1 hour), reception (3-4 hours) is the typical flow."
                },
                "capacity": {
                    "recommendation": "Plan for 5-10% declines",
                    "details": "Wedding RSVPs are generally more reliable than corporate events, but still factor in some declines."
                },
                "budget_allocation": {
                    "venue": 40,
                    "catering": 30,
                    "photography": 10,
                    "flowers": 8,
                    "music": 7,
                    "contingency": 5
                },
                "key_elements": ["ceremony space", "reception venue", "catering", "photography", "music/entertainment"]
            },
            "networking_event": {
                "timing": {
                    "recommendation": "After-work hours, 5:30-8:30 PM",
                    "details": "Allows professionals to attend after work. Thursday evenings are often most successful."
                },
                "duration": {
                    "recommendation": "2-3 hours with structured and free networking",
                    "details": "Mix of structured activities (30-45 min) and open networking. Include arrival buffer time."
                },
                "capacity": {
                    "recommendation": "50-150 people for optimal networking",
                    "details": "Large enough for diverse connections, small enough to avoid overwhelming crowds."
                },
                "budget_allocation": {
                    "venue": 30,
                    "catering": 40,
                    "marketing": 15,
                    "activities": 10,
                    "contingency": 5
                },
                "key_elements": ["name tags", "conversation starters", "structured activities", "follow-up system"]
            },
            "product_launch": {
                "timing": {
                    "recommendation": "Tuesday-Wednesday for media coverage",
                    "details": "Mid-week timing ensures better media attendance and coverage. Avoid competing with other major announcements."
                },
                "duration": {
                    "recommendation": "2-3 hours including presentation and demo",
                    "details": "Product presentation (45 min), demo/hands-on (60 min), networking (30-45 min)."
                },
                "capacity": {
                    "recommendation": "Invite 2x desired attendance",
                    "details": "Product launches often have lower attendance rates. Key stakeholders and media are priority."
                },
                "budget_allocation": {
                    "venue": 25,
                    "catering": 20,
                    "av_production": 25,
                    "marketing": 20,
                    "materials": 5,
                    "contingency": 5
                },
                "key_elements": ["product demo area", "media kit", "branded materials", "photo opportunities"]
            },
            "team_building": {
                "timing": {
                    "recommendation": "Off-site during work hours or weekend retreat",
                    "details": "Work hours show company investment. Weekend retreats allow for deeper bonding but require incentives."
                },
                "duration": {
                    "recommendation": "Half-day to 2-day retreat",
                    "details": "Half-day for local teams, full day for department-wide, 2-day for company-wide or intensive programs."
                },
                "capacity": {
                    "recommendation": "10-30 people per activity group",
                    "details": "Large groups should be divided for activities. Maintain team dynamics while encouraging cross-team interaction."
                },
                "budget_allocation": {
                    "venue": 30,
                    "activities": 25,
                    "catering": 25,
                    "facilitator": 15,
                    "contingency": 5
                },
                "key_elements": ["team activities", "group challenges", "reflection sessions", "action planning"]
            }
        }
        
        # Goal-oriented recommendations
        self.goal_recommendations = {
            "networking": {
                "venue_features": ["open floor plan", "multiple conversation areas", "good acoustics"],
                "activities": ["structured introductions", "speed networking", "topic-based roundtables"],
                "timing": ["arrival buffer", "mixing activities", "follow-up facilitation"],
                "success_metrics": ["connections made", "business cards exchanged", "follow-up meetings scheduled"]
            },
            "lead_generation": {
                "venue_features": ["demo areas", "private meeting spaces", "good wifi"],
                "activities": ["product demonstrations", "one-on-one consultations", "qualification surveys"],
                "timing": ["qualification early", "demo scheduling", "follow-up capture"],
                "success_metrics": ["qualified leads", "demo requests", "contact information collected"]
            },
            "education": {
                "venue_features": ["classroom setup", "AV equipment", "breakout rooms"],
                "activities": ["interactive workshops", "Q&A sessions", "hands-on practice"],
                "timing": ["learning modules", "practice time", "knowledge assessment"],
                "success_metrics": ["knowledge retention", "skill demonstration", "satisfaction scores"]
            },
            "brand_awareness": {
                "venue_features": ["high visibility", "photo opportunities", "branded spaces"],
                "activities": ["brand storytelling", "interactive experiences", "social media moments"],
                "timing": ["brand presentation", "experience time", "sharing encouragement"],
                "success_metrics": ["brand recall", "social media mentions", "media coverage"]
            },
            "team_building": {
                "venue_features": ["activity spaces", "comfortable seating", "outdoor options"],
                "activities": ["collaborative challenges", "trust exercises", "reflection sessions"],
                "timing": ["ice breakers", "team activities", "debrief sessions"],
                "success_metrics": ["team cohesion", "communication improvement", "collaboration increase"]
            },
            "celebration": {
                "venue_features": ["festive atmosphere", "entertainment space", "photo areas"],
                "activities": ["recognition ceremonies", "entertainment", "social activities"],
                "timing": ["arrival reception", "main celebration", "informal socializing"],
                "success_metrics": ["attendance rate", "engagement level", "satisfaction scores"]
            }
        }
        
        # Contextual recommendation triggers
        self.recommendation_triggers = {
            "budget_tight": [
                "Consider off-peak dates for better venue rates",
                "Local speakers can reduce travel costs significantly",
                "Breakfast or lunch events are typically more cost-effective than dinner",
                "Partner venues may offer better rates for mutual promotion"
            ],
            "budget_flexible": [
                "Premium speakers can significantly enhance your event's value",
                "Unique venues create memorable experiences worth the investment",
                "Professional photography captures ROI for future marketing",
                "Enhanced catering options improve attendee satisfaction"
            ],
            "timeline_urgent": [
                "Focus on venues with in-house catering to simplify coordination",
                "Consider existing speaker networks for faster booking",
                "Digital invitations and registration speed up the process",
                "Prioritize must-have elements and defer nice-to-haves"
            ],
            "timeline_flexible": [
                "Early booking often secures better rates and availability",
                "More time allows for comprehensive speaker vetting",
                "Detailed planning phases improve overall event quality",
                "Multiple venue visits ensure the best choice"
            ],
            "large_event": [
                "Professional event management becomes cost-effective at scale",
                "Multiple registration streams prevent bottlenecks",
                "Crowd management and security planning are essential",
                "Live streaming can extend reach beyond physical capacity"
            ],
            "small_event": [
                "Intimate venues create better networking opportunities",
                "Personalized touches have greater impact",
                "Flexible formats allow for real-time adjustments",
                "Higher per-person investment in quality experiences"
            ],
            "outdoor_event": [
                "Weather contingency plans are absolutely essential",
                "Permit requirements vary significantly by location",
                "Power and restroom facilities need special consideration",
                "Seasonal timing affects both weather and costs"
            ],
            "corporate_event": [
                "Align event timing with business calendar and fiscal year",
                "Consider travel policies and approval processes",
                "Professional photography supports internal communications",
                "ROI measurement helps justify future event investments"
            ]
        }
        
        # Industry-specific considerations
        self.industry_considerations = {
            "technology": {
                "preferences": ["cutting-edge venues", "high-tech AV", "interactive demos"],
                "timing": ["avoid major tech conferences", "consider product cycles"],
                "networking": ["technical discussions", "innovation showcases", "startup connections"]
            },
            "healthcare": {
                "preferences": ["professional settings", "continuing education", "compliance focus"],
                "timing": ["avoid flu season for large gatherings", "consider medical conference calendar"],
                "networking": ["peer learning", "case studies", "regulatory updates"]
            },
            "finance": {
                "preferences": ["upscale venues", "security considerations", "professional atmosphere"],
                "timing": ["avoid quarter-end", "consider market hours", "regulatory calendar"],
                "networking": ["relationship building", "market insights", "regulatory discussions"]
            },
            "education": {
                "preferences": ["learning-focused venues", "interactive spaces", "accessible locations"],
                "timing": ["academic calendar", "testing periods", "holiday schedules"],
                "networking": ["peer collaboration", "resource sharing", "best practice exchange"]
            }
        }
    
    def get_recommendations(self, event_details: Dict[str, Any], user_goals: List[str], context: str) -> str:
        """
        Get relevant recommendations based on current context.
        
        Args:
            event_details: Current event details from state
            user_goals: List of user's primary goals
            context: Current conversation context/category
            
        Returns:
            Formatted recommendation text
        """
        recommendations = []
        
        # Get event type specific recommendations
        event_type = (event_details.get("event_type") or "").lower()
        event_type_key = self._map_event_type_to_key(event_type)
        
        if event_type_key and event_type_key in self.best_practices:
            best_practice = self.best_practices[event_type_key]
            
            # Context-specific recommendations
            if context == "timeline" and "timing" in best_practice:
                recommendations.append(f"**Timing Tip**: {best_practice['timing']['recommendation']} - {best_practice['timing']['details']}")
            
            elif context == "basic_details" and "capacity" in best_practice:
                recommendations.append(f"**Attendance Planning**: {best_practice['capacity']['recommendation']} - {best_practice['capacity']['details']}")
            
            elif context == "budget" and "budget_allocation" in best_practice:
                allocation = best_practice['budget_allocation']
                budget_text = ", ".join([f"{k.replace('_', ' ').title()}: {v}%" for k, v in allocation.items()])
                recommendations.append(f"**Budget Breakdown**: Typical allocation for {event_type}: {budget_text}")
        
        # Get goal-oriented recommendations
        for goal in user_goals:
            if goal in self.goal_recommendations:
                goal_rec = self.goal_recommendations[goal]
                
                if context == "location" and "venue_features" in goal_rec:
                    features = ", ".join(goal_rec["venue_features"])
                    recommendations.append(f"**For {goal.replace('_', ' ').title()}**: Look for venues with {features}")
                
                elif context == "success_criteria" and "success_metrics" in goal_rec:
                    metrics = ", ".join(goal_rec["success_metrics"])
                    recommendations.append(f"**Success Metrics**: For {goal.replace('_', ' ')}, consider tracking: {metrics}")
        
        # Get contextual recommendations based on event characteristics
        attendee_count = event_details.get("attendee_count", 0)
        if attendee_count:
            if attendee_count > 200:
                trigger_recs = self.recommendation_triggers.get("large_event", [])
                if trigger_recs and context in ["location", "resources"]:
                    recommendations.append(f"**Large Event Tip**: {trigger_recs[0]}")
            elif attendee_count < 50:
                trigger_recs = self.recommendation_triggers.get("small_event", [])
                if trigger_recs and context in ["location", "resources"]:
                    recommendations.append(f"**Intimate Event Tip**: {trigger_recs[0]}")
        
        # Budget-based recommendations
        if context == "budget":
            # This would be enhanced with actual budget analysis
            recommendations.append("**Budget Planning**: Always include a 10-15% contingency fund for unexpected expenses")
        
        # Combine recommendations
        if recommendations:
            return " | ".join(recommendations)
        
        return ""
    
    def _map_event_type_to_key(self, event_type: str) -> Optional[str]:
        """
        Map user's event type description to our best practice keys.
        
        Args:
            event_type: User's event type description
            
        Returns:
            Mapped key or None
        """
        event_type_lower = event_type.lower()
        
        # Direct mappings
        if any(word in event_type_lower for word in ["conference", "corporate"]):
            return "corporate_conference"
        elif any(word in event_type_lower for word in ["workshop", "training", "seminar"]):
            return "workshop"
        elif any(word in event_type_lower for word in ["wedding", "marriage"]):
            return "wedding"
        elif any(word in event_type_lower for word in ["networking", "mixer", "meetup"]):
            return "networking_event"
        elif any(word in event_type_lower for word in ["launch", "announcement", "unveiling"]):
            return "product_launch"
        elif any(word in event_type_lower for word in ["team building", "retreat", "offsite"]):
            return "team_building"
        
        return None
    
    def suggest_alternatives(self, current_choice: str, event_type: str, context: str) -> List[str]:
        """
        Suggest alternative approaches based on current choice.
        
        Args:
            current_choice: User's current choice/preference
            event_type: Type of event being planned
            context: Context of the choice (venue, timing, etc.)
            
        Returns:
            List of alternative suggestions
        """
        alternatives = []
        
        if context == "venue" and event_type:
            event_key = self._map_event_type_to_key(event_type)
            if event_key == "corporate_conference":
                alternatives = [
                    "Hotel conference centers offer all-in-one convenience",
                    "University venues provide academic atmosphere at lower cost",
                    "Unique venues like museums create memorable experiences",
                    "Corporate headquarters can reinforce company culture"
                ]
            elif event_key == "workshop":
                alternatives = [
                    "Training centers have built-in learning technology",
                    "Co-working spaces offer modern, flexible environments",
                    "Libraries provide quiet, focused atmospheres",
                    "Corporate training rooms ensure privacy and control"
                ]
        
        elif context == "timing":
            if "weekend" in current_choice.lower():
                alternatives = [
                    "Weekday events often have better venue availability",
                    "Tuesday-Thursday timing maximizes business attendance",
                    "Morning events can be more cost-effective",
                    "Evening events work well for networking"
                ]
            elif "weekday" in current_choice.lower():
                alternatives = [
                    "Weekend events allow for longer, more relaxed formats",
                    "Saturday events accommodate working professionals",
                    "Friday afternoon events can extend into social time",
                    "Sunday events work well for community gatherings"
                ]
        
        elif context == "budget":
            if any(word in current_choice.lower() for word in ["tight", "limited", "small"]):
                alternatives = [
                    "Partner with sponsors to offset costs",
                    "Consider co-hosting with complementary organizations",
                    "Use volunteer staff for non-critical roles",
                    "Choose venues with inclusive packages"
                ]
            elif any(word in current_choice.lower() for word in ["flexible", "generous", "large"]):
                alternatives = [
                    "Invest in premium speakers for higher value",
                    "Enhanced catering creates lasting impressions",
                    "Professional photography provides marketing value",
                    "Unique venues justify premium pricing"
                ]
        
        return alternatives[:3]  # Return top 3 alternatives
    
    def provide_best_practices(self, category: str, event_type: str) -> str:
        """
        Provide industry best practices for a specific category.
        
        Args:
            category: Category of best practice (timing, venue, budget, etc.)
            event_type: Type of event
            
        Returns:
            Best practice recommendation text
        """
        event_key = self._map_event_type_to_key(event_type)
        
        if not event_key or event_key not in self.best_practices:
            return ""
        
        best_practice = self.best_practices[event_key]
        
        if category == "timing" and "timing" in best_practice:
            return f"{best_practice['timing']['recommendation']} - {best_practice['timing']['details']}"
        
        elif category == "duration" and "duration" in best_practice:
            return f"{best_practice['duration']['recommendation']} - {best_practice['duration']['details']}"
        
        elif category == "capacity" and "capacity" in best_practice:
            return f"{best_practice['capacity']['recommendation']} - {best_practice['capacity']['details']}"
        
        elif category == "budget" and "budget_allocation" in best_practice:
            allocation = best_practice['budget_allocation']
            budget_items = [f'{k.replace("_", " ").title()}: {v}%' for k, v in allocation.items()]
            return f"Typical budget allocation: {', '.join(budget_items)}"
        
        elif category == "elements" and "key_elements" in best_practice:
            elements = ", ".join(best_practice['key_elements'])
            return f"Essential elements for {event_type}: {elements}"
        
        return ""
    
    def get_proactive_suggestions(self, state: Dict[str, Any]) -> List[str]:
        """
        Generate proactive suggestions based on current state.
        
        Args:
            state: Current conversation state
            
        Returns:
            List of proactive suggestions
        """
        suggestions = []
        event_details = state.get("event_details", {})
        user_goals = state.get("user_goals", [])
        
        # Analyze current information for proactive suggestions
        event_type = event_details.get("event_type", "").lower()
        attendee_count = event_details.get("attendee_count", 0)
        
        # Timeline-based suggestions
        if event_details.get("timeline_start"):
            timeline = event_details["timeline_start"].lower()
            if any(word in timeline for word in ["soon", "urgent", "quickly", "asap"]):
                suggestions.append("Given your tight timeline, I recommend focusing on venues with in-house catering and AV to simplify coordination.")
        
        # Budget optimization suggestions
        requirements = state.get("requirements", {})
        if "budget" in requirements:
            budget_info = requirements["budget"]
            if any(word in str(budget_info).lower() for word in ["tight", "limited", "small"]):
                suggestions.append("For budget optimization, consider Tuesday-Wednesday events, local speakers, and venues with inclusive packages.")
        
        # Event type specific proactive suggestions
        if "corporate" in event_type or "business" in event_type:
            suggestions.append("For corporate events, I recommend planning 3-4 months in advance to ensure executive availability and proper approvals.")
        
        if "networking" in event_type or "networking" in user_goals:
            suggestions.append("For networking success, plan for 1 person per 10-12 square feet and include structured ice-breaker activities.")
        
        # Size-based suggestions
        if attendee_count > 100:
            suggestions.append("With over 100 attendees, consider professional event management and multiple registration/check-in stations.")
        elif attendee_count > 0 and attendee_count < 30:
            suggestions.append("For intimate events like this, you can focus on personalized experiences and interactive formats.")
        
        # Goal-based suggestions
        if "lead_generation" in user_goals:
            suggestions.append("For lead generation, plan dedicated demo areas and ensure you have a system to capture and qualify attendee information.")
        
        if "education" in user_goals:
            suggestions.append("Educational events benefit from interactive elements - consider breakout sessions, hands-on activities, and Q&A periods.")
        
        return suggestions[:2]  # Return top 2 most relevant suggestions
    
    def get_risk_mitigation_recommendations(self, event_details: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """
        Provide risk mitigation recommendations based on event characteristics.
        
        Args:
            event_details: Event details
            requirements: Event requirements
            
        Returns:
            List of risk mitigation recommendations
        """
        recommendations = []
        
        # Weather-related risks
        location_info = requirements.get("location", {})
        if any(word in str(location_info).lower() for word in ["outdoor", "garden", "park", "beach"]):
            recommendations.append("For outdoor events, always have an indoor backup plan and monitor weather forecasts closely.")
        
        # Technology risks
        event_type = event_details.get("event_type", "").lower()
        if any(word in event_type for word in ["conference", "presentation", "workshop", "demo"]):
            recommendations.append("Have backup AV equipment and test all technology 24 hours before the event.")
        
        # Attendance risks
        attendee_count = event_details.get("attendee_count", 0)
        if attendee_count > 200:
            recommendations.append("For large events, implement a waitlist system and have contingency plans for both over and under-attendance.")
        
        # Speaker/vendor risks
        if any(word in event_type for word in ["conference", "workshop", "launch"]):
            recommendations.append("Always have backup speakers identified and maintain vendor contact lists with alternatives.")
        
        # Budget risks
        recommendations.append("Maintain a 15% contingency fund and get written quotes from all vendors to avoid surprise costs.")
        
        return recommendations[:3]  # Return top 3 most relevant recommendations
