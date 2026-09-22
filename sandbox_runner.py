import subprocess
import tempfile
import os


def run_code(code: str, test_code: str = ""):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:

            code_file = os.path.join(temp_dir, "main.py")
            test_file = os.path.join(temp_dir, "test.py")

            with open(code_file, "w") as file:
                file.write(code)
            with open(test_file, "w") as file:
                file.write(test_code)

            result = subprocess.run(
                [
                    "docker", "run",
                    "--rm",
                    "--network", "none",
                    "--cpus", "0.5",
                    "--memory", "256m",
                    "-v", f"{temp_dir}:/app:ro",
                    "python:3.12-slim",
                    "python", "/app/test.py"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            return {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Execution timed out after 5 seconds.",
            "return_code": -1
        }