"""
ai_brain.py — Groq AI Logic
Generates flashcards from any topic or notes
"""

import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import GROQ_API_KEY

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0.7
)

SYSTEM_PROMPT = """
You are a flashcard generator AI.
When given a topic or notes, generate exactly 10 flashcards.

Respond ONLY with a valid JSON array like this:
[
  {
    "id": 1,
    "question": "What is Python?",
    "answer": "Python is a high-level programming language known for its simplicity and readability.",
    "hint": "Think about its creator and main use cases"
  },
  ...
]

Rules:
- Generate exactly 10 flashcards
- Questions should be clear and specific
- Answers should be concise (1-3 sentences)
- Hints should guide thinking without giving answer
- Cover different aspects of the topic
- No markdown, no extra text, ONLY the JSON array
"""

def generate_flashcards(topic: str) -> list:
    """Generate 10 flashcards from a topic or notes"""
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Generate flashcards for this topic/notes:\n\n{topic}")
        ]
        response = llm.invoke(messages)
        text = response.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        cards = json.loads(text)
        return cards
    except Exception as e:
        print(f"AI Error: {e}")
        return []


CHECK_PROMPT = """
You are a strict but fair answer checker for flashcards.

Compare the student's answer with the correct answer.
Focus on MEANING and KEY CONCEPTS, not exact wording.
Accept partial answers if the core concept is correct.
Be lenient with spelling mistakes.

Respond ONLY with this JSON:
{
  "correct": true or false,
  "score": 0-100,
  "feedback": "short encouraging feedback in 1 sentence",
  "missing": "what key concept was missing (if wrong), empty string if correct"
}

Rules:
- correct=true if student got the main idea (score >= 60)
- correct=false if student missed the main concept
- feedback should be encouraging even when wrong
- No markdown, ONLY JSON
"""

def check_answer_with_ai(question: str, correct_answer: str, user_answer: str) -> dict:
    """Use Groq AI to intelligently check if answer is correct"""
    try:
        prompt = f"""
Question: {question}
Correct Answer: {correct_answer}
Student Answer: {user_answer}

Is the student's answer correct?
"""
        messages = [
            SystemMessage(content=CHECK_PROMPT),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        text = response.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return result
    except Exception as e:
        print(f"AI Check Error: {e}")
        # Fallback to simple check
        correct = user_answer.lower() in correct_answer.lower() or correct_answer.lower() in user_answer.lower()
        return {
            "correct": correct,
            "score": 70 if correct else 30,
            "feedback": "Good try! Review the correct answer below." ,
            "missing": "" if correct else "Check the correct answer"
        }
