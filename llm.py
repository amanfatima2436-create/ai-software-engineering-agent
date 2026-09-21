class LLM:
    def generate(self, prompt: str) -> str:

        # Calculator task
        if "calculator" in prompt.lower():

            # First attempt: intentionally wrong
            if "REJECTED" not in prompt:
                return """
def add(a, b):
    return a - b

print(add(5, 3))
print(add(10, 20))
print(add(-5, 2))
"""

            # Second attempt: corrected after review
            return """
def add(a, b):
    return a + b

print(add(5, 3))
print(add(10, 20))
print(add(-5, 2))
"""

        # Prime number task
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

        # Hello task
        if "hello" in prompt.lower():
            return 'print("Hello from the AI Software Engineering Agent")'

        # Generic correction
        if "REJECTED" in prompt:
            return 'print("Corrected solution generated after review")'

        return 'print("Hello from the AI Software Engineering Agent")'