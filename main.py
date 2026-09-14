from fastapi import FastAPI
from agent import agent

app = FastAPI(title="AI Software Engineering Agent")


@app.get("/")
def home():
    return {
        "message": "AI Software Engineering Agent is running!"
    }


@app.post("/run-agent")
def run_agent(task: str):
    result = agent.invoke({
        "task": task,
        "plan": "",
        "code": "",
        "test_result": "",
        "review": "",
        "attempts": 0
    })

    return result