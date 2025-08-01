"""
Recommendation Learning System
Tracks recommendation effectiveness and improves recommendations over time
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)

class RecommendationLearning:
    """
    System for tracking recommendation effectiveness and learning from user feedback
    to improve future recommendations.
    """
    
    def __init__(self):
        self.feedback_data = defaultdict(list)
        self.recommendation_history = defaultdict(list)
        self.effectiveness_scores = defaultdict(list)
        self.user_preferences = defaultdict(dict)
        self.recommendation_analytics = {
            'total_recommendations': 0,
            'total_feedback': 0,
            'average_effectiveness': 0.0,
            'top_performing_categories': [],
            'improvement_trends': []
        }
    
    def track_recommendation(self, 
                           recommendation_id: str,
                           recommendation_type: str,
                           recommendation_content: str,
                           context: Dict[str, Any],
                           user_id: Optional[str] = None,
                           event_type: Optional[str] = None) -> None:
        """
        Track a recommendation that was given to a user
        
        Args:
            recommendation_id: Unique identifier for the recommendation
            recommendation_type: Category of recommendation (timing, venue, budget, etc.)
            recommendation_content: The actual recommendation text
            context: Context in which recommendation was given
            user_id: User who received the recommendation
            event_type: Type of event being planned
        """
        try:
            recommendation_record = {
                'id': recommendation_id,
                'type': recommendation_type,
                'content': recommendation_content,
                'context': context,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'event_type': event_type,
                'feedback_received': False,
                'effectiveness_score': None
            }
            
            # Store in recommendation history
            key = f"{user_id}_{event_type}" if user_id and event_type else "global"
            self.recommendation_history[key].append(recommendation_record)
            
            # Update analytics
            self.recommendation_analytics['total_recommendations'] += 1
            
            logger.info(f"Tracked recommendation {recommendation_id} of type {recommendation_type}")
            
        except Exception as e:
            logger.error(f"Error tracking recommendation: {str(e)}")
    
    def collect_feedback(self,
                        recommendation_id: str,
                        feedback_type: str,
                        feedback_value: Any,
                        user_id: Optional[str] = None,
                        additional_context: Optional[Dict[str, Any]] = None) -> None:
        """
        Collect feedback on a recommendation
        
        Args:
            recommendation_id: ID of the recommendation being rated
            feedback_type: Type of feedback (rating, binary, text, etc.)
            feedback_value: The feedback value (1-5 rating, true/false, text, etc.)
            user_id: User providing feedback
            additional_context: Additional context about the feedback
        """
        try:
            feedback_record = {
                'recommendation_id': recommendation_id,
                'feedback_type': feedback_type,
                'feedback_value': feedback_value,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'context': additional_context or {}
            }
            
            # Store feedback
            self.feedback_data[recommendation_id].append(feedback_record)
            
            # Update recommendation record
            self._update_recommendation_with_feedback(recommendation_id, feedback_record)
            
            # Update analytics
            self.recommendation_analytics['total_feedback'] += 1
            
            # Learn from feedback
            self._learn_from_feedback(feedback_record)
            
            logger.info(f"Collected feedback for recommendation {recommendation_id}: {feedback_type}={feedback_value}")
            
        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
    
    def _update_recommendation_with_feedback(self, recommendation_id: str, feedback_record: Dict[str, Any]) -> None:
        """Update the recommendation record with feedback information"""
        try:
            # Find and update the recommendation record
            for key, recommendations in self.recommendation_history.items():
                for rec in recommendations:
                    if rec['id'] == recommendation_id:
                        rec['feedback_received'] = True
                        
                        # Calculate effectiveness score based on feedback
                        effectiveness_score = self._calculate_effectiveness_score(feedback_record)
                        rec['effectiveness_score'] = effectiveness_score
                        
                        # Store effectiveness score for analytics
                        self.effectiveness_scores[rec['type']].append(effectiveness_score)
                        break
                        
        except Exception as e:
            logger.error(f"Error updating recommendation with feedback: {str(e)}")
    
    def _calculate_effectiveness_score(self, feedback_record: Dict[str, Any]) -> float:
        """
        Calculate effectiveness score from feedback
        
        Returns:
            Float between 0.0 and 1.0 representing effectiveness
        """
        try:
            feedback_type = feedback_record['feedback_type']
            feedback_value = feedback_record['feedback_value']
            
            if feedback_type == 'rating':
                # Convert 1-5 rating to 0.0-1.0 scale
                return max(0.0, min(1.0, (feedback_value - 1) / 4))
            
            elif feedback_type == 'binary':
                # True/False feedback
                return 1.0 if feedback_value else 0.0
            
            elif feedback_type == 'helpful':
                # Helpful/Not helpful feedback
                return 1.0 if feedback_value in ['helpful', 'yes', True] else 0.0
            
            elif feedback_type == 'implemented':
                # Whether user implemented the recommendation
                return 1.0 if feedback_value else 0.0
            
            else:
                # Default neutral score for unknown feedback types
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating effectiveness score: {str(e)}")
            return 0.5
    
    def _learn_from_feedback(self, feedback_record: Dict[str, Any]) -> None:
        """Learn patterns from feedback to improve future recommendations"""
        try:
            recommendation_id = feedback_record['recommendation_id']
            user_id = feedback_record.get('user_id')
            
            # Find the original recommendation
            recommendation = self._find_recommendation(recommendation_id)
            if not recommendation:
                return
            
            # Update user preferences if user_id available
            if user_id:
                self._update_user_preferences(user_id, recommendation, feedback_record)
            
            # Update global learning patterns
            self._update_global_patterns(recommendation, feedback_record)
            
        except Exception as e:
            logger.error(f"Error learning from feedback: {str(e)}")
    
    def _find_recommendation(self, recommendation_id: str) -> Optional[Dict[str, Any]]:
        """Find a recommendation by ID"""
        for recommendations in self.recommendation_history.values():
            for rec in recommendations:
                if rec['id'] == recommendation_id:
                    return rec
        return None
    
    def _update_user_preferences(self, user_id: str, recommendation: Dict[str, Any], feedback: Dict[str, Any]) -> None:
        """Update user-specific preferences based on feedback"""
        try:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {
                    'preferred_recommendation_types': Counter(),
                    'disliked_recommendation_types': Counter(),
                    'preferred_contexts': [],
                    'feedback_history': []
                }
            
            user_prefs = self.user_preferences[user_id]
            effectiveness_score = self._calculate_effectiveness_score(feedback)
            
            # Update preference counters
            if effectiveness_score >= 0.7:  # High effectiveness
                user_prefs['preferred_recommendation_types'][recommendation['type']] += 1
            elif effectiveness_score <= 0.3:  # Low effectiveness
                user_prefs['disliked_recommendation_types'][recommendation['type']] += 1
            
            # Store feedback history
            user_prefs['feedback_history'].append({
                'recommendation_type': recommendation['type'],
                'effectiveness_score': effectiveness_score,
                'context': recommendation['context'],
                'timestamp': feedback['timestamp']
            })
            
            # Keep only recent feedback (last 50 items)
            if len(user_prefs['feedback_history']) > 50:
                user_prefs['feedback_history'] = user_prefs['feedback_history'][-50:]
                
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
    
    def _update_global_patterns(self, recommendation: Dict[str, Any], feedback: Dict[str, Any]) -> None:
        """Update global recommendation patterns"""
        try:
            effectiveness_score = self._calculate_effectiveness_score(feedback)
            
            # Update average effectiveness
            all_scores = []
            for scores in self.effectiveness_scores.values():
                all_scores.extend(scores)
            
            if all_scores:
                self.recommendation_analytics['average_effectiveness'] = statistics.mean(all_scores)
            
            # Update top performing categories
            category_averages = {}
            for category, scores in self.effectiveness_scores.items():
                if scores:
                    category_averages[category] = statistics.mean(scores)
            
            # Sort by average effectiveness
            sorted_categories = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)
            self.recommendation_analytics['top_performing_categories'] = sorted_categories[:5]
            
        except Exception as e:
            logger.error(f"Error updating global patterns: {str(e)}")
    
    def get_recommendation_improvements(self, recommendation_type: str, context: Dict[str, Any]) -> List[str]:
        """
        Get suggestions for improving recommendations of a specific type
        
        Args:
            recommendation_type: Type of recommendation to improve
            context: Context for the recommendation
            
        Returns:
            List of improvement suggestions
        """
        try:
            improvements = []
            
            # Check effectiveness scores for this type
            if recommendation_type in self.effectiveness_scores:
                scores = self.effectiveness_scores[recommendation_type]
                if scores:
                    avg_score = statistics.mean(scores)
                    
                    if avg_score < 0.5:
                        improvements.append(f"Low effectiveness detected for {recommendation_type} recommendations (avg: {avg_score:.2f})")
                        improvements.append("Consider revising recommendation templates or criteria")
                    
                    if len(scores) >= 10:  # Enough data for trend analysis
                        recent_scores = scores[-5:]  # Last 5 scores
                        older_scores = scores[-10:-5]  # Previous 5 scores
                        
                        if recent_scores and older_scores:
                            recent_avg = statistics.mean(recent_scores)
                            older_avg = statistics.mean(older_scores)
                            
                            if recent_avg < older_avg - 0.1:  # Declining trend
                                improvements.append(f"Declining effectiveness trend for {recommendation_type}")
                                improvements.append("Review recent changes or user feedback patterns")
            
            # Check for user preference patterns
            common_dislikes = Counter()
            for user_prefs in self.user_preferences.values():
                for disliked_type, count in user_prefs['disliked_recommendation_types'].items():
                    if disliked_type == recommendation_type:
                        common_dislikes[recommendation_type] += count
            
            if common_dislikes[recommendation_type] > 3:  # Multiple users dislike this type
                improvements.append(f"Multiple users show negative feedback for {recommendation_type}")
                improvements.append("Consider alternative approaches or more personalized recommendations")
            
            return improvements
            
        except Exception as e:
            logger.error(f"Error getting recommendation improvements: {str(e)}")
            return []
    
    def get_personalized_recommendation_strategy(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalized recommendation strategy for a user based on their history
        
        Args:
            user_id: User to get strategy for
            
        Returns:
            Dictionary with personalized strategy recommendations
        """
        try:
            if user_id not in self.user_preferences:
                return {
                    'strategy': 'default',
                    'preferred_types': [],
                    'avoid_types': [],
                    'confidence': 0.0,
                    'recommendations': ['Use default recommendation strategy - no user history available']
                }
            
            user_prefs = self.user_preferences[user_id]
            
            # Get most preferred recommendation types
            preferred_types = [item[0] for item in user_prefs['preferred_recommendation_types'].most_common(3)]
            
            # Get types to avoid
            avoid_types = [item[0] for item in user_prefs['disliked_recommendation_types'].most_common(2)]
            
            # Calculate confidence based on amount of feedback
            total_feedback = len(user_prefs['feedback_history'])
            confidence = min(1.0, total_feedback / 10.0)  # Full confidence after 10+ feedback items
            
            # Generate strategy recommendations
            strategy_recommendations = []
            
            if preferred_types:
                strategy_recommendations.append(f"Prioritize {', '.join(preferred_types)} recommendations")
            
            if avoid_types:
                strategy_recommendations.append(f"Minimize or avoid {', '.join(avoid_types)} recommendations")
            
            if confidence < 0.3:
                strategy_recommendations.append("Gather more feedback to improve personalization")
            
            # Analyze recent trends
            if len(user_prefs['feedback_history']) >= 5:
                recent_scores = [item['effectiveness_score'] for item in user_prefs['feedback_history'][-5:]]
                avg_recent = statistics.mean(recent_scores)
                
                if avg_recent > 0.7:
                    strategy_recommendations.append("User shows high satisfaction with recent recommendations")
                elif avg_recent < 0.4:
                    strategy_recommendations.append("User shows low satisfaction - consider different approach")
            
            return {
                'strategy': 'personalized' if confidence > 0.3 else 'learning',
                'preferred_types': preferred_types,
                'avoid_types': avoid_types,
                'confidence': confidence,
                'recommendations': strategy_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting personalized strategy: {str(e)}")
            return {
                'strategy': 'error',
                'preferred_types': [],
                'avoid_types': [],
                'confidence': 0.0,
                'recommendations': ['Error analyzing user preferences']
            }
    
    def get_analytics_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report on recommendation effectiveness
        
        Returns:
            Dictionary with analytics data
        """
        try:
            # Calculate overall statistics
            all_scores = []
            for scores in self.effectiveness_scores.values():
                all_scores.extend(scores)
            
            overall_stats = {
                'total_recommendations': self.recommendation_analytics['total_recommendations'],
                'total_feedback': self.recommendation_analytics['total_feedback'],
                'feedback_rate': (self.recommendation_analytics['total_feedback'] / 
                                max(1, self.recommendation_analytics['total_recommendations'])),
                'average_effectiveness': statistics.mean(all_scores) if all_scores else 0.0,
                'effectiveness_std_dev': statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0
            }
            
            # Category-specific statistics
            category_stats = {}
            for category, scores in self.effectiveness_scores.items():
                if scores:
                    category_stats[category] = {
                        'count': len(scores),
                        'average_effectiveness': statistics.mean(scores),
                        'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0.0,
                        'min_score': min(scores),
                        'max_score': max(scores)
                    }
            
            # User engagement statistics
            user_stats = {
                'total_users_with_preferences': len(self.user_preferences),
                'average_feedback_per_user': (sum(len(prefs['feedback_history']) 
                                                for prefs in self.user_preferences.values()) / 
                                            max(1, len(self.user_preferences))),
                'most_active_users': self._get_most_active_users(5)
            }
            
            # Trend analysis
            trend_analysis = self._analyze_trends()
            
            # Improvement opportunities
            improvement_opportunities = self._identify_improvement_opportunities()
            
            return {
                'generated_at': datetime.now().isoformat(),
                'overall_statistics': overall_stats,
                'category_statistics': category_stats,
                'user_statistics': user_stats,
                'trend_analysis': trend_analysis,
                'improvement_opportunities': improvement_opportunities,
                'top_performing_categories': self.recommendation_analytics['top_performing_categories']
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {str(e)}")
            return {'error': str(e)}
    
    def _get_most_active_users(self, limit: int) -> List[Tuple[str, int]]:
        """Get most active users by feedback count"""
        try:
            user_activity = []
            for user_id, prefs in self.user_preferences.items():
                feedback_count = len(prefs['feedback_history'])
                user_activity.append((user_id, feedback_count))
            
            return sorted(user_activity, key=lambda x: x[1], reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"Error getting most active users: {str(e)}")
            return []
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze trends in recommendation effectiveness over time"""
        try:
            trends = {}
            
            # Analyze trends for each category
            for category, scores in self.effectiveness_scores.items():
                if len(scores) >= 10:  # Need enough data for trend analysis
                    # Split into time periods
                    mid_point = len(scores) // 2
                    early_scores = scores[:mid_point]
                    recent_scores = scores[mid_point:]
                    
                    early_avg = statistics.mean(early_scores)
                    recent_avg = statistics.mean(recent_scores)
                    
                    trend_direction = 'improving' if recent_avg > early_avg else 'declining'
                    trend_magnitude = abs(recent_avg - early_avg)
                    
                    trends[category] = {
                        'direction': trend_direction,
                        'magnitude': trend_magnitude,
                        'early_average': early_avg,
                        'recent_average': recent_avg,
                        'significance': 'high' if trend_magnitude > 0.2 else 'moderate' if trend_magnitude > 0.1 else 'low'
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {}
    
    def _identify_improvement_opportunities(self) -> List[str]:
        """Identify specific opportunities for improvement"""
        try:
            opportunities = []
            
            # Low-performing categories
            for category, scores in self.effectiveness_scores.items():
                if scores:
                    avg_score = statistics.mean(scores)
                    if avg_score < 0.4:
                        opportunities.append(f"Low performance in {category} recommendations (avg: {avg_score:.2f})")
            
            # Categories with high variance (inconsistent performance)
            for category, scores in self.effectiveness_scores.items():
                if len(scores) > 5:
                    std_dev = statistics.stdev(scores)
                    if std_dev > 0.3:
                        opportunities.append(f"High variance in {category} recommendations - inconsistent quality")
            
            # Low feedback rate
            if self.recommendation_analytics['total_recommendations'] > 0:
                feedback_rate = (self.recommendation_analytics['total_feedback'] / 
                               self.recommendation_analytics['total_recommendations'])
                if feedback_rate < 0.3:
                    opportunities.append("Low feedback collection rate - consider improving feedback mechanisms")
            
            # Users with consistently low satisfaction
            low_satisfaction_users = 0
            for user_prefs in self.user_preferences.values():
                if len(user_prefs['feedback_history']) >= 5:
                    recent_scores = [item['effectiveness_score'] for item in user_prefs['feedback_history'][-5:]]
                    if statistics.mean(recent_scores) < 0.4:
                        low_satisfaction_users += 1
            
            if low_satisfaction_users > 0:
                opportunities.append(f"{low_satisfaction_users} users show consistently low satisfaction")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying improvement opportunities: {str(e)}")
            return []
    
    def export_learning_data(self) -> Dict[str, Any]:
        """Export all learning data for backup or analysis"""
        try:
            return {
                'export_timestamp': datetime.now().isoformat(),
                'feedback_data': dict(self.feedback_data),
                'recommendation_history': dict(self.recommendation_history),
                'effectiveness_scores': dict(self.effectiveness_scores),
                'user_preferences': dict(self.user_preferences),
                'recommendation_analytics': self.recommendation_analytics
            }
        except Exception as e:
            logger.error(f"Error exporting learning data: {str(e)}")
            return {}
    
    def import_learning_data(self, data: Dict[str, Any]) -> bool:
        """Import learning data from backup"""
        try:
            if 'feedback_data' in data:
                self.feedback_data = defaultdict(list, data['feedback_data'])
            
            if 'recommendation_history' in data:
                self.recommendation_history = defaultdict(list, data['recommendation_history'])
            
            if 'effectiveness_scores' in data:
                self.effectiveness_scores = defaultdict(list, data['effectiveness_scores'])
            
            if 'user_preferences' in data:
                self.user_preferences = defaultdict(dict, data['user_preferences'])
            
            if 'recommendation_analytics' in data:
                self.recommendation_analytics.update(data['recommendation_analytics'])
            
            logger.info("Successfully imported learning data")
            return True
            
        except Exception as e:
            logger.error(f"Error importing learning data: {str(e)}")
            return False


# Global instance for easy access
recommendation_learning = RecommendationLearning()
