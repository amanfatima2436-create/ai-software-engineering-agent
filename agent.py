from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from llm import LLM
from sandbox_runner import run_code

class AgentState(TypedDict):
    task: str
    plan: str
    code: str
    test_cases: list[dict]
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
            {
                "function": "add",
                "inputs": [5, 3],
                "expected": 8
            },
            {
                "function": "add",
                "inputs": [10, 20],
                "expected": 30
            },
            {
                "function": "add",
                "inputs": [-5, 2],
                "expected": -3
            }
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

    functions = {test_case["function"] for test_case in test_cases}
    imports = ", ".join(sorted(functions))

    test_code = f"from main import {imports}\n\n"

    for test_case in test_cases:
        function = test_case["function"]
        inputs = ", ".join(str(value) for value in test_case["inputs"])
        expected = repr(test_case["expected"])

        test_code += f"assert {function}({inputs}) == {expected}\n"

    test_code += '\nprint("All tests passed")'

    result = run_code(code, test_code)

    if result["return_code"] != 0:
        return {
            "test_result": (
                "FAIL: Test cases failed.\n"
                f"Error:\n{result['error']}"
            )
        }

    output = result["output"].strip()

    return {
        "test_result": (
            "PASS: All generated test cases passed.\n"
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
