"""
Agent Evaluation Script
=======================
Step 1: Tests that the planner agent routes queries to the correct agent type.
        This validates the autonomous decision-making logic of the agentic system.

Run from the backend/ directory:
    python -m tests.test_planner
"""

import sys
import os

# Step 2: Add the backend directory to the Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.planner import decide_agent


# Step 3: Define test cases — each is a (query, expected_agent) pair
# Covers all 4 agent types: llm, web_search, rag, tool
TEST_CASES = [
    # --- LLM (default) queries ---
    ("hello", "llm"),
    ("What is machine learning?", "llm"),
    ("Tell me a joke", "llm"),
    ("How does gravity work?", "llm"),

    # --- Web Search queries ---
    ("search latest AI trends", "web_search"),
    ("What is the latest news about Python?", "web_search"),
    ("Find online resources for React", "web_search"),
    ("What is currently trending in tech?", "web_search"),

    # --- Calculator / Tool queries ---
    ("calculate 25 * 4 + 10", "tool"),
    ("calculate the square root of 144", "tool"),

    # --- RAG queries (these depend on FAISS index existing) ---
    ("What does the pdf say about chapter 1?", "rag"),
    ("Summarize the document", "rag"),
    ("Explain the notes on page 5", "rag"),
    ("What is in the uploaded file?", "rag"),
]


def run_evaluation():
    """
    Step 4: Run all test cases and report pass/fail for each.
    Returns the number of passed and failed tests.
    """
    passed = 0
    failed = 0
    total = len(TEST_CASES)

    print("=" * 65)
    print("  AGENT ROUTING EVALUATION")
    print("=" * 65)
    print()

    for i, (query, expected) in enumerate(TEST_CASES, 1):
        # Step 5: Get the planner's decision for this query
        actual = decide_agent(query)

        # Step 6: Compare actual vs expected
        status = "PASS" if actual == expected else "FAIL"
        icon = "[PASS]" if status == "PASS" else "[FAIL]"

        if status == "PASS":
            passed += 1
        else:
            failed += 1

        # Step 7: Print the result for this test case
        print(f"  {icon} Test {i:2d}/{total} | {status} | Expected: {expected:<12} | Got: {actual:<12} | \"{query}\"")

    # Step 8: Print the summary
    print()
    print("-" * 65)
    print(f"  Results: {passed}/{total} passed, {failed}/{total} failed")
    accuracy = (passed / total) * 100 if total > 0 else 0
    print(f"  Accuracy: {accuracy:.1f}%")
    print("-" * 65)

    if failed == 0:
        print("  ALL TESTS PASSED!")
    else:
        print(f"  WARNING: {failed} test(s) failed -- check routing keywords.")
    print()

    return passed, failed


if __name__ == "__main__":
    # Step 9: Run the evaluation when this script is executed directly
    passed, failed = run_evaluation()
    # Step 10: Exit with code 1 if any test failed (useful for CI/CD)
    sys.exit(1 if failed > 0 else 0)
