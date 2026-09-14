class LLM:
    def generate(self, prompt: str) -> str:
        if "REJECTED" in prompt:
            return 'print("Corrected solution generated after review")'

        if "calculator" in prompt.lower():
            return """
def add(a, b):
    return a + b

print(add(5, 3))
"""

        if "prime" in prompt.lower():
            return """
def is_prime(number):
    if number < 2:
        return False

    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False

    return True

print(is_prime(7))
"""

        return 'print("Hello from the AI Software Engineering Agent")'