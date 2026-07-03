import os
from groq import Groq
from groq.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from retriever import get_retriever, retrieve

# ── Load environment variables ─────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── Groq client ────────────────────────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "openai/gpt-oss-120b"   # replaces llama-3.3-70b-versatile (Groq decommission 2026-08-16)

# ── Prompt template (as specified) ────────────────────────────────────────────
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a warm, curious NASA space science guide who loves helping people understand the cosmos.
Everything you know comes from the document excerpts provided below — treat these as your only source of facts.

Ground every claim in the context. If the context doesn't contain the answer, be honest and gently say so, for example:
"That's a great question, but I don't have enough in my current sources to answer it accurately — I don't want to guess."

Context:
{context}

Question: {question}

Now answer in a natural, conversational, and genuinely engaging way:
- Write like a knowledgeable person explaining something they find fascinating, not like a search result.
- Open with a direct answer, then add helpful color, context, or a vivid detail that brings it to life — as long as it's supported by the context.
- Use plain, welcoming language; feel free to show a little enthusiasm for the science.
- Keep it accurate above all: never add facts, figures, or names that aren't in the context.
- Aim for a few well-formed sentences rather than a terse one-liner, but don't pad — every sentence should earn its place.
"""
)

# ── Max chat history turns to keep in memory ──────────────────────────────────
MAX_HISTORY_TURNS = 6

# ── Guardrail: the only topics this bot is allowed to answer ───────────────────
# The bot answers only when (a) the question strongly matches a stored Q&A pair,
# or (b) the question is about astronomy / astrophysics / space science.
# Everything else is politely declined.
TOPIC_GATE_PROMPT = """You are a strict topic classifier for a NASA space science assistant.
Decide whether the user's latest question is about astronomy, astrophysics, or space science.
This INCLUDES: stars, planets, moons, comets, galaxies, black holes, cosmology, the universe,
space missions, spacecraft, telescopes, and NASA science in general.
This does NOT include: cooking, sports, politics, finance, personal advice, general coding,
horoscopes/astrology, or any other everyday topic.
Use the conversation so far to interpret short follow-up questions (e.g. "tell me more", "why?").
Respond with exactly one word: YES if it is on-topic, or NO if it is not."""

REJECTION_MESSAGE = (
    "I'd genuinely love to help, but I'm here as a space science guide — my world is astronomy "
    "and astrophysics: planets, stars, galaxies, black holes, and the missions exploring them. "
    "That one falls outside what I can speak to, so I'll gently pass on it. But ask me anything "
    "about the cosmos and I'm all yours!"
)


class NASAChatbot:
    def __init__(self):
        print("🚀 Initialising NASA Space Science Chatbot...")
        self.doc_col, self.qa_col = get_retriever()
        self.chat_history: list[ChatCompletionMessageParam] = []
        print("✅ Chatbot ready!\n")

    def _build_messages(self, context: str, question: str) -> list[ChatCompletionMessageParam]:
        """
        Build the full message list for Groq:
        - System message with the prompt template filled in
        - Recent chat history for memory
        - Current user question
        """
        filled_prompt = prompt.format(context=context, question=question)

        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": filled_prompt}]

        # Add recent chat history (last N turns only to stay within token limits)
        recent_history = self.chat_history[-(MAX_HISTORY_TURNS * 2):]
        messages.extend(recent_history)

        # Add the current question
        messages.append({"role": "user", "content": question})

        return messages

    def _is_on_topic(self, question: str) -> bool:
        """
        Guardrail classifier: is the question about astronomy / astrophysics /
        space science? Uses recent chat history so short follow-ups are understood.
        Fails open (returns True) if the classifier is unclear — the grounded
        answer prompt will still decline gracefully when no relevant context exists.
        """
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": TOPIC_GATE_PROMPT}]
        messages.extend(self.chat_history[-(MAX_HISTORY_TURNS * 2):])
        messages.append({"role": "user", "content": question})

        result = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            max_tokens=10,
        )
        verdict = (result.choices[0].message.content or "").strip().upper()

        if "NO" in verdict:
            return False
        if "YES" in verdict:
            return True
        return True   # unclear → lenient; grounded prompt is the safety net

    def ask(self, question: str) -> dict:
        """
        Main method — takes a question, retrieves context, generates answer.

        Returns a dict with:
            - answer       : str  — the LLM's response
            - source       : str  — "qa", "document", or "rejected"
            - matched_qa   : dict or None
            - doc_sources  : list of source URLs
            - confidence   : float
        """
        # ── Retrieve relevant context ──────────────────────────────────────────
        retrieval = retrieve(question, self.doc_col, self.qa_col)

        # ── Guardrail ──────────────────────────────────────────────────────────
        # Answer only if there's a strong Q&A match OR the question is on-topic
        # (astronomy / astrophysics / space science). Otherwise, politely decline.
        if retrieval["source"] != "qa" and not self._is_on_topic(question):
            self.chat_history.append({"role": "user",      "content": question})
            self.chat_history.append({"role": "assistant", "content": REJECTION_MESSAGE})
            return {
                "answer":      REJECTION_MESSAGE,
                "source":      "rejected",
                "matched_qa":  None,
                "doc_sources": [],
                "confidence":  retrieval["confidence"],
            }

        context = retrieval["context"]

        # ── Build messages and call Groq ───────────────────────────────────────
        messages = self._build_messages(context, question)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.5,    # a touch warmer/more natural, still grounded in context
            max_tokens=1024,
        )

        answer = (response.choices[0].message.content or "").strip()

        # ── Update chat history ────────────────────────────────────────────────
        self.chat_history.append({"role": "user",      "content": question})
        self.chat_history.append({"role": "assistant", "content": answer})

        return {
            "answer":      answer,
            "source":      retrieval["source"],
            "matched_qa":  retrieval["matched_qa"],
            "doc_sources": retrieval["doc_sources"],
            "confidence":  retrieval["confidence"],
        }

    def clear_history(self):
        """Reset the conversation memory."""
        self.chat_history = []
        print("🗑️  Chat history cleared.")


if __name__ == "__main__":
    # Interactive test in the terminal
    bot = NASAChatbot()
    print("NASA Space Science Chatbot — type 'quit' to exit, 'clear' to reset\n")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye! 🚀")
            break
        if user_input.lower() == "clear":
            bot.clear_history()
            continue

        result = bot.ask(user_input)

        print(f"\nBot: {result['answer']}")
        print(f"\n[Source: {result['source'].upper()} | "
            f"Confidence: {result['confidence']} | "
            f"Pages: {', '.join(result['doc_sources'][:2]) or 'N/A'}]")