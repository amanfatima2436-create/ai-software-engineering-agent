from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from llm import LLM
from sandbox_runner import run_code

class AgentState(TypedDict):
    task: str
    plan: str
    code: str
    test_cases: list[str]
    test_result: str
    review: str
    attempts: int


def planner(state: AgentState):
    task = state["task"]

    return {
        "plan": f"""
1. Understand the task: {task}
2. Decide what needs to be implemented
3. Write the required code
4. Test the implementation
""",
        "test_cases": [
            "For a calculator, add(5, 3) should return 8.",
            "For a calculator, add(10, 20) should return 30.",
            "For a calculator, add(-5, 2) should return -3."
        ]
    }


def coder(state: AgentState):
    task = state["task"]
    plan = state["plan"]
    review = state["review"]
    attempts = state["attempts"]

    llm = LLM()

    prompt = f"""
You are a software engineer.

User task:
{task}

Create code based on this plan:

{plan}

Previous reviewer feedback:
{review}

Generate the required code.
"""

    code = llm.generate(prompt)

    return {
        "code": code,
        "attempts": attempts + 1
    }

def tester(state: AgentState):
    code = state["code"]
    test_cases = state["test_cases"]

    result = run_code(code)

    if result["return_code"] != 0:
        return {
            "test_result": (
                "FAIL: Code execution failed.\n"
                f"Error:\n{result['error']}"
            )
        }

    output = result["output"].strip()

    if "calculator" in state["task"].lower():
        expected_outputs = ["8", "30", "-3"]

        for expected in expected_outputs:
            if expected not in output:
                return {
                    "test_result": (
                        "FAIL: Calculator test case failed.\n"
                        f"Expected result: {expected}\n"
                        f"Actual output:\n{output}"
                    )
                }

        return {
            "test_result": (
                "PASS: Calculator code executed and "
                "all expected results were found.\n"
                f"Output:\n{output}"
            )
        }

    return {
        "test_result": (
            "PASS: Code executed successfully.\n"
            f"Output:\n{output}"
        )
    }
def reviewer(state: AgentState):
    test_result = state["test_result"]

    if test_result.startswith("PASS"):
        review = "APPROVED: The code passed the task-specific tests."
    else:
        review = "REJECTED: The code failed the task-specific tests."

    return {
        "review": review
    }
def review_router(state: AgentState):
    review = state["review"]
    attempts = state["attempts"]

    if "APPROVED" in review:
        return "end"

    if attempts < 3:
        return "coder"

    return "end"
graph = StateGraph(AgentState)

graph.add_node("planner", planner)
graph.add_node("coder", coder)
graph.add_node("tester", tester)
graph.add_node("reviewer", reviewer)

graph.add_edge(START, "planner")
graph.add_edge("planner", "coder")
graph.add_edge("coder", "tester")
graph.add_edge("tester", "reviewer")
graph.add_conditional_edges(
    "reviewer",
    review_router,
    {
        "end": END,
        "coder": "coder"
    }
)

agent = graph.compile()


result = agent.invoke({
    "task": "Build a Python calculator",
    "plan": "",
    "code": "",
    "test_cases": [],
    "test_result": "",
    "review": "",
    "attempts": 0
})

print("PLAN:")
print(result["plan"])

print("\nCODE:")
print(result["code"])
print("\nTEST RESULT:")
print(result["test_result"])
print("\nREVIEW:")
print(result["review"])
print("\nATTEMPTS:")
print(result["attempts"])
