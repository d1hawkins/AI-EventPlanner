#!/usr/bin/env python3
"""
Performance Optimization Testing for Conversational Agent
Tests and optimizes question generation speed, recommendation response time, memory usage, and state management
"""

import asyncio
import time
import psutil
import json
import gc
import tracemalloc
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from app.graphs.coordinator_graph import create_coordinator_graph
from app.utils.question_manager import QuestionManager
from app.utils.recommendation_engine import RecommendationEngine
from app.utils.conversation_paths import ConversationPaths
from app.utils.proactive_suggestions import ProactiveSuggestions

class PerformanceOptimizationSuite:
    """Comprehensive performance testing and optimization suite"""
    
    def __init__(self):
        self.graph = create_coordinator_graph()
        self.question_manager = QuestionManager()
        self.recommendation_engine = RecommendationEngine()
        self.conversation_paths = ConversationPaths()
        self.proactive_suggestions = ProactiveSuggestions()
        self.performance_results = {
            "question_generation_speed": [],
            "recommendation_response_time": [],
            "memory_usage": [],
            "state_management": [],
            "concurrent_performance": [],
            "optimization_recommendations": []
        }
        self.baseline_metrics = {}
    
    async def run_all_tests(self):
        """Run all performance tests and optimizations"""
        print("🚀 Starting Performance Optimization Suite...")
        print("=" * 60)
        
        # Establish baseline metrics
        await self.establish_baseline_metrics()
        
        # Test 1: Question Generation Speed
        await self.test_question_generation_speed()
        
        # Test 2: Recommendation Response Time
        await self.test_recommendation_response_time()
        
        # Test 3: Memory Usage Analysis
        await self.test_memory_usage()
        
        # Test 4: State Management Performance
        await self.test_state_management_performance()
        
        # Test 5: Concurrent Performance
        await self.test_concurrent_performance()
        
        # Generate optimization recommendations
        self.generate_optimization_recommendations()
        
        # Generate final report
        self.generate_performance_report()
    
    async def establish_baseline_metrics(self):
        """Establish baseline performance metrics"""
        print("\n📊 Establishing Baseline Metrics...")
        
        # Memory baseline
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # CPU baseline
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Question generation baseline
        start_time = time.time()
        state = self.create_test_state()
        question = self.question_manager.get_next_question(state, {})
        question_time = time.time() - start_time
        
        # Recommendation baseline
        start_time = time.time()
        recommendations = self.recommendation_engine.get_recommendations(
            {"event_type": "conference", "attendee_count": 100},
            ["networking"],
            {"stage": "planning"}
        )
        recommendation_time = time.time() - start_time
        
        self.baseline_metrics = {
            "memory_mb": memory_info.rss / 1024 / 1024,
            "cpu_percent": cpu_percent,
            "question_generation_ms": question_time * 1000,
            "recommendation_generation_ms": recommendation_time * 1000
        }
        
        print(f"  Memory Usage: {self.baseline_metrics['memory_mb']:.1f} MB")
        print(f"  CPU Usage: {self.baseline_metrics['cpu_percent']:.1f}%")
        print(f"  Question Generation: {self.baseline_metrics['question_generation_ms']:.1f} ms")
        print(f"  Recommendation Generation: {self.baseline_metrics['recommendation_generation_ms']:.1f} ms")
    
    async def test_question_generation_speed(self):
        """Test question generation speed optimization"""
        print("\n⚡ Testing Question Generation Speed...")
        
        test_scenarios = [
            {"name": "Simple State", "complexity": "low"},
            {"name": "Medium State", "complexity": "medium"},
            {"name": "Complex State", "complexity": "high"},
            {"name": "Very Complex State", "complexity": "very_high"}
        ]
        
        for scenario in test_scenarios:
            print(f"  Testing: {scenario['name']}")
            
            # Create test state based on complexity
            state = self.create_test_state(complexity=scenario["complexity"])
            
            # Measure question generation time
            times = []
            for i in range(50):  # 50 iterations for statistical significance
                start_time = time.perf_counter()
                question = self.question_manager.get_next_question(state, {})
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
            # Calculate statistics
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            # Performance assessment
            target_time = 3000  # 3 seconds target
            passed = avg_time <= target_time
            
            result = {
                "scenario": scenario["name"],
                "complexity": scenario["complexity"],
                "avg_time_ms": avg_time,
                "min_time_ms": min_time,
                "max_time_ms": max_time,
                "target_ms": target_time,
                "passed": passed,
                "improvement_vs_baseline": ((self.baseline_metrics["question_generation_ms"] - avg_time) / self.baseline_metrics["question_generation_ms"]) * 100
            }
            
            self.performance_results["question_generation_speed"].append(result)
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"    {status} - Avg: {avg_time:.1f}ms (Target: <{target_time}ms)")
    
    async def test_recommendation_response_time(self):
        """Test recommendation engine response time"""
        print("\n🎯 Testing Recommendation Response Time...")
        
        test_cases = [
            {
                "name": "Basic Conference",
                "event_details": {"event_type": "conference", "attendee_count": 100},
                "goals": ["networking"],
                "context": {"stage": "planning"}
            },
            {
                "name": "Complex Corporate Event",
                "event_details": {"event_type": "corporate_event", "attendee_count": 500, "budget": 100000},
                "goals": ["networking", "brand_awareness", "lead_generation"],
                "context": {"stage": "planning", "industry": "technology"}
            },
            {
                "name": "Multi-day Conference",
                "event_details": {"event_type": "conference", "attendee_count": 1000, "duration": 3},
                "goals": ["knowledge_sharing", "networking", "thought_leadership"],
                "context": {"stage": "detailed_planning", "international": True}
            }
        ]
        
        for case in test_cases:
            print(f"  Testing: {case['name']}")
            
            # Measure recommendation generation time
            times = []
            for i in range(30):  # 30 iterations
                start_time = time.perf_counter()
                recommendations = self.recommendation_engine.get_recommendations(
                    case["event_details"],
                    case["goals"],
                    case["context"]
                )
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)
            
            # Calculate statistics
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            # Performance assessment
            target_time = 3000  # 3 seconds target
            passed = avg_time <= target_time
            
            result = {
                "case": case["name"],
                "avg_time_ms": avg_time,
                "min_time_ms": min_time,
                "max_time_ms": max_time,
                "target_ms": target_time,
                "passed": passed,
                "recommendations_count": len(recommendations) if recommendations else 0
            }
            
            self.performance_results["recommendation_response_time"].append(result)
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"    {status} - Avg: {avg_time:.1f}ms (Target: <{target_time}ms)")
    
    async def test_memory_usage(self):
        """Test memory usage and optimization"""
        print("\n💾 Testing Memory Usage...")
        
        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        
        # Test scenarios with increasing memory load
        test_scenarios = [
            {"name": "Single Conversation", "conversations": 1},
            {"name": "Multiple Conversations", "conversations": 10},
            {"name": "Heavy Load", "conversations": 50},
            {"name": "Stress Test", "conversations": 100}
        ]
        
        for scenario in test_scenarios:
            print(f"  Testing: {scenario['name']}")
            
            # Measure initial memory
            initial_memory = process.memory_info().rss / 1024 / 1024
            
            # Create multiple conversation states
            states = []
            for i in range(scenario["conversations"]):
                state = self.create_test_state(complexity="medium")
                
                # Simulate conversation progression
                for j in range(10):  # 10 questions per conversation
                    question = self.question_manager.get_next_question(state, {})
                    if question:
                        mock_answer = f"Answer {j} for conversation {i}"
                        self.question_manager.process_answer(state, mock_answer, question)
                
                states.append(state)
            
            # Measure peak memory
            peak_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = peak_memory - initial_memory
            
            # Get memory snapshot
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            # Clean up
            del states
            gc.collect()
            
            # Measure memory after cleanup
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_recovered = peak_memory - final_memory
            
            # Performance assessment
            memory_per_conversation = memory_increase / scenario["conversations"] if scenario["conversations"] > 0 else 0
            target_memory_per_conversation = 5.0  # 5MB per conversation target
            passed = memory_per_conversation <= target_memory_per_conversation
            
            result = {
                "scenario": scenario["name"],
                "conversations": scenario["conversations"],
                "initial_memory_mb": initial_memory,
                "peak_memory_mb": peak_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "memory_recovered_mb": memory_recovered,
                "memory_per_conversation_mb": memory_per_conversation,
                "target_mb": target_memory_per_conversation,
                "passed": passed,
                "top_memory_consumers": [(stat.traceback.format()[-1], stat.size / 1024 / 1024) for stat in top_stats[:3]]
            }
            
            self.performance_results["memory_usage"].append(result)
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"    {status} - {memory_per_conversation:.1f}MB per conversation (Target: <{target_memory_per_conversation}MB)")
        
        tracemalloc.stop()
    
    async def test_state_management_performance(self):
        """Test state management performance"""
        print("\n🔄 Testing State Management Performance...")
        
        # Test state operations
        operations = [
            {"name": "State Creation", "operation": "create"},
            {"name": "State Update", "operation": "update"},
            {"name": "State Query", "operation": "query"},
            {"name": "State Serialization", "operation": "serialize"}
        ]
        
        for operation in operations:
            print(f"  Testing: {operation['name']}")
            
            times = []
            
            if operation["operation"] == "create":
                # Test state creation
                for i in range(100):
                    start_time = time.perf_counter()
                    state = self.create_test_state(complexity="medium")
                    end_time = time.perf_counter()
                    times.append((end_time - start_time) * 1000)
            
            elif operation["operation"] == "update":
                # Test state updates
                state = self.create_test_state(complexity="medium")
                for i in range(100):
                    start_time = time.perf_counter()
                    state["event_details"][f"field_{i}"] = f"value_{i}"
                    state["question_history"].append({"id": i, "question": f"Question {i}"})
                    end_time = time.perf_counter()
                    times.append((end_time - start_time) * 1000)
            
            elif operation["operation"] == "query":
                # Test state queries
                state = self.create_test_state(complexity="high")
                for i in range(100):
                    start_time = time.perf_counter()
                    # Simulate common queries
                    completeness = len(state.get("event_details", {})) / 10
                    history_count = len(state.get("question_history", []))
                    current_stage = state.get("conversation_stage", "unknown")
                    end_time = time.perf_counter()
                    times.append((end_time - start_time) * 1000)
            
            elif operation["operation"] == "serialize":
                # Test state serialization
                state = self.create_test_state(complexity="high")
                for i in range(100):
                    start_time = time.perf_counter()
                    serialized = json.dumps(state, default=str)
                    deserialized = json.loads(serialized)
                    end_time = time.perf_counter()
                    times.append((end_time - start_time) * 1000)
            
            # Calculate statistics
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            # Performance assessment
            target_time = 10.0  # 10ms target for state operations
            passed = avg_time <= target_time
            
            result = {
                "operation": operation["name"],
                "avg_time_ms": avg_time,
                "min_time_ms": min_time,
                "max_time_ms": max_time,
                "target_ms": target_time,
                "passed": passed
            }
            
            self.performance_results["state_management"].append(result)
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"    {status} - Avg: {avg_time:.2f}ms (Target: <{target_time}ms)")
    
    async def test_concurrent_performance(self):
        """Test concurrent performance under load"""
        print("\n🔀 Testing Concurrent Performance...")
        
        concurrent_levels = [1, 5, 10, 20]
        
        for level in concurrent_levels:
            print(f"  Testing: {level} concurrent conversations")
            
            async def simulate_conversation(conversation_id: int) -> Dict[str, Any]:
                """Simulate a single conversation"""
                state = self.create_test_state()
                conversation_times = []
                
                for i in range(5):  # 5 questions per conversation
                    start_time = time.perf_counter()
                    
                    # Get question
                    question = self.question_manager.get_next_question(state, {})
                    
                    # Get recommendations
                    if question:
                        recommendations = self.recommendation_engine.get_recommendations(
                            state.get("event_details", {}),
                            state.get("user_goals", []),
                            {"stage": "planning"}
                        )
                        
                        # Process answer
                        mock_answer = f"Answer {i} from conversation {conversation_id}"
                        self.question_manager.process_answer(state, mock_answer, question)
                    
                    end_time = time.perf_counter()
                    conversation_times.append((end_time - start_time) * 1000)
                
                return {
                    "conversation_id": conversation_id,
                    "avg_time_ms": sum(conversation_times) / len(conversation_times),
                    "total_time_ms": sum(conversation_times)
                }
            
            # Run concurrent conversations
            start_time = time.perf_counter()
            
            tasks = [simulate_conversation(i) for i in range(level)]
            results = await asyncio.gather(*tasks)
            
            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            
            # Calculate statistics
            avg_conversation_time = sum(r["avg_time_ms"] for r in results) / len(results)
            total_conversation_time = sum(r["total_time_ms"] for r in results)
            
            # Performance assessment
            target_time_per_conversation = 15000  # 15 seconds per conversation
            passed = avg_conversation_time <= target_time_per_conversation
            
            result = {
                "concurrent_level": level,
                "total_time_ms": total_time,
                "avg_conversation_time_ms": avg_conversation_time,
                "total_conversation_time_ms": total_conversation_time,
                "throughput_conversations_per_second": level / (total_time / 1000),
                "target_ms": target_time_per_conversation,
                "passed": passed
            }
            
            self.performance_results["concurrent_performance"].append(result)
            
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"    {status} - Avg: {avg_conversation_time:.1f}ms per conversation")
            print(f"    Throughput: {result['throughput_conversations_per_second']:.2f} conversations/sec")
    
    def generate_optimization_recommendations(self):
        """Generate optimization recommendations based on test results"""
        print("\n🔧 Generating Optimization Recommendations...")
        
        recommendations = []
        
        # Question generation optimization
        question_times = [r["avg_time_ms"] for r in self.performance_results["question_generation_speed"]]
        if question_times and max(question_times) > 2000:  # > 2 seconds
            recommendations.append({
                "category": "Question Generation",
                "priority": "High",
                "issue": "Slow question generation for complex states",
                "recommendation": "Implement question caching and pre-computation for common scenarios",
                "implementation": "Add LRU cache to QuestionManager.get_next_question() method"
            })
        
        # Recommendation engine optimization
        rec_times = [r["avg_time_ms"] for r in self.performance_results["recommendation_response_time"]]
        if rec_times and max(rec_times) > 2000:  # > 2 seconds
            recommendations.append({
                "category": "Recommendation Engine",
                "priority": "High",
                "issue": "Slow recommendation generation",
                "recommendation": "Pre-compute common recommendations and use async processing",
                "implementation": "Add recommendation cache and background processing"
            })
        
        # Memory optimization
        memory_results = self.performance_results["memory_usage"]
        high_memory_usage = any(r["memory_per_conversation_mb"] > 3.0 for r in memory_results)
        if high_memory_usage:
            recommendations.append({
                "category": "Memory Usage",
                "priority": "Medium",
                "issue": "High memory usage per conversation",
                "recommendation": "Implement conversation state compression and cleanup",
                "implementation": "Add state pruning and use weak references for cached data"
            })
        
        # State management optimization
        state_times = [r["avg_time_ms"] for r in self.performance_results["state_management"]]
        if state_times and max(state_times) > 5.0:  # > 5ms
            recommendations.append({
                "category": "State Management",
                "priority": "Medium",
                "issue": "Slow state operations",
                "recommendation": "Optimize state data structures and serialization",
                "implementation": "Use more efficient data structures and lazy loading"
            })
        
        # Concurrent performance optimization
        concurrent_results = self.performance_results["concurrent_performance"]
        low_throughput = any(r["throughput_conversations_per_second"] < 1.0 for r in concurrent_results)
        if low_throughput:
            recommendations.append({
                "category": "Concurrent Performance",
                "priority": "High",
                "issue": "Low concurrent throughput",
                "recommendation": "Implement connection pooling and async processing",
                "implementation": "Add async/await patterns and connection pooling"
            })
        
        self.performance_results["optimization_recommendations"] = recommendations
        
        for rec in recommendations:
            print(f"  🔧 {rec['category']} ({rec['priority']} Priority)")
            print(f"     Issue: {rec['issue']}")
            print(f"     Recommendation: {rec['recommendation']}")
    
    def create_test_state(self, complexity: str = "medium") -> Dict[str, Any]:
        """Create test state with varying complexity"""
        base_state = {
            "messages": [],
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
        
        if complexity == "low":
            base_state["event_details"] = {"event_type": "conference"}
            base_state["user_goals"] = ["networking"]
        
        elif complexity == "medium":
            base_state["event_details"] = {
                "event_type": "conference",
                "attendee_count": 100,
                "budget": 50000,
                "timeline": "3 months"
            }
            base_state["user_goals"] = ["networking", "knowledge_sharing"]
            base_state["question_history"] = [
                {"id": i, "category": f"category_{i}", "text": f"Question {i}"}
                for i in range(5)
            ]
        
        elif complexity == "high":
            base_state["event_details"] = {
                "event_type": "corporate_conference",
                "attendee_count": 500,
                "budget": 200000,
                "timeline": "6 months",
                "venue_requirements": ["AV equipment", "catering", "parking"],
                "stakeholders": ["executives", "employees", "clients"],
                "success_metrics": ["attendance", "satisfaction", "ROI"]
            }
            base_state["user_goals"] = ["networking", "knowledge_sharing", "brand_awareness", "lead_generation"]
            base_state["question_history"] = [
                {"id": i, "category": f"category_{i}", "text": f"Question {i}", "answer": f"Answer {i}"}
                for i in range(15)
            ]
            base_state["recommendations_given"] = [
                {"id": i, "category": f"rec_category_{i}", "text": f"Recommendation {i}"}
                for i in range(10)
            ]
        
        elif complexity == "very_high":
            base_state["event_details"] = {
                "event_type": "international_conference",
                "attendee_count": 2000,
                "budget": 1000000,
                "timeline": "12 months",
                "venue_requirements": ["multiple_rooms", "translation", "live_streaming"],
                "stakeholders": ["board", "executives", "employees", "clients", "media", "partners"],
                "success_metrics": ["attendance", "satisfaction", "ROI", "media_coverage", "lead_generation"],
                "compliance_requirements": ["accessibility", "data_privacy", "international_regulations"],
                "marketing_channels": ["social_media", "email", "PR", "advertising", "partnerships"],
                "logistics": ["accommodation", "transportation", "catering", "security", "registration"]
            }
            base_state["user_goals"] = [
                "networking", "knowledge_sharing", "brand_awareness", "lead_generation",
                "thought_leadership", "partnership_building", "market_expansion"
            ]
            base_state["question_history"] = [
                {"id": i, "category": f"category_{i}", "text": f"Question {i}", "answer": f"Answer {i}"}
                for i in range(50)
            ]
            base_state["recommendations_given"] = [
                {"id": i, "category": f"rec_category_{i}", "text": f"Recommendation {i}"}
                for i in range(25)
            ]
        
        return base_state
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE OPTIMIZATION REPORT")
        print("=" * 60)
        
        # Question Generation Speed Results
        print("\n⚡ Question Generation Speed:")
        question_results = self.performance_results["question_generation_speed"]
        if question_results:
            avg_times = [r["avg_time_ms"] for r in question_results]
            overall_avg = sum(avg_times) / len(avg_times)
            passed_count = sum(1 for r in question_results if r["passed"])
            
            print(f"  Overall Average: {overall_avg:.1f}ms")
            print(f"  Tests Passed: {passed_count}/{len(question_results)}")
            print(f"  Target: <3000ms - {'✅ MET' if overall_avg < 3000 else '❌ NOT MET'}")
        
        # Recommendation Response Time Results
        print("\n🎯 Recommendation Response Time:")
        rec_results = self.performance_results["recommendation_response_time"]
        if rec_results:
            avg_times = [r["avg_time_ms"] for r in rec_results]
            overall_avg = sum(avg_times) / len(avg_times)
            passed_count = sum(1 for r in rec_results if r["passed"])
            
            print(f"  Overall Average: {overall_avg:.1f}ms")
            print(f"  Tests Passed: {passed_count}/{len(rec_results)}")
            print(f"  Target: <3000ms - {'✅ MET' if overall_avg < 3000 else '❌ NOT MET'}")
        
        # Memory Usage Results
        print("\n💾 Memory Usage:")
        memory_results = self.performance_results["memory_usage"]
        if memory_results:
            memory_per_conv = [r["memory_per_conversation_mb"] for r in memory_results]
            max_memory = max(memory_per_conv) if memory_per_conv else 0
            passed_count = sum(1 for r in memory_results if r["passed"])
            
            print(f"  Max Memory per Conversation: {max_memory:.1f}MB")
            print(f"  Tests Passed: {passed_count}/{len(memory_results)}")
            print(f"  Target: <5.0MB - {'✅ MET' if max_memory < 5.0 else '❌ NOT MET'}")
        
        # State Management Results
        print("\n🔄 State Management:")
        state_results = self.performance_results["state_management"]
        if state_results:
            avg_times = [r["avg_time_ms"] for r in state_results]
            overall_avg = sum(avg_times) / len(avg_times)
            passed_count = sum(1 for r in state_results if r["passed"])
            
            print(f"  Overall Average: {overall_avg:.2f}ms")
            print(f"  Tests Passed: {passed_count}/{len(state_results)}")
            print(f"  Target: <10ms - {'✅ MET' if overall_avg < 10 else '❌ NOT MET'}")
        
        # Concurrent Performance Results
        print("\n🔀 Concurrent Performance:")
        concurrent_results = self.performance_results["concurrent_performance"]
        if concurrent_results:
            throughputs = [r["throughput_conversations_per_second"] for r in concurrent_results]
            max_throughput = max(throughputs) if throughputs else 0
            passed_count = sum(1 for r in concurrent_results if r["passed"])
            
            print(f"  Max Throughput: {max_throughput:.2f} conversations/sec")
            print(f"  Tests Passed: {passed_count}/{len(concurrent_results)}")
            print(f"  Target: >1.0 conv/sec - {'✅ MET' if max_throughput > 1.0 else '❌ NOT MET'}")
        
        # Optimization Recommendations
        print("\n🔧 Optimization Recommendations:")
        recommendations = self.performance_results["optimization_recommendations"]
        if recommendations:
            high_priority = [r for r in recommendations if r["priority"] == "High"]
            medium_priority = [r for r in recommendations if r["priority"] == "Medium"]
            
            print(f"  High Priority: {len(high_priority)} recommendations")
            print(f"  Medium Priority: {len(medium_priority)} recommendations")
            
            for rec in high_priority:
                print(f"    🔴 {rec['category']}: {rec['recommendation']}")
            
            for rec in medium_priority:
                print(f"    🟡 {rec['category']}: {rec['recommendation']}")
        else:
            print("  🎉 No optimization recommendations - Performance is optimal!")
        
        # Overall Assessment
        print("\n🏆 OVERALL PERFORMANCE ASSESSMENT:")
        
        # Calculate overall performance score
        all_results = (
            self.performance_results["question_generation_speed"] +
            self.performance_results["recommendation_response_time"] +
            self.performance_results["memory_usage"] +
            self.performance_results["state_management"] +
            self.performance_results["concurrent_performance"]
        )
        
        total_tests = len(all_results)
        total_passed = sum(1 for r in all_results if r.get("passed", False))
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"  Overall Pass Rate: {overall_pass_rate:.1f}%")
        print(f"  Tests Passed: {total_passed}/{total_tests}")
        
        if overall_pass_rate >= 80:
            print("  🎉 PERFORMANCE TESTS: PASSED")
        else:
            print("  ⚠️  PERFORMANCE TESTS: NEEDS OPTIMIZATION")
        
        # Performance vs Baseline
        print("\n📈 Performance vs Baseline:")
        if self.baseline_metrics:
            current_question_avg = sum(r["avg_time_ms"] for r in self.performance_results["question_generation_speed"]) / len(self.performance_results["question_generation_speed"]) if self.performance_results["question_generation_speed"] else 0
            current_rec_avg = sum(r["avg_time_ms"] for r in self.performance_results["recommendation_response_time"]) / len(self.performance_results["recommendation_response_time"]) if self.performance_results["recommendation_response_time"] else 0
            
            question_improvement = ((self.baseline_metrics["question_generation_ms"] - current_question_avg) / self.baseline_metrics["question_generation_ms"]) * 100 if current_question_avg > 0 else 0
            rec_improvement = ((self.baseline_metrics["recommendation_generation_ms"] - current_rec_avg) / self.baseline_metrics["recommendation_generation_ms"]) * 100 if current_rec_avg > 0 else 0
            
            print(f"  Question Generation: {question_improvement:+.1f}% vs baseline")
            print(f"  Recommendation Generation: {rec_improvement:+.1f}% vs baseline")
        
        # Save detailed results
        with open("performance_optimization_results.json", "w") as f:
            json.dump({
                "baseline_metrics": self.baseline_metrics,
                "performance_results": self.performance_results,
                "timestamp": time.time()
            }, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: performance_optimization_results.json")

async def main():
    """Run performance optimization tests"""
    test_suite = PerformanceOptimizationSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
