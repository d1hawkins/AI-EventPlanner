"""
Test file for the Recommendation Learning System
Tests all functionality of the recommendation learning and feedback collection system
"""

import pytest
import uuid
from datetime import datetime, timedelta
from app.utils.recommendation_learning import RecommendationLearning, recommendation_learning

def test_recommendation_learning_initialization():
    """Test that RecommendationLearning initializes correctly"""
    learning_system = RecommendationLearning()
    
    assert len(learning_system.feedback_data) == 0
    assert len(learning_system.recommendation_history) == 0
    assert len(learning_system.effectiveness_scores) == 0
    assert len(learning_system.user_preferences) == 0
    assert learning_system.recommendation_analytics['total_recommendations'] == 0
    assert learning_system.recommendation_analytics['total_feedback'] == 0

def test_track_recommendation():
    """Test tracking recommendations"""
    learning_system = RecommendationLearning()
    
    rec_id = str(uuid.uuid4())
    learning_system.track_recommendation(
        recommendation_id=rec_id,
        recommendation_type="venue",
        recommendation_content="Consider a hotel conference center for professional atmosphere",
        context={"event_type": "corporate_conference", "attendees": 50},
        user_id="user123",
        event_type="corporate_conference"
    )
    
    assert learning_system.recommendation_analytics['total_recommendations'] == 1
    
    # Check that recommendation was stored
    key = "user123_corporate_conference"
    assert key in learning_system.recommendation_history
    assert len(learning_system.recommendation_history[key]) == 1
    
    stored_rec = learning_system.recommendation_history[key][0]
    assert stored_rec['id'] == rec_id
    assert stored_rec['type'] == "venue"
    assert stored_rec['user_id'] == "user123"
    assert stored_rec['feedback_received'] == False

def test_collect_feedback_rating():
    """Test collecting rating feedback"""
    learning_system = RecommendationLearning()
    
    # First track a recommendation
    rec_id = str(uuid.uuid4())
    learning_system.track_recommendation(
        recommendation_id=rec_id,
        recommendation_type="timing",
        recommendation_content="Tuesday-Thursday is optimal for corporate events",
        context={"event_type": "corporate_conference"},
        user_id="user123"
    )
    
    # Then collect feedback
    learning_system.collect_feedback(
        recommendation_id=rec_id,
        feedback_type="rating",
        feedback_value=4,  # 4 out of 5
        user_id="user123"
    )
    
    assert learning_system.recommendation_analytics['total_feedback'] == 1
    assert rec_id in learning_system.feedback_data
    assert len(learning_system.feedback_data[rec_id]) == 1
    
    feedback = learning_system.feedback_data[rec_id][0]
    assert feedback['feedback_type'] == "rating"
    assert feedback['feedback_value'] == 4
    assert feedback['user_id'] == "user123"

def test_collect_feedback_binary():
    """Test collecting binary feedback"""
    learning_system = RecommendationLearning()
    
    rec_id = str(uuid.uuid4())
    learning_system.track_recommendation(
        recommendation_id=rec_id,
        recommendation_type="budget",
        recommendation_content="Allocate 20% buffer for unexpected costs",
        context={"event_type": "wedding"},
        user_id="user456"
    )
    
    learning_system.collect_feedback(
        recommendation_id=rec_id,
        feedback_type="helpful",
        feedback_value="yes",
        user_id="user456"
    )
    
    # Check effectiveness score calculation
    assert "budget" in learning_system.effectiveness_scores
    assert len(learning_system.effectiveness_scores["budget"]) == 1
    assert learning_system.effectiveness_scores["budget"][0] == 1.0  # "yes" should be 1.0

def test_effectiveness_score_calculation():
    """Test effectiveness score calculation for different feedback types"""
    learning_system = RecommendationLearning()
    
    # Test rating conversion (1-5 scale to 0.0-1.0)
    feedback_record = {
        'feedback_type': 'rating',
        'feedback_value': 5
    }
    score = learning_system._calculate_effectiveness_score(feedback_record)
    assert score == 1.0
    
    feedback_record['feedback_value'] = 1
    score = learning_system._calculate_effectiveness_score(feedback_record)
    assert score == 0.0
    
    feedback_record['feedback_value'] = 3
    score = learning_system._calculate_effectiveness_score(feedback_record)
    assert score == 0.5
    
    # Test binary feedback
    feedback_record = {
        'feedback_type': 'binary',
        'feedback_value': True
    }
    score = learning_system._calculate_effectiveness_score(feedback_record)
    assert score == 1.0
    
    feedback_record['feedback_value'] = False
    score = learning_system._calculate_effectiveness_score(feedback_record)
    assert score == 0.0
    
    # Test helpful feedback
    feedback_record = {
        'feedback_type': 'helpful',
        'feedback_value': 'helpful'
    }
    score = learning_system._calculate_effectiveness_score(feedback_record)
    assert score == 1.0

