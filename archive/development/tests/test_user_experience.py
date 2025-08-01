#!/usr/bin/env python3
"""
User Experience Testing for Conversational Agent
Tests conversation naturalness, recommendation relevance, question flow logic, and goal achievement
"""

import asyncio
import json
import time
from typing import Dict, List, Any
from app.graphs.coordinator_graph import create_coordinator_graph
from app.utils.question_manager import QuestionManager
from app.utils.recommendation_engine import RecommendationEngine
from app.utils.conversation_paths import ConversationPaths
from app.utils.proactive_suggestions import ProactiveSuggestions

class UserExperienceTestSuite:
    """Comprehensive user experience testing suite"""
    
    def __init__(self):
        self.graph = create_coordinator_graph()
        self.question_manager = QuestionManager()
        self.recommendation_engine = RecommendationEngine()
        self.conversation_paths = ConversationPaths()
        self.proactive_suggestions = ProactiveSuggestions()
        self.test_results = {
            "conversation_naturalness": [],
            "recommendation_relevance": [],
            "question_flow_logic": [],
            "goal_achievement": [],
            "performance_metrics": {}
        }
    
    async def run_all_tests(self):
        """Run all user experience tests"""
        print("🚀 Starting User Experience Test Suite...")
        print("=" * 60)
        
        # Test 1: Conversation Naturalness
        await self.test_conversation_naturalness()
        
        # Test 2: Recommendation Relevance
        await self.test_recommendation_relevance()
        
        # Test 3: Question Flow Logic
        await self.test_question_flow_logic()
        
        # Test 4: Goal Achievement
        await self.test_goal_achievement()
        
        # Generate final report
        self.generate_test_report()
    
    async def test_conversation_naturalness(self):
        """Test if conversations feel natural and engaging"""
        print("\n📝 Testing Conversation Naturalness...")
        
        test_scenarios = [
            {
                "name": "Corporate Conference Planning",
                "initial_message": "I need to plan a corporate conference for our company",
                "expected_flow": ["event_type", "goals", "attendees", "timeline", "budget"]
            },
            {
                "name": "Team Building Retreat",
                "initial_message": "We want to organize a team building retreat",
                "expected_flow": ["team_size", "goals", "duration", "activities", "location"]
            },
            {
                "name": "Product Launch Event",
                "initial_message": "Help me plan a product launch event",
                "expected_flow": ["product_type", "audience", "goals", "scale", "timeline"]
            }
        ]
        
        for scenario in test_scenarios:
            print(f"  Testing: {scenario['name']}")
            
            # Initialize conversation state
            state = {
                "messages": [{"role": "user", "content": scenario["initial_message"]}],
                "event_details": {},
                "requirements": {},
                "conversation_stage": "discovery",
                "current_question_focus": None,
                "question_history": [],
                "user_goals": [],
                "recommendations_given": [],
                "next_question_priority": [],
                "information_completeness": {}
            }
            
            # Run conversation for 5 exchanges
            conversation_quality_score = 0
            for i in range(5):
                try:
                    # Get next question
                    next_question = self.question_manager.get_next_question(state, {})
                    if next_question:
                        # Evaluate question quality
                        quality_score = self.evaluate_question_quality(
                            next_question, 
                            state, 
                            scenario["expected_flow"]
                        )
                        conversation_quality_score += quality_score
                        
                        # Simulate user response
                        user_response = self.simulate_user_response(next_question, scenario["name"])
                        state["messages"].append({"role": "user", "content": user_response})
                        
                        # Update state based on response
                        self.question_manager.process_answer(state, user_response, next_question)
                    
                except Exception as e:
                    print(f"    ❌ Error in conversation flow: {e}")
                    conversation_quality_score -= 10
            
            # Calculate average quality score
            avg_quality = conversation_quality_score / 5 if conversation_quality_score > 0 else 0
            
            result = {
                "scenario": scenario["name"],
                "quality_score": avg_quality,
                "conversation_length": len(state["messages"]),
                "questions_asked": len(state["question_history"]),
                "passed": avg_quality >= 7.0  # Target: >7.0/10
            }
            
            self.test_results["conversation_naturalness"].append(result)
            
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"    {status} - Quality Score: {avg_quality:.1f}/10")
    
    async def test_recommendation_relevance(self):
        """Test if recommendations are relevant and helpful"""
        print("\n🎯 Testing Recommendation Relevance...")
        
        test_cases = [
            {
                "event_type": "corporate_conference",
                "goals": ["networking", "knowledge_sharing"],
                "attendees": 150,
                "expected_recommendations": ["interactive_sessions", "networking_breaks", "expert_speakers"]
            },
            {
                "event_type": "team_retreat",
                "goals": ["team_building", "strategic_planning"],
                "attendees": 25,
                "expected_recommendations": ["team_activities", "facilitated_sessions", "outdoor_activities"]
            },
            {
                "event_type": "product_launch",
                "goals": ["brand_awareness", "lead_generation"],
                "attendees": 200,
                "expected_recommendations": ["demo_stations", "media_coverage", "follow_up_strategy"]
            }
        ]
        
        for case in test_cases:
            print(f"  Testing: {case['event_type']} recommendations")
            
            # Get recommendations
            recommendations = self.recommendation_engine.get_recommendations(
                {"event_type": case["event_type"], "attendee_count": case["attendees"]},
                case["goals"],
                {"stage": "planning"}
            )
            
            # Evaluate relevance
            relevance_score = self.evaluate_recommendation_relevance(
                recommendations,
                case["expected_recommendations"],
                case["event_type"]
            )
            
            result = {
                "event_type": case["event_type"],
                "relevance_score": relevance_score,
                "recommendations_count": len(recommendations) if recommendations else 0,
                "passed": relevance_score >= 8.0  # Target: >80% relevance
            }
            
            self.test_results["recommendation_relevance"].append(result)
            
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"    {status} - Relevance Score: {relevance_score:.1f}/10")
    
    async def test_question_flow_logic(self):
        """Test if question flow follows logical progression"""
        print("\n🔄 Testing Question Flow Logic...")
        
        # Test logical question progression
        state = {
            "messages": [],
            "event_details": {},
            "requirements": {},
            "conversation_stage": "discovery",
            "current_question_focus": None,
            "question_history": [],
            "user_goals": [],
            "recommendations_given": [],
            "next_question_priority": [],
            "information_completeness": {
                "basic_details": 0.0,
                "timeline": 0.0,
                "budget": 0.0,
                "logistics": 0.0
            }
        }
        
        question_sequence = []
        logic_score = 10.0
        
        # Generate 10 questions and evaluate flow
        for i in range(10):
            try:
                next_question = self.question_manager.get_next_question(state, {})
                if next_question:
                    question_sequence.append(next_question["category"])
                    
                    # Check if question follows logical progression
                    if i > 0:
                        previous_category = question_sequence[i-1]
                        current_category = next_question["category"]
                        
                        if not self.is_logical_progression(previous_category, current_category, state):
                            logic_score -= 1.0
                    
                    # Simulate answer and update state
                    mock_answer = self.generate_mock_answer(next_question)
                    self.question_manager.process_answer(state, mock_answer, next_question)
                
            except Exception as e:
                print(f"    ❌ Error in question flow: {e}")
                logic_score -= 2.0
        
        result = {
            "question_sequence": question_sequence,
            "logic_score": logic_score,
            "total_questions": len(question_sequence),
            "passed": logic_score >= 9.0  # Target: >90% logical flow
        }
        
        self.test_results["question_flow_logic"].append(result)
        
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"    {status} - Logic Score: {logic_score:.1f}/10")
        print(f"    Question Flow: {' → '.join(question_sequence[:5])}...")
    
    async def test_goal_achievement(self):
        """Test if conversations successfully achieve user goals"""
        print("\n🎯 Testing Goal Achievement...")
        
        goal_scenarios = [
            {
                "user_goal": "plan_successful_conference",
                "required_info": ["event_type", "attendees", "budget", "timeline", "venue"],
                "success_criteria": ["proposal_generated", "timeline_created", "budget_allocated"]
            },
            {
                "user_goal": "organize_team_building",
                "required_info": ["team_size", "objectives", "duration", "activities"],
                "success_criteria": ["activity_plan", "schedule_created", "logistics_planned"]
            }
        ]
        
        for scenario in goal_scenarios:
            print(f"  Testing goal: {scenario['user_goal']}")
            
            # Simulate full conversation to achieve goal
            state = {
                "messages": [],
                "event_details": {},
                "requirements": {},
                "conversation_stage": "discovery",
                "current_question_focus": None,
                "question_history": [],
                "user_goals": [scenario["user_goal"]],
                "recommendations_given": [],
                "next_question_priority": [],
                "information_completeness": {}
            }
            
            # Run conversation until goal is achieved or max iterations
            goal_achieved = False
            iterations = 0
            max_iterations = 15
            
            while not goal_achieved and iterations < max_iterations:
                try:
                    # Check if we have enough information
                    info_completeness = self.assess_information_completeness(
                        state, 
                        scenario["required_info"]
                    )
                    
                    if info_completeness >= 0.8:  # 80% complete
                        # Try to generate proposal/plan
                        goal_achieved = self.simulate_goal_completion(state, scenario)
                        break
                    
                    # Continue conversation
                    next_question = self.question_manager.get_next_question(state, {})
                    if next_question:
                        mock_answer = self.generate_mock_answer(next_question)
                        self.question_manager.process_answer(state, mock_answer, next_question)
                    
                    iterations += 1
                    
                except Exception as e:
                    print(f"    ❌ Error in goal achievement: {e}")
                    break
            
            result = {
                "goal": scenario["user_goal"],
                "achieved": goal_achieved,
                "iterations": iterations,
                "info_completeness": self.assess_information_completeness(state, scenario["required_info"]),
                "passed": goal_achieved and iterations <= 12  # Target: achieve goal in ≤12 exchanges
            }
            
            self.test_results["goal_achievement"].append(result)
            
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"    {status} - Goal achieved in {iterations} iterations")
    
    def evaluate_question_quality(self, question: Dict, state: Dict, expected_flow: List[str]) -> float:
        """Evaluate the quality of a question (0-10 scale)"""
        score = 5.0  # Base score
        
        # Check if question is relevant to expected flow
        if question.get("category") in expected_flow:
            score += 2.0
        
        # Check if question builds on previous context
        if len(state.get("question_history", [])) > 0:
            if self.builds_on_context(question, state):
                score += 1.5
        
        # Check question clarity and specificity
        if len(question.get("text", "")) > 20 and "?" in question.get("text", ""):
            score += 1.0
        
        # Check if question includes helpful context/recommendations
        if "recommendation" in question.get("text", "").lower():
            score += 0.5
        
        return min(score, 10.0)
    
    def evaluate_recommendation_relevance(self, recommendations: List, expected: List[str], event_type: str) -> float:
        """Evaluate recommendation relevance (0-10 scale)"""
        if not recommendations:
            return 0.0
        
        relevance_score = 0.0
        total_recommendations = len(recommendations)
        
        for rec in recommendations:
            rec_text = rec.get("text", "").lower() if isinstance(rec, dict) else str(rec).lower()
            
            # Check if recommendation matches expected categories
            for expected_rec in expected:
                if expected_rec.lower() in rec_text:
                    relevance_score += 2.0
                    break
            
            # Check if recommendation is event-type appropriate
            if event_type.lower() in rec_text:
                relevance_score += 1.0
        
        return min(relevance_score / total_recommendations * 2, 10.0)
    
    def is_logical_progression(self, previous_category: str, current_category: str, state: Dict) -> bool:
        """Check if question progression is logical"""
        logical_flows = {
            "event_type": ["goals", "attendees", "timeline"],
            "goals": ["attendees", "timeline", "budget"],
            "attendees": ["venue", "budget", "logistics"],
            "timeline": ["venue", "logistics", "marketing"],
            "budget": ["venue", "catering", "logistics"],
            "venue": ["catering", "logistics", "equipment"],
            "logistics": ["marketing", "registration", "follow_up"]
        }
        
        expected_next = logical_flows.get(previous_category, [])
        return current_category in expected_next or current_category == previous_category
    
    def simulate_user_response(self, question: Dict, scenario_name: str) -> str:
        """Simulate realistic user responses"""
        category = question.get("category", "")
        
        responses = {
            "event_type": {
                "Corporate Conference Planning": "A 2-day corporate conference",
                "Team Building Retreat": "A team building retreat for our department",
                "Product Launch Event": "A product launch event for our new software"
            },
            "goals": {
                "Corporate Conference Planning": "Knowledge sharing and networking",
                "Team Building Retreat": "Improve team collaboration and morale",
                "Product Launch Event": "Generate buzz and attract potential customers"
            },
            "attendees": {
                "Corporate Conference Planning": "Around 150 people",
                "Team Building Retreat": "25 team members",
                "Product Launch Event": "About 200 people including media and clients"
            },
            "timeline": {
                "Corporate Conference Planning": "In 3 months",
                "Team Building Retreat": "Next quarter",
                "Product Launch Event": "In 6 weeks"
            },
            "budget": {
                "Corporate Conference Planning": "$50,000",
                "Team Building Retreat": "$15,000",
                "Product Launch Event": "$75,000"
            }
        }
        
        return responses.get(category, {}).get(scenario_name, "I'm not sure yet")
    
    def generate_mock_answer(self, question: Dict) -> str:
        """Generate mock answers for testing"""
        category = question.get("category", "")
        
        mock_answers = {
            "event_type": "Corporate conference",
            "goals": "Networking and knowledge sharing",
            "attendees": "100 people",
            "timeline": "In 2 months",
            "budget": "$30,000",
            "venue": "Downtown convention center",
            "catering": "Lunch and coffee breaks",
            "logistics": "Need AV equipment and registration desk"
        }
        
        return mock_answers.get(category, "Yes, that sounds good")
    
    def builds_on_context(self, question: Dict, state: Dict) -> bool:
        """Check if question builds on previous context"""
        if not state.get("question_history"):
            return True
        
        # Simple heuristic: check if question references previous information
        question_text = question.get("text", "").lower()
        
        for prev_q in state["question_history"]:
            prev_category = prev_q.get("category", "")
            if prev_category in question_text:
                return True
        
        return False
    
    def assess_information_completeness(self, state: Dict, required_info: List[str]) -> float:
        """Assess how complete the required information is"""
        if not required_info:
            return 1.0
        
        collected_info = 0
        for info_type in required_info:
            if state.get("event_details", {}).get(info_type) or \
               any(q.get("category") == info_type for q in state.get("question_history", [])):
                collected_info += 1
        
        return collected_info / len(required_info)
    
    def simulate_goal_completion(self, state: Dict, scenario: Dict) -> bool:
        """Simulate whether goal was successfully completed"""
        # Check if we have minimum required information
        required_info = scenario["required_info"]
        completeness = self.assess_information_completeness(state, required_info)
        
        # Goal is achieved if we have 80% of required info and reasonable conversation length
        return completeness >= 0.8 and len(state.get("question_history", [])) >= 5
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 USER EXPERIENCE TEST REPORT")
        print("=" * 60)
        
        # Conversation Naturalness Results
        print("\n📝 Conversation Naturalness:")
        naturalness_scores = [r["quality_score"] for r in self.test_results["conversation_naturalness"]]
        avg_naturalness = sum(naturalness_scores) / len(naturalness_scores) if naturalness_scores else 0
        passed_naturalness = sum(1 for r in self.test_results["conversation_naturalness"] if r["passed"])
        
        print(f"  Average Quality Score: {avg_naturalness:.1f}/10")
        print(f"  Tests Passed: {passed_naturalness}/{len(self.test_results['conversation_naturalness'])}")
        print(f"  Target: >7.0/10 - {'✅ MET' if avg_naturalness >= 7.0 else '❌ NOT MET'}")
        
        # Recommendation Relevance Results
        print("\n🎯 Recommendation Relevance:")
        relevance_scores = [r["relevance_score"] for r in self.test_results["recommendation_relevance"]]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        passed_relevance = sum(1 for r in self.test_results["recommendation_relevance"] if r["passed"])
        
        print(f"  Average Relevance Score: {avg_relevance:.1f}/10")
        print(f"  Tests Passed: {passed_relevance}/{len(self.test_results['recommendation_relevance'])}")
        print(f"  Target: >8.0/10 - {'✅ MET' if avg_relevance >= 8.0 else '❌ NOT MET'}")
        
        # Question Flow Logic Results
        print("\n🔄 Question Flow Logic:")
        logic_scores = [r["logic_score"] for r in self.test_results["question_flow_logic"]]
        avg_logic = sum(logic_scores) / len(logic_scores) if logic_scores else 0
        passed_logic = sum(1 for r in self.test_results["question_flow_logic"] if r["passed"])
        
        print(f"  Average Logic Score: {avg_logic:.1f}/10")
        print(f"  Tests Passed: {passed_logic}/{len(self.test_results['question_flow_logic'])}")
        print(f"  Target: >9.0/10 - {'✅ MET' if avg_logic >= 9.0 else '❌ NOT MET'}")
        
        # Goal Achievement Results
        print("\n🎯 Goal Achievement:")
        achieved_goals = sum(1 for r in self.test_results["goal_achievement"] if r["achieved"])
        total_goals = len(self.test_results["goal_achievement"])
        achievement_rate = (achieved_goals / total_goals * 100) if total_goals > 0 else 0
        
        print(f"  Goals Achieved: {achieved_goals}/{total_goals}")
        print(f"  Achievement Rate: {achievement_rate:.1f}%")
        print(f"  Target: >85% - {'✅ MET' if achievement_rate >= 85 else '❌ NOT MET'}")
        
        # Overall Assessment
        print("\n🏆 OVERALL ASSESSMENT:")
        total_tests = (
            len(self.test_results["conversation_naturalness"]) +
            len(self.test_results["recommendation_relevance"]) +
            len(self.test_results["question_flow_logic"]) +
            len(self.test_results["goal_achievement"])
        )
        
        total_passed = (
            passed_naturalness + passed_relevance + passed_logic +
            sum(1 for r in self.test_results["goal_achievement"] if r["passed"])
        )
        
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"  Overall Pass Rate: {overall_pass_rate:.1f}%")
        print(f"  Tests Passed: {total_passed}/{total_tests}")
        
        if overall_pass_rate >= 80:
            print("  🎉 USER EXPERIENCE TESTS: PASSED")
        else:
            print("  ⚠️  USER EXPERIENCE TESTS: NEEDS IMPROVEMENT")
        
        # Save detailed results
        with open("user_experience_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: user_experience_test_results.json")

async def main():
    """Run user experience tests"""
    test_suite = UserExperienceTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
