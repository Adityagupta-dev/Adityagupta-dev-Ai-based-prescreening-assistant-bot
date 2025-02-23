# src/chatbot.py
from rag_pipeline import get_question, evaluate_answer

class PrescreeningBot:
    def __init__(self):
        self.complexity = 1  # Start with the lowest complexity

    def get_next_question(self):
        question, metadata = get_question(self.complexity)
        return question, metadata

    def evaluate_response(self, question, answer):
        evaluation = evaluate_answer(question, answer)
        if "correct" in evaluation.lower():
            self.complexity += 1
        elif "incorrect" in evaluation.lower():
            self.complexity = max(1, self.complexity - 1)
        return evaluation

# Example usage
if __name__ == "__main__":
    bot = PrescreeningBot()
    question, metadata = bot.get_next_question()
    print(f"Question: {question}")
    answer = input("Your answer: ")
    evaluation = bot.evaluate_response(question, answer)
    print(f"Evaluation: {evaluation}")