def test_user_preferences_learning():
    """Test that user preferences are learned from feedback"""
    learning_system = RecommendationLearning()
    
    user_id = "user789"
    
    # Track and give positive feedback for venue recommendations
    for i in range(3):
        rec_id = str(uuid.uuid4())
        learning_system.track_recommendation(
            recommendation_id=rec_id,
            recommendation_type="venue",
            recommendation_content=f"Venue recommendation {i}",
            context={"event_type": "wedding"},
            user_id=user_id
        )
        
        learning_system.collect_feedback(
            recommendation_id=rec_id,
            feedback_type="rating",
            feedback_value=5,
            user_id=user_id
        )
    
    # Track and give negative feedback for catering recommendations
    for i in range(2):
        rec_id = str(uuid.uuid4())
        learning_system.track_recommendation(
            recommendation_id=rec_id,
            recommendation_type="catering",
            recommendation_content=f"Catering recommendation {i}",
            context={"event_type": "wedding"},
            user_id=user_id
        )
        
        learning_system.collect_feedback(
            recommendation_id=rec_id,
            feedback_type="rating",
            feedback_value=1,
            user_id=user_id
        )
    
    # Check user preferences
    assert user_id in learning_system.user_preferences
    user_prefs = learning_system.user_preferences[user_id]
    
    # Should prefer venue recommendations
    assert user_prefs['preferred_recommendation_types']['venue'] == 3
    
    # Should dislike catering recommendations
    assert user_prefs['disliked_recommendation_types']['catering'] == 2
    
    # Should have feedback history
    assert len(user_prefs['feedback_history']) == 5

def test_personalized_recommendation_strategy():
    """Test getting personalized recommendation strategy"""
    learning_system = RecommendationLearning()
    
    # Test with no user history
    strategy = learning_system.get_personalized_recommendation_strategy("new_user")
    assert strategy['strategy'] == 'default'
    assert strategy['confidence'] == 0.0
    assert len(strategy['preferred_types']) == 0
    
    # Create user with preferences
    user_id = "experienced_user"
    
    # Add positive feedback for timing recommendations
    for i in range(5):
        rec_id = str(uuid.uuid4())
        learning_system.track_recommendation(
            recommendation_id=rec_id,
            recommendation_type="timing",
            recommendation_content=f"Timing recommendation {i}",
            context={"event_type": "corporate"},
            user_id=user_id
        )
        
        learning_system.collect_feedback(
            recommendation_id=rec_id,
            feedback_type="rating",
            feedback_value=5,
            user_id=user_id
        )
    
    strategy = learning_system.get_personalized_recommendation_strategy(user_id)
    assert strategy['strategy'] == 'personalized'  # Should be 'personalized' when confidence > 0.3
    assert strategy['confidence'] == 0.5  # 5/10 = 0.5
    assert 'timing' in strategy['preferred_types']

def test_recommendation_improvements():
    """Test getting recommendation improvements"""
    learning_system = RecommendationLearning()
    
    # Create low-performing recommendation type
    rec_type = "low_performing_type"
    
    for i in range(5):
        rec_id = str(uuid.uuid4())
        learning_system.track_recommendation(
            recommendation_id=rec_id,
            recommendation_type=rec_type,
            recommendation_content=f"Poor recommendation {i}",
            context={"event_type": "test"},
            user_id=f"user{i}"
        )
        
        learning_system.collect_feedback(
            recommendation_id=rec_id,
            feedback_type="rating",
            feedback_value=1,  # Poor rating
            user_id=f"user{i}"
        )
    
    improvements = learning_system.get_recommendation_improvements(rec_type, {})
    assert len(improvements) > 0
    assert any("Low effectiveness detected" in imp for imp in improvements)

def test_analytics_report():
    """Test generating analytics report"""
    learning_system = RecommendationLearning()
    
    # Add some test data
    for i in range(3):
        rec_id = str(uuid.uuid4())
        learning_system.track_recommendation(
            recommendation_id=rec_id,
            recommendation_type="venue",
            recommendation_content=f"Venue recommendation {i}",
            context={"event_type": "wedding"},
            user_id=f"user{i}"
        )
        
        learning_system.collect_feedback(
            recommendation_id=rec_id,
            feedback_type="rating",
            feedback_value=4,
            user_id=f"user{i}"
        )
    
    report = learning_system.get_analytics_report()
    
    assert 'overall_statistics' in report
    assert 'category_statistics' in report
    assert 'user_statistics' in report
    assert 'generated_at' in report
    
    overall_stats = report['overall_statistics']
    assert overall_stats['total_recommendations'] == 3
    assert overall_stats['total_feedback'] == 3
    assert overall_stats['feedback_rate'] == 1.0
    assert overall_stats['average_effectiveness'] == 0.75  # Rating 4 -> 0.75

