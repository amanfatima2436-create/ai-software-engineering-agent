from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from llm import LLM

class AgentState(TypedDict):
    task: str
    plan: str
    code: str
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
"""
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

    if "print(" in code:
        result = "PASS: The generated code contains a print statement."
    else:
        result = "FAIL: No print statement found."

    return {
        "test_result": result
    }
def reviewer(state: AgentState):
    code = state["code"]
    test_result = state["test_result"]

    if "PASS" in test_result and "print(" in code:
        review = "APPROVED: The code passed the test and looks acceptable."
    else:
        review = "REJECTED: The code needs improvement."

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
    "task": "Build a Python program that says hello",
    "plan": "",
    "code": "",
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
