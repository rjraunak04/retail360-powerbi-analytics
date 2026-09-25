"""Small recruiter-friendly demonstration of the governed Retail360 agent."""

from agent import build_default_agent


QUESTIONS = (
    "What is gross margin?",
    "Explain current inventory",
    "Explain the semantic model schema",
)


def main() -> None:
    agent = build_default_agent()
    for question in QUESTIONS:
        response = agent.answer(question)
        print(f"Q: {question}")
        print(f"Intent: {response.intent}")
        print(f"A: {response.answer}")
        print("-" * 72)


if __name__ == "__main__":
    main()