def test_export_import_learning_data():
    """Test exporting and importing learning data"""
    learning_system = RecommendationLearning()
    
    # Add some test data
    rec_id = str(uuid.uuid4())
    learning_system.track_recommendation(
        recommendation_id=rec_id,
        recommendation_type="test_type",
        recommendation_content="Test recommendation",
        context={"test": True},
        user_id="test_user"
    )
    
    learning_system.collect_feedback(
        recommendation_id=rec_id,
        feedback_type="rating",
        feedback_value=5,
        user_id="test_user"
    )
    
    # Export data
    exported_data = learning_system.export_learning_data()
    assert 'export_timestamp' in exported_data
    assert 'feedback_data' in exported_data
    assert 'recommendation_history' in exported_data
    
    # Create new instance and import
    new_learning_system = RecommendationLearning()
    success = new_learning_system.import_learning_data(exported_data)
    assert success == True
    
    # Verify data was imported
    assert new_learning_system.recommendation_analytics['total_recommendations'] == 1
    assert new_learning_system.recommendation_analytics['total_feedback'] == 1
    assert rec_id in new_learning_system.feedback_data

def test_trend_analysis():
    """Test trend analysis functionality"""
    learning_system = RecommendationLearning()
    
    rec_type = "trending_type"
    
    # Add early poor performance
    for i in range(5):
        rec_id = str(uuid.uuid4())
        learning_system.track_recommendation(
            recommendation_id=rec_id,
            recommendation_type=rec_type,
            recommendation_content=f"Early recommendation {i}",
            context={"period": "early"},
            user_id=f"user{i}"
        )
        
        learning_system.collect_feedback(
            recommendation_id=rec_id,
            feedback_type="rating",
            feedback_value=2,  # Poor early performance
            user_id=f"user{i}"
        )
    
    # Add recent good performance
    for i in range(5, 10):
        rec_id = str(uuid.uuid4())
        learning_system.track_recommendation(
            recommendation_id=rec_id,
            recommendation_type=rec_type,
            recommendation_content=f"Recent recommendation {i}",
            context={"period": "recent"},
            user_id=f"user{i}"
        )
        
        learning_system.collect_feedback(
            recommendation_id=rec_id,
            feedback_type="rating",
            feedback_value=5,  # Good recent performance
            user_id=f"user{i}"
        )
    
    trends = learning_system._analyze_trends()
    assert rec_type in trends
    trend = trends[rec_type]
    assert trend['direction'] == 'improving'
    assert trend['significance'] in ['high', 'moderate', 'low']

def test_global_instance():
    """Test that global instance works correctly"""
    # Test that we can use the global instance
    rec_id = str(uuid.uuid4())
    recommendation_learning.track_recommendation(
        recommendation_id=rec_id,
        recommendation_type="global_test",
        recommendation_content="Global instance test",
        context={"test": "global"},
        user_id="global_user"
    )
    
    assert recommendation_learning.recommendation_analytics['total_recommendations'] >= 1

def test_error_handling():
    """Test error handling in various scenarios"""
    learning_system = RecommendationLearning()
    
    # Test collecting feedback for non-existent recommendation
    learning_system.collect_feedback(
        recommendation_id="non_existent_id",
        feedback_type="rating",
        feedback_value=5,
        user_id="test_user"
    )
    
    # Should not crash, just log error
    assert learning_system.recommendation_analytics['total_feedback'] == 1
    
    # Test with invalid feedback type
    rec_id = str(uuid.uuid4())
    learning_system.track_recommendation(
        recommendation_id=rec_id,
        recommendation_type="test",
        recommendation_content="Test",
        context={},
        user_id="test_user"
    )
    
    learning_system.collect_feedback(
        recommendation_id=rec_id,
        feedback_type="unknown_type",
        feedback_value="unknown",
        user_id="test_user"
    )
    
    # Should default to 0.5 effectiveness score
    assert "test" in learning_system.effectiveness_scores
    assert learning_system.effectiveness_scores["test"][0] == 0.5

if __name__ == "__main__":
    print("Running Recommendation Learning System Tests...")
    
    # Run all tests
    test_functions = [
        test_recommendation_learning_initialization,
        test_track_recommendation,
        test_collect_feedback_rating,
        test_collect_feedback_binary,
        test_effectiveness_score_calculation,
        test_user_preferences_learning,
        test_personalized_recommendation_strategy,
        test_recommendation_improvements,
        test_analytics_report,
        test_export_import_learning_data,
        test_trend_analysis,
        test_global_instance,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: {str(e)}")
            failed += 1
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
