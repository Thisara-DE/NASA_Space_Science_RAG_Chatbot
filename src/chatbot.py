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
MODEL  = "llama-3.3-70b-versatile"

# ── Prompt template (as specified) ────────────────────────────────────────────
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an intelligent document assistant. Your only knowledge comes from the provided document excerpts below.
Answer the user's question based **only** on the information contained in the following context.
If the answer is not clearly contained in the context, say:
"I don't have enough information in the document to answer this question accurately."

Context:
{context}

Question: {question}

Answer in a clear, concise and helpful way. Be direct — avoid unnecessary introductions like "According to the document" unless it adds clarity.
"""
)

# ── Max chat history turns to keep in memory ──────────────────────────────────
MAX_HISTORY_TURNS = 6


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

    def ask(self, question: str) -> dict:
        """
        Main method — takes a question, retrieves context, generates answer.

        Returns a dict with:
            - answer       : str  — the LLM's response
            - source       : str  — "qa" or "document"
            - matched_qa   : dict or None
            - doc_sources  : list of source URLs
            - confidence   : float
        """
        # ── Retrieve relevant context ──────────────────────────────────────────
        retrieval = retrieve(question, self.doc_col, self.qa_col)
        context   = retrieval["context"]

        # ── Build messages and call Groq ───────────────────────────────────────
        messages = self._build_messages(context, question)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,    # low temperature = more factual answers
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